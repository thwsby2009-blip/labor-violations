#!/usr/bin/env python3
"""更新勞動部裁罰資料（唯一更新腳本）

手動執行：python spider.py（驗證通過才會寫入 data/labor_violations.csv）
CI 執行：GitHub Actions 每日排程，見 .github/workflows/cron.yml
"""
import os
import ssl
import sys
import time
import gzip
import zipfile
import io
import urllib.request
import urllib.parse

import pandas as pd

BASE_URL = "https://announcement.mol.gov.tw/Download/"
FIELDS = {
    "downloadType": "3",
    "CITYNO": "",          # 空=全部
    "UNITNAME": "",
    "REGNUMBER": "1",      # 1=勞動基準法
    "REGNO": "",
    "FINE": "",
    "DOCstartDate": "",
    "DOCEndDate": "",
}
DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "labor_violations.csv")
MAX_ATTEMPTS = 3
RETRY_DELAY = 10  # 秒

# 勞動部伺服器憑證鏈有問題（2026-06-18 起已知）；先走正常驗證，失敗才降級重試並留下警告
STRICT_CTX = ssl.create_default_context()
LENIENT_CTX = ssl.create_default_context()
LENIENT_CTX.check_hostname = False
LENIENT_CTX.verify_mode = ssl.CERT_NONE

KNOWN_CITIES = {
    "台北市", "新北市", "桃園市", "台中市", "台南市", "高雄市",
    "基隆市", "新竹市", "嘉義市", "新竹縣", "苗栗縣", "彰化縣",
    "南投縣", "雲林縣", "嘉義縣", "屏東縣", "宜蘭縣", "花蓮縣",
    "台東縣", "澎湖縣", "金門縣", "連江縣",
    "加工出口區管理處", "科技業園區", "農業科技園區", "科學園區",
}


def urlencode(params: dict) -> str:
    return "&".join(f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items())


def fetch_once() -> pd.DataFrame:
    """下載一次。先走憑證驗證，遇 SSL 錯誤才降級並印出警告。"""
    data = urlencode(FIELDS).encode()
    response = None
    for ctx, label in ((STRICT_CTX, "嚴格 TLS"), (LENIENT_CTX, "降級 TLS（不驗憑證）")):
        req = urllib.request.Request(BASE_URL, data=data, method="POST")
        req.add_header("User-Agent", "Mozilla/5.0")
        req.add_header("Referer", "https://announcement.mol.gov.tw/")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        try:
            with urllib.request.urlopen(req, timeout=120, context=ctx) as resp:
                raw = resp.read()
                encoding = resp.headers.get("Content-Encoding", "").strip().lower()
            response = (raw, encoding)
            break
        except urllib.error.URLError as error:
            # 憑證錯誤包在 URLError.reason 裡（SSLCertVerificationError 屬 SSLError 子類）
            reason = getattr(error, "reason", None)
            if not isinstance(reason, ssl.SSLError):
                raise  # 純網路問題，交給外層重試，不降級
            print(f"⚠️ {label} 憑證驗證失敗：{reason}")
            if label.startswith("嚴格"):
                continue
            raise
        except ssl.SSLError as error:
            print(f"⚠️ {label} 連線失敗：{error}")
            if label.startswith("嚴格"):
                continue
            raise
    if response is None:
        raise RuntimeError("無法建立連線")
    raw, encoding = response
    if label.startswith("降級"):
        print("⚠️ 勞動部憑證驗證失敗，已降級為不驗證 TLS 抓取（資料仍為官方來源，請留意）")
    print(f"下載完成（{label}），大小：{len(raw):,} bytes")

    if encoding == "gzip":
        raw = gzip.decompress(raw)
        print(f"解壓後大小：{len(raw):,} bytes")

    # 伺服器可能直接回 CSV，也可能包 ZIP
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            csv_files = [f for f in z.namelist() if f.endswith(".csv")]
            print(f"ZIP 內含 {len(csv_files)} 個 CSV 檔")
            frames = []
            for fname in csv_files:
                with z.open(fname) as f:
                    frames.append(pd.read_csv(f, encoding="utf-8-sig", skiprows=1, dtype=str))
            df = pd.concat(frames, ignore_index=True)
    except zipfile.BadZipFile:
        df = pd.read_csv(io.BytesIO(raw), encoding="utf-8-sig", skiprows=1, dtype=str)

    return df.dropna(how="all")


def fetch() -> pd.DataFrame:
    """最多 3 次重試，避開勞動部偶發逾時。"""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            return fetch_once()
        except Exception as error:  # 網路/解析錯誤都重試
            print(f"⚠️ 第 {attempt}/{MAX_ATTEMPTS} 次下載失敗：{error}")
            if attempt < MAX_ATTEMPTS:
                time.sleep(RETRY_DELAY)
    raise RuntimeError(f"下載失敗，已重試 {MAX_ATTEMPTS} 次")


def validate(df: pd.DataFrame) -> bool:
    """格式變動檢查。下載順序不固定，檢查不可依賴第一列：
    - 全部列的縣市欄都不該是日期（日期出現代表欄位錯位，阻擋）
    - 未知縣市／機關只提示不阻擋（勞動部機關名稱會變動，例如園區改名）
    """
    if len(df) < 1000:
        print(f"⚠️ 資料筆數過少（{len(df)}），可能下載失敗")
        return False
    cities = df.iloc[:, 0].astype(str).str.strip()
    dated = cities[cities.str.contains(r"^\d{2,3}/\d{1,2}/\d{1,2}$", regex=True, na=False)]
    if not dated.empty:
        print(f"⚠️ 格式變動偵測：縣市欄出現日期值（如 '{dated.iloc[0]}'，共 {len(dated)} 列），欄位可能已錯位")
        return False
    unknown = sorted(set(cities) - KNOWN_CITIES)
    if unknown:
        print(f"ℹ️ 有 {len(unknown)} 個非縣市機關（不阻擋）：{', '.join(unknown[:5])}{'…' if len(unknown) > 5 else ''}")
    print(f"✅ 格式驗證通過（總筆數：{len(df):,}）")
    return True


if __name__ == "__main__":
    df = fetch()
    if not validate(df):
        print("格式驗證失敗，終止寫入。請檢查勞動部是否變更格式。")
        sys.exit(1)

    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    df.to_csv(DATA_FILE, encoding="utf-8-sig", index=False)
    print(f"已更新 {len(df):,} 筆資料 → {DATA_FILE}")

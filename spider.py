#!/usr/bin/env python3
"""
更新勞動部裁罰資料
直接執行會下載最新 CSV 並取代 data/labor_violations.csv

用法：
  python update_data.py
"""
import os, sys, zipfile, io, re, ssl
import urllib.request
import urllib.parse
import pandas as pd

# 針對勞動部舊版 SSL 的降級處理
SSL_ctx = ssl.create_default_context()
SSL_ctx.check_hostname = False
SSL_ctx.verify_mode = ssl.CERT_NONE

BASE_URL = "https://announcement.mol.gov.tw/Download/"
FIELDS = {
    "downloadType": "3",
    "CITYNO": "",          # 空=全部，可改如 "63" 只下載台北市
    "UNITNAME": "",
    "REGNUMBER": "1",      # 1=勞動基準法
    "REGNO": "",
    "FINE": "",
    "DOCstartDate": "",
    "DOCEndDate": "",
}
DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "labor_violations.csv")

KNOWN_CITIES = {
    "台北市", "新北市", "桃園市", "台中市", "台南市", "高雄市",
    "基隆市", "新竹市", "嘉義市", "新竹縣", "苗栗縣", "彰化縣",
    "南投縣", "雲林縣", "嘉義縣", "屏東縣", "宜蘭縣", "花蓮縣",
    "台東縣", "澎湖縣", "金門縣", "連江縣",
    "加工出口區管理處", "科技業園區", "農業科技園區", "科學園區",
}

def validate(df: pd.DataFrame) -> bool:
    """格式變動檢查：驗證第一筆資料的縣市是否為已知縣市名稱（而非日期）"""
    if len(df) < 1000:
        print(f"⚠️ 資料筆數過少（{len(df)}），可能下載失敗")
        return False
    # 取第一筆資料的縣市欄位（row index 0）
    city = str(df.iloc[0, 0]).strip()
    if city not in KNOWN_CITIES:
        # 可能是日期（代表格式錯位）
        if "/" in city and city.split("/")[0].isdigit():
            print(f"⚠️ 格式變動偵測：第一筆資料是日期 '{city}'，縣市欄位可能已錯位")
            return False
        print(f"⚠️ 未知縣市 '{city}'，可能格式已有變動")
        return False
    print(f"✅ 格式驗證通過（首筆縣市：{city}，總筆數：{len(df):,}）")
    return True

def fetch() -> pd.DataFrame:
    data = urlencode(FIELDS).encode()
    req = urllib.request.Request(BASE_URL, data=data, method="POST")
    req.add_header("User-Agent", "Mozilla/5.0")
    req.add_header("Referer", "https://announcement.mol.gov.tw/")

    print("正在下載最新資料（約 8 萬筆），請稍候...")
    with urllib.request.urlopen(req, timeout=120, context=SSL_ctx) as resp:
        raw = resp.read()

    print(f"下載完成，檔案大小：{len(raw):,} bytes")

    # CSV 直接解碼（伺服器直接回傳 CSV，不再是 ZIP）
    from io import StringIO
    text = raw.decode("utf-8-sig", errors="replace")
    df = pd.read_csv(StringIO(text), dtype=str, skiprows=1)
    return df

def urlencode(params: dict) -> str:
    return "&".join(f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items())

if __name__ == "__main__":
    df = fetch()
    if not validate(df):
        print("格式驗證失敗，終止寫入。請檢查勞動部是否變更格式。")
        sys.exit(1)

    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    df.to_csv(DATA_FILE, encoding="utf-8-sig", index=False)
    print(f"已更新 {len(df):,} 筆資料 → {DATA_FILE}")
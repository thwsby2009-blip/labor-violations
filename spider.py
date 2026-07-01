#!/usr/bin/env python3
"""
更新勞動部裁罰資料
直接執行會下載最新 CSV 並取代 data/labor_violations.csv

用法：
  python spider.py
"""
import os, zipfile, io, ssl
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

# 對應勞動部 CSV 的實際欄位（不依賴 CSV 原本的標題列）
COLUMN_NAMES = [
    "編號",
    "縣市",
    "公告日期",
    "事業單位",
    "處分日期",
    "處分字號",
    "違反法規",
    "法條敘述",
    "罰鍰金額",
]
COLUMN_DTYPES = {col: str for col in COLUMN_NAMES}


def urlencode(params: dict) -> str:
    return "&".join(f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items())


def fetch() -> pd.DataFrame:
    data = urlencode(FIELDS).encode()
    req = urllib.request.Request(BASE_URL, data=data, method="POST")
    req.add_header("User-Agent", "Mozilla/5.0")
    req.add_header("Referer", "https://announcement.mol.gov.tw/")

    print("正在下載最新資料（約 8 萬筆），請稍候...")
    with urllib.request.urlopen(req, timeout=120, context=SSL_ctx) as resp:
        raw = resp.read()

    print(f"下載完成，檔案大小：{len(raw):,} bytes")

    # 解 ZIP，合併所有縣市 CSV
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        csv_files = [f for f in z.namelist() if f.endswith(".csv")]
        print(f"ZIP 內含 {len(csv_files)} 個 CSV 檔：{csv_files}")
        dfs = []
        for fname in csv_files:
            with z.open(fname) as f:
                # 跳過第一列（「違反雇主清冊」標題）
                # 手動指定欄位名稱，不依賴 CSV 原本的標題列
                df = pd.read_csv(
                    f,
                    encoding="utf-8-sig",
                    skiprows=1,
                    header=None,
                    names=COLUMN_NAMES,
                    dtype=COLUMN_DTYPES,
                    on_bad_lines="skip",
                )
                dfs.append(df)
        combined = pd.concat(dfs, ignore_index=True)

    # 去除全空白列與「編號」=空的（過濾標題殘留列）
    combined = combined.dropna(how="all")
    if "編號" in combined.columns:
        combined = combined[combined["編號"].str.strip() != ""]
    return combined


if __name__ == "__main__":
    df = fetch()

    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    df.to_csv(DATA_FILE, encoding="utf-8-sig", index=False)
    print(f"已更新 {len(df):,} 筆資料 → {DATA_FILE}")
#!/usr/bin/env python3
"""
更新勞動部裁罰資料
直接執行會下載最新 CSV 並取代 data/labor_violations.csv

用法：
  python update_data.py
"""
import os, sys, zipfile, io, re
import urllib.request
import pandas as pd

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

def fetch() -> pd.DataFrame:
    data = urlencode(FIELDS).encode()
    req = urllib.request.Request(BASE_URL, data=data, method="POST")
    req.add_header("User-Agent", "Mozilla/5.0")
    req.add_header("Referer", "https://announcement.mol.gov.tw/")

    print("正在下載最新資料（約 8 萬筆），請稍候...")
    with urllib.request.urlopen(req, timeout=120) as resp:
        raw = resp.read()

    print(f"下載完成，檔案大小：{len(raw):,} bytes")

    # 解 ZIP，取最大的 CSV
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        csv_files = [f for f in z.namelist() if f.endswith(".csv")]
        print(f"ZIP 內含 {len(csv_files)} 個 CSV 檔：{csv_files}")
        # 合併所有 CSV
        dfs = []
        for fname in csv_files:
            with z.open(fname) as f:
                df = pd.read_csv(f, encoding="utf-8-sig", skiprows=1, dtype=str)
                dfs.append(df)
        combined = pd.concat(dfs, ignore_index=True)

    # 去除全空白列
    combined = combined.dropna(how="all")
    return combined

def urlencode(params: dict) -> str:
    return "&".join(f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items())

if __name__ == "__main__":
    import urllib.parse
    df = fetch()

    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    df.to_csv(DATA_FILE, encoding="utf-8-sig", index=False)
    print(f"已更新 {len(df):,} 筆資料 → {DATA_FILE}")
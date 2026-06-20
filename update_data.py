#!/usr/bin/env python3
"""
更新勞動部裁罰資料
直接執行會下載最新 CSV 並取代 data/labor_violations.csv

用法：
  python update_data.py
"""
import os, sys, zipfile, io, ssl
import pandas as pd

ssl._create_default_https_context = ssl._create_unverified_context

BASE_URL = "https://announcement.mol.gov.tw/Download/"
FIELDS = {
    "downloadType": "3",
    "CITYNO": "",
    "UNITNAME": "",
    "REGNUMBER": "1",   # 1=勞動基準法
    "REGNO": "",
    "FINE": "",
    "DOCstartDate": "",
    "DOCEndDate": "",
}
DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "labor_violations.csv")


def urlencode(params):
    import urllib.parse
    return "&".join(f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items())


def fetch() -> pd.DataFrame:
    import urllib.request
    import gzip

    data = urlencode(FIELDS).encode()
    req = urllib.request.Request(BASE_URL, data=data, method="POST")
    req.add_header("User-Agent", "Mozilla/5.0")
    req.add_header("Referer", "https://announcement.mol.gov.tw/")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    print("正在下載最新資料（約 8 萬筆），請稍候...")
    with urllib.request.urlopen(req, timeout=120) as resp:
        raw = resp.read()
        content_encoding = resp.headers.get("Content-Encoding", "").strip().lower()

    print(f"下載完成，原始大小：{len(raw):,} bytes，編碼：{content_encoding}")

    # 解壓縮（如果伺服器用 gzip 壓縮）
    if content_encoding == "gzip":
        raw = gzip.decompress(raw)
        print(f"解壓後大小：{len(raw):,} bytes")

    # 嘗試解 ZIP，失敗就當 CSV
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            csv_files = [f for f in z.namelist() if f.endswith(".csv")]
            print(f"ZIP 內含 {len(csv_files)} 個 CSV 檔")
            dfs = []
            for fname in csv_files:
                with z.open(fname) as f:
                    df = pd.read_csv(f, encoding="utf-8-sig", skiprows=1, dtype=str)
                    dfs.append(df)
            combined = pd.concat(dfs, ignore_index=True)
    except zipfile.BadZipFile:
        # 直接是 CSV
        print("直接 CSV 格式，解析中...")
        combined = pd.read_csv(io.BytesIO(raw), encoding="utf-8-sig", skiprows=1, dtype=str)

    combined = combined.dropna(how="all")
    return combined


if __name__ == "__main__":
    import urllib.parse
    df = fetch()

    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    df.to_csv(DATA_FILE, encoding="utf-8-sig", index=False)
    print(f"已更新 {len(df):,} 筆資料 → {DATA_FILE}")
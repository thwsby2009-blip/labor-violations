# 違反勞動基準法裁罰查詢

以年度直條圖、縣市長條圖及違規類型環形圖呈現公開裁罰資料，並提供篩選與明細查詢。

**線上版：** https://labor-violations-vd3ywxclaubcxqtozzh6gf.streamlit.app/

---

## 功能

- **視覺化總覽** — 裁罰案件數、依公告名稱區分的事業單位數、已提供罰鍰總額
- **年度直條圖** — 依處分年度統計，補登舊案歸回原年度；選定年度時保留歷年比較
- **縣市排名長條圖** — 依公告機關統計，科學園區等其他機關另外列示，不推定為公司所在地
- **違規類型環形圖** — 前五種法條及其他；占比按法條出現次數，一案同條只計一次
- **互動明細** — 篩選年度、單位、法條與名稱，排序表格並下載 CSV

### 統計口徑

同一公告單位、同一處分字號合併為一件；缺少字號時只合併相同紀錄。不同法條不重複計為多件案件。金額缺漏或同件金額不一致時，不納入金額加總。公司數按完整公告名稱區分，因無統編，不能視為精確家數。日期不一致的案件不納入年度圖，保留於全部年度明細。

今年為未完整年度；裁罰紀錄不等於實際違規率，沒有紀錄也不代表零違規。資料可能含撤銷、更正備註，請以原公告為準。最新公告日期不是系統同步時間。圖表不使用 Google Maps，也不需要地圖 API 金鑰。

### 驗證

```bash
python -m unittest test_dashboard_data.py test_dashboard_ui.py
```

## 資料來源

資料來自 [勞動部公告系統](https://announcement.mol.gov.tw/)，設有每日更新排程，實際收錄以資料檔為準，包括：

- 事業單位名稱（含負責人）
- 縣市/單位別
- 處分日期與公告日期
- 違反法規條款
- 法條詳細說明
- 裁罰金額

---

## 技術

- **前端**：Streamlit（Python）
- **資料格式**：CSV（收錄於 `data/labor_violations.csv`）
- **部署**：Streamlit Cloud（連接 GitHub 自動發布）

## 本地運行

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 更新資料

### 方式一：本地更新腳本
```bash
python update_data.py
```
執行後會自動從勞動部下載最新裁罰資料，取代 `data/labor_violations.csv`。約需 30-60 秒。

### 方式二：手動更新
1. 前往 [勞動部公告系統](https://announcement.mol.gov.tw/)
2. 選擇「縣市」與「法規：勞動基準法」
3. 下載格式選 **CSV**，點下載
4. 將 CSV 檔案取代 `data/labor_violations.csv` 即完成更新

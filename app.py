import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="違反勞基法查詢", page_icon="⚖️", layout="wide")

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "labor_violations.csv")

@st.cache_data(ttl=3600)
def load_data():
    df = pd.read_csv(
        DATA_PATH,
        encoding="utf-8-sig",
        skiprows=1,  # 跳過第一行「違反雇主清冊」標題
        dtype=str,
    )
    df.columns = [c.strip() for c in df.columns]
    df = df.fillna("")
    df["縣市"] = df["縣市／單位別"].str.split("／").str[0].str.strip()
    df["罰鍰數字"] = (
        df["罰鍰金額"]
        .str.replace(",", "")
        .str.replace(" ", "")
        .str.extract(r"(\d+)", expand=False)
    )
    return df

try:
    df = load_data()
    total = len(df)
    CITIES = sorted(df["縣市"].unique().tolist())
    LAW_ARTICLES = sorted(df["違反法規條款"].unique().tolist())
except Exception as e:
    st.error(f"無法讀取資料：{e}")
    st.stop()

# ===== UI =====
st.title("⚖️ 違反勞動基準法裁罰查詢")
st.caption(f"共 {total:,} 筆裁罰資料｜資料來源：勞動部")

with st.container():
    c1, c2, c3 = st.columns(3)
    with c1:
        city = st.selectbox("縣市", ["全部"] + CITIES)
    with c2:
        article = st.selectbox("違反法條", ["全部"] + LAW_ARTICLES)
    with c3:
        keyword = st.text_input("公司名稱關鍵字", placeholder="輸入公司名稱...")

filtered = df.copy()
if city != "全部":
    filtered = filtered[filtered["縣市"] == city]
if article != "全部":
    filtered = filtered[filtered["違反法規條款"] == article]
if keyword:
    col_name = "事業單位名稱(負責人)\n自然人姓名"
    filtered = filtered[filtered[col_name].str.contains(keyword, na=False, regex=False)]

st.divider()
st.markdown(f"### 查到 {len(filtered):,} 筆結果")

PAGE_SIZE = 50
pages = list(range(0, len(filtered), PAGE_SIZE))

def render_page(df_page):
    for _, row in df_page.iterrows():
        co = row.get("事業單位名稱(負責人)\n自然人姓名", "").strip()
        city_val = row.get("縣市", "").strip()
        date = row.get("處分日期", "").strip()
        law = row.get("違反法規條款", "").strip()
        desc = row.get("法條敘述", "").strip()
        fine = row.get("罰鍰金額", "").strip()
        announce = row.get("公告日期", "").strip()

        with st.container():
            c1, c2, c3 = st.columns([3, 1, 1])
            with c1:
                st.markdown(f"**🏢 {co}**")
                st.caption(f"📍 {city_val}　📅 處分：{date}　📣 公告：{announce}")
            with c2:
                st.markdown(f"**{law}**")
                st.caption("違反法規")
            with c3:
                st.markdown(f"**{fine}**")
                st.caption("裁罰金額")
            st.markdown(f"　{desc}")
            st.divider()

if len(filtered) == 0:
    st.warning("沒有找到符合條件的資料，請調整篩選條件。")
else:
    page_idx = st.number_input(
        f"第幾頁（1~{len(pages)}）",
        min_value=1,
        max_value=max(1, len(pages)),
        value=1,
        step=1,
    )
    start = (page_idx - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    render_page(filtered.iloc[start:end])

# ===== SIDEBAR =====
with st.sidebar:
    st.markdown("### 📊 統計")
    st.metric("總記錄數", f"{total:,}")
    st.metric("符合篩選", f"{len(filtered):,}")
    st.markdown("---")
    st.markdown("### 🔗 資料來源")
    st.markdown("[勞動部公告系統](https://announcement.mol.gov.tw/)")
    st.markdown("---")
    st.markdown("### 📌 常見違反法條")
    st.markdown("""
    - **第24條**：延長工時未依規定加給工資
    - **第30條**：工作時間記錄未逐日記載
    - **第30-1條**：輪班制未給予充分休息
    - **第32條**：延長工時超過上限
    - **第38條**：特別休假未依法折算工資
    - **第39條**：員工請假規定未核給
    - **第22條**：工資未全額直接給付
    """)
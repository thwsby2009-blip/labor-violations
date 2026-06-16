import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="違反勞動基準法裁罰查詢", layout="wide")

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "labor_violations.csv")

# ===== DATA =====
@st.cache_data(ttl=3600)
def load_data():
    col_names = [
        "編號", "縣市／單位別", "公告日期",
        "事業單位名稱(負責人)\n自然人姓名",
        "處分日期", "處分字號",
        "違反法規條款", "法條敘述", "罰鍰金額", "備註"
    ]
    df = pd.read_csv(DATA_PATH, encoding="utf-8-sig", skiprows=2,
                     header=None, names=col_names, dtype=str)
    df = df.fillna("")
    df["縣市"] = df["縣市／單位別"].str.split("／").str[0].str.strip()
    return df

try:
    df = load_data()
    total = len(df)
    CITIES = sorted(df["縣市"].unique().tolist())
    LAW_ARTICLES = sorted(df["違反法規條款"].unique().tolist())
except Exception as e:
    st.error(f"無法讀取資料：{e}")
    st.stop()

# ===== HEADER =====
st.title("⚖️ 違反勞動基準法裁罰查詢")
st.caption(f"Labor Standards Act Violations — 公開資料視覺化")
st.markdown(f"**裁罰總筆數** {total:,} 筆　**涵蓋縣市** {len(CITIES)} 個　**違反法條** {len(LAW_ARTICLES)} 種")
st.divider()

# ===== FILTER =====
c1, c2, c3 = st.columns([1, 1, 1.5])
with c1:
    city = st.selectbox("縣市", ["全部"] + CITIES)
with c2:
    article = st.selectbox("違反法條", ["全部"] + LAW_ARTICLES)
with c3:
    keyword = st.text_input("公司名稱關鍵字", placeholder="輸入公司名稱或負責人...")

# ===== FILTER DATA =====
filtered = df.copy()
if city != "全部":
    filtered = filtered[filtered["縣市"] == city]
if article != "全部":
    filtered = filtered[filtered["違反法規條款"] == article]
if keyword:
    filtered = filtered[filtered["事業單位名稱(負責人)\n自然人姓名"].str.contains(keyword, na=False, regex=False)]

st.markdown(f"**查到 {len(filtered):,} 筆結果，共 {total:,} 筆資料**")

PAGE_SIZE = 30
pages = list(range(0, len(filtered), PAGE_SIZE))

def render_page(df_page):
    for _, row in df_page.iterrows():
        co   = row["事業單位名稱(負責人)\n自然人姓名"].strip()
        city = row["縣市"].strip()
        date = row["處分日期"].strip()
        law  = row["違反法規條款"].strip()
        desc = row["法條敘述"].strip().replace(";", "；")
        fine = row["罰鍰金額"].strip()
        ann  = row["公告日期"].strip()
        unit = row["縣市／單位別"].strip()

        with st.container():
            cl, cr = st.columns([4, 1])
            with cl:
                st.markdown(f"**🏢 {co}**")
                st.caption(f"📍 {unit}　📅 處分：{date}　📣 公告：{ann}")
            with cr:
                if law:
                    st.markdown(f":orange[{law}]")
                if fine:
                    st.markdown(f":red[**{fine}**]")
            st.markdown(f"{desc}")
        st.divider()

if len(filtered) == 0:
    st.warning("沒有找到符合條件的資料，請調整篩選條件。")
else:
    page_idx = st.number_input(f"第幾頁（1~{len(pages)}）",
        min_value=1, max_value=max(1, len(pages)), value=1, step=1,
        label_visibility="collapsed")
    start = (page_idx - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    render_page(filtered.iloc[start:end])

# ===== SIDEBAR =====
with st.sidebar:
    st.markdown("### 📊 統計概覽")
    st.markdown(f"裁罰總筆數 **{total:,}** 筆")
    st.markdown(f"符合篩選 **{len(filtered):,}** 筆")
    st.markdown(f"涵蓋縣市 **{len(CITIES)}** 個")
    st.divider()
    st.markdown("### 🔗 資料來源")
    st.markdown("[➡️ 勞動部公告系統](https://announcement.mol.gov.tw/)")
    st.divider()
    st.markdown("### 📌 常見違反法條")
    laws = [
        ("第24條", "延長工時未依規定加給工資"),
        ("第30條", "工時未逐日記載"),
        ("第30-1條", "輪班制未給予充分休息"),
        ("第32條", "延長工時超過上限"),
        ("第38條", "特別休假未依法折算"),
        ("第39條", "員工請假規定未核給"),
        ("第22條", "工資未全額直接給付"),
    ]
    for num, text in laws:
        st.markdown(f"**{num}** {text}")
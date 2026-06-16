import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="違反勞基法查詢", page_icon="⚖️", layout="wide")

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "labor_violations.csv")

# ===== CUSTOM CSS =====
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;500;600;700&family=Noto+Sans+TC:wght@300;400;500;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --bg: #f4f2ed;
  --surface: #ffffff;
  --border: #e0ddd5;
  --text: #1a1814;
  --muted: #8a8278;
  --accent: #c8922a;
  --accent-light: #fdf3e0;
  --navy: #1c2b3a;
  --red: #c0392b;
  --red-light: #fdecea;
  --mono: 'JetBrains Mono', monospace;
}

* { font-family: 'Noto Sans TC', 'Chakra Petch', sans-serif; }

.stApp { background: var(--bg); }

.header-wrap {
  background: var(--navy);
  border-radius: 16px;
  padding: 28px 32px;
  margin-bottom: 20px;
}
.header-title {
  font-family: 'Chakra Petch', sans-serif;
  font-size: 1.5rem;
  font-weight: 700;
  color: #ffffff;
  letter-spacing: 2px;
}
.header-title span { color: var(--accent); }
.header-sub { font-size: 0.75rem; color: rgba(255,255,255,0.45); margin-top: 4px; }
.stat-num { font-family: var(--mono); font-size: 1.3rem; font-weight: 600; color: #fff; }
.stat-label { font-size: 0.65rem; color: rgba(255,255,255,0.4); letter-spacing: 1px; text-transform: uppercase; margin-top: 1px; }

.filter-bar {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 18px 24px;
  margin-bottom: 20px;
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
}

.record-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 18px 20px;
  margin-bottom: 12px;
  border-left: 3px solid var(--accent);
}
.record-company { font-size: 0.95rem; font-weight: 600; color: var(--text); }
.record-meta { font-size: 0.7rem; color: var(--muted); margin-top: 4px; display: flex; gap: 12px; flex-wrap: wrap; }
.record-badges { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; margin-top: 6px; }
.badge-law {
  background: var(--accent-light);
  color: var(--accent);
  border: 1px solid rgba(200,146,42,0.25);
  border-radius: 6px;
  padding: 2px 9px;
  font-size: 0.7rem;
  font-weight: 600;
  font-family: var(--mono);
}
.badge-fine {
  background: var(--red-light);
  color: var(--red);
  border: 1px solid rgba(192,57,43,0.18);
  border-radius: 6px;
  padding: 2px 9px;
  font-size: 0.78rem;
  font-weight: 700;
  font-family: var(--mono);
}
.record-desc { font-size: 0.76rem; color: var(--muted); margin-top: 8px; line-height: 1.6; padding-top: 8px; border-top: 1px solid var(--border); }

.sidebar-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 14px;
}
.sidebar-title {
  font-size: 0.65rem;
  font-weight: 700;
  color: var(--accent);
  letter-spacing: 2px;
  text-transform: uppercase;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border);
}
.sidebar-row { display: flex; justify-content: space-between; align-items: center; padding: 4px 0; }
.sidebar-val { font-family: var(--mono); font-weight: 600; color: var(--navy); font-size: 0.82rem; }
.sidebar-law { display: flex; gap: 8px; padding: 3px 0; }
.sidebar-law-num { font-family: var(--mono); color: var(--accent); font-weight: 600; font-size: 0.72rem; min-width: 52px; }
.sidebar-law-text { font-size: 0.72rem; color: var(--muted); }

/* Streamlit element overrides */
.stTextInput input, .stSelectbox div {
  border-color: var(--border) !important;
  color: var(--text) !important;
}
.stTextInput input:focus, .stSelectbox:focus-within {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 2px rgba(200,146,42,0.12) !important;
}
</style>
""", unsafe_allow_html=True)

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
st.markdown('<div class="header-wrap">', unsafe_allow_html=True)
ch1, ch2 = st.columns([1, 1])
with ch1:
    st.markdown('<div class="header-title">⚖️ 違反勞動基準法裁罰查詢</div>', unsafe_allow_html=True)
    st.markdown('<div class="header-sub">Labor Standards Act Violations — 公開資料視覺化</div>', unsafe_allow_html=True)
with ch2:
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        st.markdown(f'<div class="stat-num">{total:,}</div><div class="stat-label">裁罰總筆數</div>', unsafe_allow_html=True)
    with sc2:
        st.markdown(f'<div class="stat-num">{len(CITIES)}</div><div class="stat-label">涵蓋縣市</div>', unsafe_allow_html=True)
    with sc3:
        st.markdown(f'<div class="stat-num">{len(LAW_ARTICLES)}</div><div class="stat-label">違反法條</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ===== FILTER =====
st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
c1, c2, c3 = st.columns([1, 1, 1.5])
with c1:
    city = st.selectbox("縣市", ["全部"] + CITIES, label_visibility="collapsed")
with c2:
    article = st.selectbox("違反法條", ["全部"] + LAW_ARTICLES, label_visibility="collapsed")
with c3:
    keyword = st.text_input("公司名稱關鍵字", placeholder="輸入公司名稱或負責人...", label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

# ===== FILTER =====
filtered = df.copy()
if city != "全部":
    filtered = filtered[filtered["縣市"] == city]
if article != "全部":
    filtered = filtered[filtered["違反法規條款"] == article]
if keyword:
    filtered = filtered[filtered["事業單位名稱(負責人)\n自然人姓名"].str.contains(keyword, na=False, regex=False)]

st.markdown(f"**查到 {len(filtered):,} 筆結果，共 {total:,} 筆**", unsafe_allow_html=False)

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
            # Row: company + badges
            col_left, col_right = st.columns([4, 1])
            with col_left:
                st.markdown(f"**🏢 {co}**")
                st.caption(f"📍 {unit}　📅 處分：{date}　📣 公告：{ann}")
            with col_right:
                st.markdown(f'<div class="record-badges">', unsafe_allow_html=True)
                st.markdown(f'<span class="badge-law">{law}</span>', unsafe_allow_html=True)
                if fine:
                    st.markdown(f'<span class="badge-fine">{fine}</span>', unsafe_allow_html=True)
                st.markdown(f'</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="record-desc">▸ {desc}</div>', unsafe_allow_html=True)
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
    st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">📊 統計概覽</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sidebar-row"><span>裁罰總筆數</span><span class="sidebar-val">{total:,}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sidebar-row"><span>符合篩選</span><span class="sidebar-val">{len(filtered):,}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sidebar-row"><span>涵蓋縣市</span><span class="sidebar-val">{len(CITIES)}</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">🔗 資料來源</div>', unsafe_allow_html=True)
    st.markdown('[➡️ 勞動部公告系統](https://announcement.mol.gov.tw/)')
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">📌 常見違反法條</div>', unsafe_allow_html=True)
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
        st.markdown(f'<div class="sidebar-law"><span class="sidebar-law-num">{num}</span><span class="sidebar-law-text">{text}</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
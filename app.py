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
  --navy-light: #2d4356;
  --red: #c0392b;
  --red-light: #fdecea;
  --mono: 'JetBrains Mono', monospace;
}

* { font-family: 'Noto Sans TC', 'Chakra Petch', sans-serif; }

/* Page background */
.stApp { background: var(--bg); }

/* Main card */
.main-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 28px 32px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}

/* Header */
.header-wrap {
  background: var(--navy);
  border-radius: 16px;
  padding: 28px 32px;
  margin-bottom: 20px;
  position: relative;
  overflow: hidden;
}
.header-wrap::before {
  content: '';
  position: absolute;
  top: 0; right: 0;
  width: 300px; height: 100%;
  background: linear-gradient(135deg, transparent 40%, rgba(200,146,42,0.15) 100%);
  pointer-events: none;
}
.header-title {
  font-family: 'Chakra Petch', 'Noto Sans TC', sans-serif;
  font-size: 1.6rem;
  font-weight: 700;
  color: #ffffff;
  letter-spacing: 2px;
  margin-bottom: 6px;
}
.header-title span { color: var(--accent); }
.header-sub {
  font-size: 0.78rem;
  color: rgba(255,255,255,0.5);
  letter-spacing: 1px;
}
.header-stats {
  display: flex;
  gap: 32px;
  margin-top: 20px;
}
.stat-item { text-align: center; }
.stat-num {
  font-family: 'JetBrains Mono', monospace;
  font-size: 1.5rem;
  font-weight: 500;
  color: #fff;
}
.stat-label { font-size: 0.68rem; color: rgba(255,255,255,0.45); letter-spacing: 1px; text-transform: uppercase; margin-top: 2px; }

/* Stat pills in header */
.stat-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 20px;
  padding: 4px 12px;
  font-size: 0.75rem;
  color: rgba(255,255,255,0.7);
}
.stat-pill strong { color: var(--accent); font-family: 'JetBrains Mono', monospace; }

/* Filter bar */
.filter-bar {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 18px 24px;
  margin-bottom: 20px;
  display: flex;
  gap: 14px;
  align-items: flex-end;
  flex-wrap: wrap;
}
.filter-group { flex: 1; min-width: 160px; }
.filter-label {
  font-size: 0.68rem;
  font-weight: 500;
  color: var(--muted);
  letter-spacing: 1.5px;
  text-transform: uppercase;
  margin-bottom: 6px;
}
.filter-divider { width: 1px; background: var(--border); align-self: stretch; }

/* Result count */
.result-count {
  font-family: 'Chakra Petch', sans-serif;
  font-size: 0.82rem;
  color: var(--muted);
  letter-spacing: 1px;
  margin-bottom: 14px;
}
.result-count strong { color: var(--accent); font-weight: 600; }

/* Record card */
.record-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px 24px;
  margin-bottom: 12px;
  transition: all 0.2s;
  position: relative;
}
.record-card:hover {
  border-color: var(--accent);
  box-shadow: 0 4px 20px rgba(200,146,42,0.1);
  transform: translateY(-1px);
}
.record-card::before {
  content: '';
  position: absolute;
  left: 0; top: 12px; bottom: 12px;
  width: 3px;
  background: var(--accent);
  border-radius: 0 2px 2px 0;
  opacity: 0;
  transition: opacity 0.2s;
}
.record-card:hover::before { opacity: 1; }

.record-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 10px;
}
.record-company {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text);
  line-height: 1.4;
}
.record-meta {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  margin-top: 5px;
}
.record-meta-item {
  font-size: 0.72rem;
  color: var(--muted);
  display: flex;
  align-items: center;
  gap: 4px;
}
.record-meta-item .dot {
  width: 4px; height: 4px;
  border-radius: 50%;
  background: var(--accent);
  flex-shrink: 0;
}
.record-badges { display: flex; gap: 8px; align-items: center; flex-shrink: 0; }
.badge-law {
  background: var(--accent-light);
  color: var(--accent);
  border: 1px solid rgba(200,146,42,0.2);
  border-radius: 6px;
  padding: 3px 10px;
  font-size: 0.72rem;
  font-weight: 600;
  font-family: 'JetBrains Mono', monospace;
  white-space: nowrap;
}
.badge-fine {
  background: var(--red-light);
  color: var(--red);
  border: 1px solid rgba(192,57,43,0.15);
  border-radius: 6px;
  padding: 3px 10px;
  font-size: 0.8rem;
  font-weight: 700;
  font-family: 'JetBrains Mono', monospace;
  white-space: nowrap;
}
.record-desc {
  font-size: 0.8rem;
  color: var(--muted);
  line-height: 1.6;
  padding-top: 8px;
  border-top: 1px solid var(--border);
  margin-top: 8px;
}

/* Sidebar */
.sidebar-section {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 18px;
  margin-bottom: 14px;
}
.sidebar-title {
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--accent);
  letter-spacing: 2px;
  text-transform: uppercase;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border);
}
.sidebar-stat {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
  font-size: 0.82rem;
}
.sidebar-stat .val {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 600;
  color: var(--navy);
}
.sidebar-link {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  color: var(--accent);
  text-decoration: none;
  font-size: 0.78rem;
  padding: 6px 0;
  transition: opacity 0.2s;
}
.sidebar-link:hover { opacity: 0.7; }
.sidebar-law-item {
  font-size: 0.75rem;
  color: var(--muted);
  padding: 4px 0;
  border-bottom: 1px dashed rgba(0,0,0,0.06);
  display: flex;
  gap: 8px;
}
.sidebar-law-item:last-child { border-bottom: none; }
.sidebar-law-item .num {
  font-family: 'JetBrains Mono', monospace;
  color: var(--accent);
  font-weight: 600;
  white-space: nowrap;
  min-width: 60px;
}

/* Pagination */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 24px;
  font-family: 'JetBrains Mono', monospace;
}

/* Streamlit overrides */
.stTextInput > div > div > input,
.stSelectbox > div > div {
  border-radius: 8px !important;
  border-color: var(--border) !important;
  color: var(--text) !important;
}
.stTextInput > div > div > input:focus,
.stSelectbox > div > div:focus-within {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 2px rgba(200,146,42,0.15) !important;
}
[data-testid="stMetricValue"] { font-family: 'JetBrains Mono', monospace !important; }
.stMarkdown, .stText, p, span { color: var(--text) !important; }
.stApp h1, .stApp h2, .stApp h3, .stApp h4 { color: var(--navy) !important; }
</style>
""", unsafe_allow_html=True)

# ===== DATA LOAD =====
@st.cache_data(ttl=3600)
def load_data():
    col_names = [
        "編號", "縣市／單位別", "公告日期",
        "事業單位名稱(負責人)\n自然人姓名",
        "處分日期", "處分字號",
        "違反法規條款", "法條敘述", "罰鍰金額", "備註"
    ]
    df = pd.read_csv(
        DATA_PATH, encoding="utf-8-sig",
        skiprows=2, header=None, names=col_names, dtype=str,
    )
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
col_h1, col_h2 = st.columns([1, 1])
with col_h1:
    st.markdown('<div class="header-title">⚖️ 違反勞動基準法裁罰查詢</div>', unsafe_allow_html=True)
    st.markdown('<div class="header-sub">Labor Standards Act Violations — 公開資料視覺化</div>', unsafe_allow_html=True)
with col_h2:
    st.markdown(f"""
    <div class="header-stats">
        <div class="stat-item">
            <div class="stat-num">{total:,}</div>
            <div class="stat-label">裁罰總筆數</div>
        </div>
        <div class="stat-item">
            <div class="stat-num">{len(CITIES)}</div>
            <div class="stat-label">涵蓋縣市</div>
        </div>
        <div class="stat-item">
            <div class="stat-num">{len(LAW_ARTICLES)}</div>
            <div class="stat-label">違反法條</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ===== FILTER =====
st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
f1, f2, f3 = st.columns([1, 1, 1.5])
with f1:
    city = st.selectbox("縣市", ["全部"] + CITIES, label_visibility="collapsed")
with f2:
    article = st.selectbox("違反法條", ["全部"] + LAW_ARTICLES, label_visibility="collapsed")
with f3:
    keyword = st.text_input(
        "公司名稱關鍵字",
        placeholder="輸入公司名稱、主要產品或負責人姓名...",
        label_visibility="collapsed"
    )
st.markdown('</div>', unsafe_allow_html=True)

# ===== FILTER DATA =====
filtered = df.copy()
if city != "全部":
    filtered = filtered[filtered["縣市"] == city]
if article != "全部":
    filtered = filtered[filtered["違反法規條款"] == article]
if keyword:
    col_name = "事業單位名稱(負責人)\n自然人姓名"
    filtered = filtered[filtered[col_name].str.contains(keyword, na=False, regex=False)]

# ===== RESULTS =====
st.markdown(f'<div class="result-count">查到 <strong>{len(filtered):,}</strong> 筆結果，共 <strong>{total:,}</strong> 筆資料</div>', unsafe_allow_html=True)

PAGE_SIZE = 30
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

        st.markdown(f"""
        <div class="record-card">
            <div class="record-top">
                <div>
                    <div class="record-company">🏢 {co}</div>
                    <div class="record-meta">
                        <div class="record-meta-item"><div class="dot"></div>{city_val}</div>
                        <div class="record-meta-item"><div class="dot"></div>處分 {date}</div>
                        <div class="record-meta-item"><div class="dot"></div>公告 {announce}</div>
                    </div>
                </div>
                <div class="record-badges">
                    <div class="badge-law">{law}</div>
                    <div class="badge-fine">{fine}</div>
                </div>
            </div>
            <div class="record-desc">▸ {desc}</div>
        </div>
        """, unsafe_allow_html=True)

if len(filtered) == 0:
    st.warning("沒有找到符合條件的資料，請調整篩選條件。")
else:
    page_idx = st.number_input(
        f"第幾頁（1~{len(pages)}）",
        min_value=1,
        max_value=max(1, len(pages)),
        value=1,
        step=1,
        label_visibility="collapsed",
    )
    start = (page_idx - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    render_page(filtered.iloc[start:end])

# ===== SIDEBAR =====
with st.sidebar:
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">📊 統計概覽</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="sidebar-stat"><span>裁罰總筆數</span><span class="val">{total:,}</span></div>
    <div class="sidebar-stat"><span>符合篩選</span><span class="val">{len(filtered):,}</span></div>
    <div class="sidebar-stat"><span>涵蓋縣市</span><span class="val">{len(CITIES)}</span></div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">🔗 資料來源</div>', unsafe_allow_html=True)
    st.markdown('<a class="sidebar-link" href="https://announcement.mol.gov.tw/" target="_blank">➡️ 勞動部公告系統</a>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">📌 常見違反法條</div>', unsafe_allow_html=True)
    laws = [
        ("第24條", "延長工時未依規定加給工資"),
        ("第30條", "工作時間未逐日記載"),
        ("第30-1條", "輪班制未給予充分休息"),
        ("第32條", "延長工時超過上限"),
        ("第38條", "特別休假未依法折算"),
        ("第39條", "員工請假規定未核給"),
        ("第22條", "工資未全額直接給付"),
    ]
    for num, text in laws:
        st.markdown(f'<div class="sidebar-law-item"><span class="num">{num}</span><span>{text}</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
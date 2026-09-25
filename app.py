from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import altair as alt
import pandas as pd
import streamlit as st

from dashboard_data import CITIES, load_cases

st.set_page_config(page_title='勞基法裁罰數據總覽', page_icon='⚖️', layout='wide')
st.markdown('''<style>
.stApp {background: #f6f8fc;}
.block-container {max-width: 1440px; padding-top: 2.5rem;}
[data-testid="stMetric"] {background: white; border: 1px solid #e3e9f2;
border-radius: 16px; padding: 20px;}
[data-testid="stMetricLabel"] {color: #52627a;}
h1,h2,h3 {color: #172b4d;}
</style>''', unsafe_allow_html=True)
DATA_PATH = Path(__file__).parent / 'data' / 'labor_violations.csv'


@st.cache_data
def read_data(mtime):
    records, info = load_cases(DATA_PATH)
    frame = pd.DataFrame(records)
    if frame.empty:
        return frame, info
    for column in ('處分日期', '公告日期'):
        frame[column] = pd.to_datetime(frame[column])
    return frame, info


try:
    df, info = read_data(DATA_PATH.stat().st_mtime_ns)
    if df.empty:
        st.warning('目前沒有可讀取的裁罰資料。')
        st.stop()
except (OSError, ValueError) as error:
    st.error(f'無法讀取資料：{error}')
    st.stop()

st.caption('TAIWAN LABOR DATA  /  公開裁罰資料')
st.title('勞基法裁罰數據總覽')
st.write('從年度變化、縣市分布到違規類型，了解已公開的裁罰紀錄。')
latest = df['公告日期'].max()
st.caption(f'資料內最新公告日期：{latest:%Y/%m/%d}' if pd.notna(latest) else '資料內最新公告日期：未提供')

years = sorted(df['處分年度'].dropna().astype(int).unique(), reverse=True)
units = sorted(df['單位'].unique())
c1, c2, c3, c4 = st.columns([1, 1.3, 1, 1.7])
year = c1.selectbox('處分年度', ['全部年度'] + [str(y) for y in years])
unit = c2.selectbox('縣市／公告單位', ['全部'] + units)
law_options = sorted({v for values in df['條款'] for v in values})
law = c3.selectbox('違反法條', ['全部'] + law_options)
keyword = c4.text_input('公司／負責人', placeholder='輸入名稱搜尋')

base = df.copy()
if unit != '全部':
    base = base[base['單位'] == unit]
if law != '全部':
    base = base[base['條款'].map(lambda values: law in values)]
if keyword.strip():
    base = base[base['事業單位'].str.contains(keyword.strip(), regex=False, na=False)]
filtered = base if year == '全部年度' else base[base['處分年度'] == int(year)]

m1, m2, m3 = st.columns(3)
m1.metric('裁罰案件數', f'{len(filtered):,}', help='同一公告單位、同一處分字號合併為一件；無字號時僅合併相同紀錄。')
m2.metric('受裁罰事業單位（依公告名稱）', f'{filtered["事業單位"].nunique():,}', help='目前沒有統編，以完整公告名稱（含負責人）區分，不能視為精確的公司家數。')
m3.metric('已提供罰鍰總額', f'NT$ {filtered["罰鍰金額"].sum():,.0f}')
missing_amount = int(filtered['罰鍰金額'].isna().sum())
st.caption(f'金額未提供或不一致：{missing_amount:,} 件，未列入金額加總。裁罰件數反映已收錄紀錄，不代表實際違規率。')
today = datetime.now(ZoneInfo('Asia/Taipei')).date()
if year == str(today.year) or (year == '全部年度' and today.year in years):
    st.info(f'{today.year} 年尚未結束，資料也可能延後公告；不宜直接與完整年度比較。')

st.subheader('歷年裁罰案件')
st.caption('依處分年度歸類，補登舊案歸回原年度。此圖保留所有年度，套用縣市、法條及名稱篩選。')
annual = base.dropna(subset=['處分年度']).groupby('處分年度').size().reset_index(name='案件數')
if not annual.empty:
    annual['年度'] = annual['處分年度'].astype(int).astype(str)
    annual['選取'] = annual['年度'].eq(year) if year != '全部年度' else True
    chart = alt.Chart(annual).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
        x=alt.X('年度:O', title='處分年度', axis=alt.Axis(labelAngle=0)),
        y=alt.Y('案件數:Q', title='裁罰案件數'),
        color=alt.condition(alt.datum['選取'], alt.value('#3975db'), alt.value('#c8d8f1')),
        tooltip=['年度:O', alt.Tooltip('案件數:Q', format=',')]).properties(height=270)
    st.altair_chart(chart, width='stretch')
else:
    st.info('目前條件沒有可繪製的年度資料。')
unknown_dates = int(base['處分年度'].isna().sum())
if unknown_dates:
    st.caption(f'另有 {unknown_dates:,} 件處分日期缺漏或不一致，未納入年度圖；可於全部年度的明細查看。')

left, right = st.columns([1.2, 1])
with left:
    st.subheader('縣市裁罰案件排名')
    st.caption('依公告單位分組；不等同公司所在地。僅列出有收錄案件的縣市。')
    city_rows = filtered[filtered['單位'].isin(CITIES)]
    ranking = city_rows.groupby('單位').size().reset_index(name='案件數')
    if ranking.empty:
        st.info('目前條件沒有縣市案件。')
    else:
        st.altair_chart(alt.Chart(ranking).mark_bar(cornerRadiusEnd=4, color='#3975db').encode(
            y=alt.Y('單位:N', sort='-x', title=None),
            x=alt.X('案件數:Q', title='裁罰案件數'),
            tooltip=['單位:N', alt.Tooltip('案件數:Q', format=',')]
        ).properties(height=max(240, len(ranking) * 25)), width='stretch')
    others = filtered[~filtered['單位'].isin(CITIES)]
    if not others.empty:
        with st.expander(f'其他公告機關 · {len(others):,} 件（未列入縣市排名）'):
            st.dataframe(others.groupby('單位').size().reset_index(name='案件數'), hide_index=True, width='stretch')

with right:
    st.subheader('違規類型占比')
    st.caption('依法條分類；同一案件的同一條計一次。一案可能涉及多條，占比以法條出現次數計算。')
    counts = filtered.explode('條款').groupby('條款').size().sort_values(ascending=False)
    if counts.empty:
        st.info('目前條件沒有違規類型資料。')
    else:
        top = counts.head(5).copy()
        if len(counts) > 5:
            top.loc['其他'] = counts.iloc[5:].sum()
        pie = top.rename_axis('違規類型').reset_index(name='出現次數')
        pie['占比'] = pie['出現次數'] / pie['出現次數'].sum()
        st.altair_chart(alt.Chart(pie).mark_arc(innerRadius=75, outerRadius=125, padAngle=0.025).encode(
            theta=alt.Theta('出現次數:Q'), color=alt.Color('違規類型:N', scale=alt.Scale(scheme='tableau10'), legend=alt.Legend(orient='bottom')),
            tooltip=['違規類型:N', alt.Tooltip('出現次數:Q', format=','), alt.Tooltip('占比:Q', format='.1%')]
        ).properties(height=310), width='stretch')
        st.dataframe(pie, hide_index=True, width='stretch',
                     column_config={'占比': st.column_config.NumberColumn(format='percent')})

st.subheader('裁罰明細')
st.caption(f'符合目前篩選：{len(filtered):,} 件。可在表格欄名排序，或下載完整篩選結果。')
columns = ['單位', '事業單位', '處分日期', '公告日期', '處分字號', '違反法規', '法條敘述', '罰鍰金額', '金額狀態', '備註']
details = filtered.sort_values('處分日期', ascending=False)[columns].copy()
for column in ('處分日期', '公告日期'):
    details[column] = details[column].dt.strftime('%Y/%m/%d').fillna('未提供／不一致')
if details.empty:
    st.info('沒有符合條件的案件，請調整篩選。')
else:
    st.dataframe(details, hide_index=True, width='stretch', height=430,
                 column_config={'罰鍰金額': st.column_config.NumberColumn(format='NT$ %.0f')})
    st.download_button('下載篩選結果 CSV', details.to_csv(index=False).encode('utf-8-sig'),
                       file_name='labor_violations_filtered.csv', mime='text/csv')

with st.expander('資料來源與統計方式'):
    st.markdown('[勞動部公告系統](https://announcement.mol.gov.tw/) · 每日更新排程；實際收錄以目前資料檔為準。')
    st.write(f'原始資料 {info["原始列數"]:,} 列，合併重複處分列 {info["合併列數"]:,} 列。')
    st.write('不同法條不重複計為多件處分。相同處分的金額若不一致，不列入金額總額，請查核明細及原公告。備註可能記載撤銷或更正，統計為收錄紀錄，並非有效處分的法律認定。')
    st.write('未收錄不代表零違規；沒有依縣市企業數或勞檢次數調整。無統編及地址資料，尚不能確認公司更名或同名負責人關聯。')
    st.write('最新公告日期不等於最後同步時間，也不保證各縣市資料完整。')
    if info['略過列數']:
        st.warning(f'另有 {info["略過列數"]} 列格式不完整，未納入統計。')

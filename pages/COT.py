import streamlit as st
import pandas as pd
import requests
import zipfile
import io

st.set_page_config(layout="wide", page_title="COT Positioning")
st.title("COT Gold Positioning")
st.caption("CFTC Commitments of Traders — Managed Money net positions in gold futures")

# ── Load data ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=86400)  # cache for 24 hours since COT is only weekly
def fetch_cot_gold():
    all_data = []
    for year in range(2010, 2027):
        url = f"https://www.cftc.gov/files/dea/history/fut_disagg_txt_{year}.zip"
        try:
            r = requests.get(url, timeout=10)
            with zipfile.ZipFile(io.BytesIO(r.content)) as z:
                fname = z.namelist()[0]
                df = pd.read_csv(z.open(fname), encoding='latin1', low_memory=False)
                gold = df[df['Market_and_Exchange_Names'] == 'GOLD - COMMODITY EXCHANGE INC.']
                all_data.append(gold)
        except:
            pass
    return pd.concat(all_data, ignore_index=True)

with st.spinner("Fetching COT data from CFTC — this may take a minute..."):
    raw = fetch_cot_gold()

df = raw[['Report_Date_as_YYYY-MM-DD',
          'M_Money_Positions_Long_All',
          'M_Money_Positions_Short_All']].copy()

df.columns = ['date', 'long', 'short']
df['date'] = pd.to_datetime(df['date'])
df['net_position'] = df['long'] - df['short']
df = df.sort_values('date').reset_index(drop=True)
df['zscore'] = (df['net_position'] - df['net_position'].mean()) / df['net_position'].std()

net  = df['net_position'].iloc[-1]
z    = df['zscore'].iloc[-1]
date = df['date'].iloc[-1].strftime('%d %b %Y')

# ── Signal ────────────────────────────────────────────────────────────────
z = df['zscore'].iloc[-1]
if z > 2:
    color, border, signal = "#fde8e8", "#e53935", "Crowded long — contrarian bearish, caution"
elif z > 1:
    color, border, signal = "#fff3e0", "#ffa726", "Elevated long — mild caution"
elif z < -2:
    color, border, signal = "#d4edda", "#28a745", "Crowded short — contrarian bullish, strong entry signal"
elif z < -1:
    color, border, signal = "#e8f5e9", "#66bb6a", "Elevated short — mild bullish signal"
else:
    color, border, signal = "#f5f5f5", "#bdbdbd", "Neutral positioning"

# ── Display ───────────────────────────────────────────────────────────────
st.divider()

col1, col2, col3 = st.columns(3)
col1.metric("As of", date)
col2.metric("Net Position (contracts)", f"{net:,.0f}")
col3.metric("Z-Score", f"{z:.2f}")

st.divider()
st.subheader("Signal")
st.markdown(
    f'''<div style="
        background-color:{color};
        padding:14px 16px;
        border-radius:8px;
        color:#1a1a1a;
        font-size:14px;
        border-left: 4px solid {border};
    ">{signal}</div>''',
    unsafe_allow_html=True
)

st.divider()
st.subheader("How to interpret")
st.markdown("""
- **Net position** = managed money longs minus shorts in COMEX gold futures
- **High z-score (+2)** → trade is crowded, contrarian warning — consider trimming or sizing smaller
- **Low z-score (-2)** → everyone has given up on gold, contrarian buy signal
- **Neutral** → positioning not extreme, no crowding risk
- Use this as a **risk check and exit signal**, not an entry signal
""")

st.caption("Data: CFTC Disaggregated COT Report · Updated weekly on Fridays · 2010–present")
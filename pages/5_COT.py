import streamlit as st
from utils import load_cot, signal_box

st.set_page_config(layout="wide", page_title="COT Positioning")
st.title("COT Gold Futures")
st.caption("CFTC Commitments of Traders — Managed Money net positions in gold futures")

with st.spinner("Fetching COT data from CFTC — this may take a minute..."):
    df = load_cot()

net  = df['net_position'].iloc[-1]
z    = df['zscore'].iloc[-1]
date = df['date'].iloc[-1].strftime('%d %b %Y')

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

st.divider()
col1, col2, col3 = st.columns(3)
col1.metric("As of", date)
col2.metric("Net Position (contracts)", f"{net:,.0f}")
col3.metric("Z-Score", f"{z:.2f}")

st.divider()
st.subheader("Signal")
signal_box(signal, color, border)

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
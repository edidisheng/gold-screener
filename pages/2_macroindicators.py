import streamlit as st
from utils import load_macro, zscore, signal_box, get_colors

st.set_page_config(layout="wide", page_title="Macro Indicators")
st.title("Macro Indicators")
st.caption("Real yield, inflation expectations, and USD strength vs gold")

tips, infl, dxy = load_macro()

tips_z = zscore(tips).iloc[-1]
infl_z = zscore(infl).iloc[-1]
dxy_z  = zscore(dxy).iloc[-1]

st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Real Yield (10Y TIPS)")
    st.metric("Current Yield", f"{tips.iloc[-1]:.2f}%")
    st.metric("Z-Score", f"{tips_z:.2f}")
    c, b, t = get_colors(tips_z, bullish_high=False)
    signal_box(t, c, b)

with col2:
    st.subheader("Inflation Expectations (5Y Breakeven)")
    st.metric("Current Rate", f"{infl.iloc[-1]:.2f}%")
    st.metric("Z-Score", f"{infl_z:.2f}")
    c, b, t = get_colors(infl_z, bullish_high=True)
    signal_box(t, c, b)

with col3:
    st.subheader("USD Index (DXY)")
    st.metric("Current Level", f"{dxy.iloc[-1]:.2f}")
    st.metric("Z-Score", f"{dxy_z:.2f}")
    c, b, t = get_colors(dxy_z, bullish_high=False)
    signal_box(t, c, b)

st.divider()
st.caption("Z-scores calculated vs 2003–present history · Data: FRED, Yahoo Finance")
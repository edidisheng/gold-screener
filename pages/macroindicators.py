import streamlit as st
import pandas as pd
import yfinance as yf
from fredapi import Fred

st.set_page_config(layout="wide", page_title="Macro Indicators")
st.title("Macro Indicators")
st.caption("Real yield, inflation expectations, and USD strength vs gold")

# ── Load data ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_data():
    fred = Fred(api_key=st.secrets["FRED_API_KEY"])
    tips  = fred.get_series('DFII10', observation_start='2003-01-01')
    infl  = fred.get_series('T5YIE',  observation_start='2003-01-01')
    dxy   = yf.download('DX-Y.NYB', start='2003-01-01', auto_adjust=True)['Close'].squeeze()
    dxy.index = pd.to_datetime(dxy.index).normalize()
    dxy = dxy.dropna()
    return tips, infl, dxy

# ── Helper ────────────────────────────────────────────────────────────────
def zscore(series):
    return (series - series.mean()) / series.std()

def signal_label(z, bullish_high):
    """bullish_high=True means high z is bullish (inflation), False means bearish (yield, DXY)"""
    if bullish_high:
        if z >= 2:   return "Strong tailwind — very bullish for gold 🟢"
        elif z >= 1: return "Mild tailwind — bullish for gold 🟡"
        elif z <= -2: return "Strong headwind — very bearish for gold 🔴"
        elif z <= -1: return "Mild headwind — bearish for gold 🟠"
        else:        return "Neutral zone ⚪"
    else:
        if z >= 2:   return "Strong headwind — very bearish for gold 🔴"
        elif z >= 1: return "Mild headwind — bearish for gold 🟠"
        elif z <= -2: return "Strong tailwind — very bullish for gold 🟢"
        elif z <= -1: return "Mild tailwind — bullish for gold 🟡"
        else:        return "Neutral zone ⚪"

# ── Calculate ─────────────────────────────────────────────────────────────
tips_z = zscore(tips).iloc[-1]
infl_z = zscore(infl).iloc[-1]
dxy_z = zscore(dxy).iloc[-1]

# ── Display ───────────────────────────────────────────────────────────────
st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Real Yield (10Y TIPS)")
    st.metric("Current Yield", f"{tips.iloc[-1]:.2f}%")
    st.metric("Z-Score", f"{tips_z:.2f}")
    st.info(signal_label(tips_z, bullish_high=False))

with col2:
    st.subheader("Inflation Expectations (5Y Breakeven)")
    st.metric("Current Rate", f"{infl.iloc[-1]:.2f}%")
    st.metric("Z-Score", f"{infl_z:.2f}")
    st.info(signal_label(infl_z, bullish_high=True))

with col3:
    st.subheader("USD Index (DXY)")
    st.metric("Current Level", f"{dxy.iloc[-1]:.2f}")
    st.metric("Z-Score", f"{dxy_z:.2f}")
    st.info(signal_label(dxy_z, bullish_high=False))

st.divider()
st.caption("Z-scores calculated vs 2003–present history · Data: FRED, Yahoo Finance")
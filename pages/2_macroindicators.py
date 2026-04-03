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

def signal_box(z, bullish_high):
    if bullish_high:
        if z >= 2:    color, border, text = "#d4edda", "#28a745", "Strong tailwind — very bullish for gold"
        elif z >= 1:  color, border, text = "#e8f5e9", "#66bb6a", "Mild tailwind — bullish for gold"
        elif z <= -2: color, border, text = "#fde8e8", "#e53935", "Strong headwind — very bearish for gold"
        elif z <= -1: color, border, text = "#fff3e0", "#ffa726", "Mild headwind — bearish for gold"
        else:         color, border, text = "#f5f5f5", "#bdbdbd", "Neutral zone"
    else:
        if z >= 2:    color, border, text = "#fde8e8", "#e53935", "Strong headwind — very bearish for gold"
        elif z >= 1:  color, border, text = "#fff3e0", "#ffa726", "Mild headwind — bearish for gold"
        elif z <= -2: color, border, text = "#d4edda", "#28a745", "Strong tailwind — very bullish for gold"
        elif z <= -1: color, border, text = "#e8f5e9", "#66bb6a", "Mild tailwind — bullish for gold"
        else:         color, border, text = "#f5f5f5", "#bdbdbd", "Neutral zone"

    st.markdown(
        f'''<div style="
            background-color:{color};
            padding:14px 16px;
            border-radius:8px;
            color:#1a1a1a;
            font-size:14px;
            border-left: 4px solid {border};
        ">{text}</div>''',
        unsafe_allow_html=True
    )





# ── Calculate ─────────────────────────────────────────────────────────────
tips, infl, dxy = load_data()  # add this line
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
    signal_box(tips_z, bullish_high=False)

with col2:
    st.subheader("Inflation Expectations (5Y Breakeven)")
    st.metric("Current Rate", f"{infl.iloc[-1]:.2f}%")
    st.metric("Z-Score", f"{infl_z:.2f}")
    signal_box(infl_z, bullish_high=True)

with col3:
    st.subheader("USD Index (DXY)")
    st.metric("Current Level", f"{dxy.iloc[-1]:.2f}")
    st.metric("Z-Score", f"{dxy_z:.2f}")
    signal_box(dxy_z,  bullish_high=False)

st.divider()
st.caption("Z-scores calculated vs 2003–present history · Data: FRED, Yahoo Finance")
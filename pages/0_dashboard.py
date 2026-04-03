import streamlit as st
import pandas as pd
import yfinance as yf
import statsmodels.api as sm
import requests
import zipfile
import io
from fredapi import Fred

# Import all helpers from utils.py
from utils import (
    zscore,
    signal_box,
    get_colors,
    load_macro,
    load_gold,
    load_cot,
    fit_trend
)

st.set_page_config(layout="wide", page_title="Dashboard")
st.title("Gold Investment Dashboard")
st.caption("All signals at a glance")

# ── Load all data ─────────────────────────────────────────────────────────
with st.spinner("Loading all indicators..."):
    tips, infl, dxy     = load_macro()
    df_long             = load_gold('2025-01-01')
    df_short            = load_gold('2025-10-01')
    cot_raw             = load_cot()

# ── Macro calculations ────────────────────────────────────────────────────
tips_z = zscore(tips).iloc[-1]
infl_z = zscore(infl).iloc[-1]
dxy_z  = zscore(dxy).iloc[-1]

# ── Gold trend calculations ───────────────────────────────────────────────
df_long  = fit_trend(df_long)
df_short = fit_trend(df_short)

long_dev  = df_long['deviation'].iloc[-1]
short_dev = df_short['deviation'].iloc[-1]
long_pct  = (long_dev / df_long['trend'].iloc[-1]) * 100
short_pct = (short_dev / df_short['trend'].iloc[-1]) * 100

# ── COT calculations ──────────────────────────────────────────────────────
cot = cot_raw   # cot_raw already contains the processed COT dataframe from utils
cot_z   = cot['zscore'].iloc[-1]
cot_net = cot['net_position'].iloc[-1]

# ── DISPLAY ───────────────────────────────────────────────────────────────
st.divider()

# ── Section 1: Macro Regime ───────────────────────────────────────────────
st.subheader("Macro Regime — Should I be in gold?")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Real Yield (10Y TIPS)**")
    st.metric("Yield", f"{tips.iloc[-1]:.2f}%", f"z={tips_z:.2f}")
    c, b, t = get_colors(tips_z, bullish_high=False)
    signal_box(t, c, b)

with col2:
    st.markdown("**Inflation Expectations (5Y)**")
    st.metric("Rate", f"{infl.iloc[-1]:.2f}%", f"z={infl_z:.2f}")
    c, b, t = get_colors(infl_z, bullish_high=True)
    signal_box(t, c, b)

with col3:
    st.markdown("**USD Index (DXY)**")
    st.metric("Level", f"{dxy.iloc[-1]:.2f}", f"z={dxy_z:.2f}")
    c, b, t = get_colors(dxy_z, bullish_high=False)
    signal_box(t, c, b)

st.divider()

# ── Section 2: Entry Timing ───────────────────────────────────────────────
st.subheader("Entry Timing — When do I buy?")
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Gold Long Term (1 Year)**")
    st.metric("Deviation from Trend", f"A${long_dev:,.2f}", f"{long_pct:+.2f}%")
    if long_dev < 0:
        signal_box("Below trend — favourable entry on long term view", "#e8f5e9", "#66bb6a")
    else:
        signal_box("Above trend — extended on long term view", "#fff3e0", "#ffa726")

with col2:
    st.markdown("**Gold Short Term (90 Days)**")
    st.metric("Deviation from Trend", f"A${short_dev:,.2f}", f"{short_pct:+.2f}%")
    if short_dev < 0:
        signal_box("Below trend — good entry point", "#d4edda", "#28a745")
    else:
        signal_box("Above trend — wait for pullback", "#fde8e8", "#e53935")

st.divider()

# ── Section 3: Risk Check ─────────────────────────────────────────────────
st.subheader("Risk Check — Is the trade crowded?")
col1, col2 = st.columns(2)

with col1:
    st.markdown("**COT Positioning (Managed Money)**")
    st.metric("Net Position", f"{cot_net:,.0f} contracts", f"z={cot_z:.2f}")
    if cot_z > 2:
        signal_box("Crowded long — contrarian warning, consider sizing smaller", "#fde8e8", "#e53935")
    elif cot_z > 1:
        signal_box("Elevated long — mild caution", "#fff3e0", "#ffa726")
    elif cot_z < -2:
        signal_box("Crowded short — contrarian buy signal", "#d4edda", "#28a745")
    elif cot_z < -1:
        signal_box("Elevated short — mild bullish signal", "#e8f5e9", "#66bb6a")
    else:
        signal_box("Neutral positioning — no crowding risk", "#f5f5f5", "#bdbdbd")

with col2:
    st.markdown("**EV Screener**")
    st.info("See the EV Screener page for individual stock signals")

st.divider()
st.caption("All data fetched live · Gold prices in AUD · Updated on page load")
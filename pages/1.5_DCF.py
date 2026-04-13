import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(layout="wide", page_title="DCF Valuation")
st.title("DCF Valuation")
st.caption("Discounted cash flow estimates for selected ASX gold producers")

# ── Live price ────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def get_price(ticker):
    try:
        return yf.Ticker(ticker + ".AX").fast_info["last_price"]
    except:
        return None

# ── Add your companies here ───────────────────────────────────────────────
dcf_data = [
    {
        "ticker":                "WGX",
        "name":                  "Westgold Resources",
        "dcf_value":             11.7,
        "discount_rate":         0.09,
        "gold_price_assumption": 6000,
        "notes":                 "Used 3 Year management projections"
    },
    # add more companies below in the same format
]

df = pd.DataFrame(dcf_data)

# ── Fetch live prices ─────────────────────────────────────────────────────
with st.spinner("Fetching live prices..."):
    df['current_price'] = df['ticker'].apply(get_price)

df = df.dropna(subset=['current_price'])

# ── Calculate upside ──────────────────────────────────────────────────────
df['upside_pct'] = ((df['dcf_value'] - df['current_price']) / df['current_price']) * 100

def signal(upside):
    if upside > 20:
        return "Undervalued ✅"
    elif upside < -20:
        return "Overvalued 🚩"
    else:
        return "Fair Value ⚠️"

df['signal'] = df['upside_pct'].apply(signal)
df = df.sort_values('upside_pct', ascending=False).reset_index(drop=True)

# ── Summary metrics ───────────────────────────────────────────────────────
undervalued = len(df[df['signal'] == "Undervalued ✅"])
fair        = len(df[df['signal'] == "Fair Value ⚠️"])
overvalued  = len(df[df['signal'] == "Overvalued 🚩"])

col1, col2, col3 = st.columns(3)
col1.metric("Undervalued", undervalued)
col2.metric("Fair Value",  fair)
col3.metric("Overvalued",  overvalued)

st.divider()

# ── Display table ─────────────────────────────────────────────────────────
display = df[[
    'ticker', 'name', 'current_price', 'dcf_value',
    'upside_pct', 'discount_rate', 'gold_price_assumption', 'signal', 'notes'
]].copy()

display['current_price']         = display['current_price'].map("A${:.2f}".format)
display['dcf_value']             = display['dcf_value'].map("A${:.2f}".format)
display['upside_pct']            = display['upside_pct'].map("{:+.1f}%".format)
display['discount_rate']         = display['discount_rate'].map("{:.1f}%".format)
display['gold_price_assumption'] = display['gold_price_assumption'].map("US${:,.0f}/oz".format)

display.columns = [
    'Ticker', 'Name', 'Current Price', 'DCF Value',
    'Upside/Downside', 'WACC', 'Gold Price Assumption', 'Signal', 'Notes'
]

st.dataframe(display, use_container_width=True, hide_index=True)



st.caption("Current prices fetched live from Yahoo Finance · DCF values manually maintained")
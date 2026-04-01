import streamlit as st

st.set_page_config(layout="wide", page_title="Gold Investment Framework")

st.title("Gold Investment Framework")
st.caption("A technical and trend-based framework for timing gold stock entries")

st.divider()

# ── Your intro message ────────────────────────────────────────────────────
st.markdown("""
Hello! There are two graphs, **Goldlong** which is a polynomial squared regression over a year of gold prices. **Goldshort** is the same except done on a 90 day timeframe.

The purpose of the 1 year regression is to analyse the structural trend of gold and whether to be in it at all. The biggest deviation week section is meant to be a reference for the user to search up what happened geopolitically in the news that week to see what caused the deviation. The 90 day graph is simply to determine the best time of entry when buying gold stocks on the ASX.
            
The **evscreener** is to identify discounted EV/oz gold producers but currently is innacurate due to the dataset being extremely limited and under construction. The planned strategy is to build a portfolio of every single discounted gold producer in the market, purchase them at the **IDEAL BUY SIGNAL**, and hold for a few months under the assumption that on average discounted gold stocks have higher returns than those that arent. This stems from two smaller assumptions, that a gold price rally will have a higher effect on discounted stocks and that these discounted stocks are possibly mispriced (undervalued)
            
Note that although the original model code for graphs and ev screening was done largely manually, this streamlit port is assisted heavily by AI and made mainly for accessibility reasons. 

Thanks! Edison Duong
""")



st.subheader("Ideal Buy Signal")
st.success("Long term trend is UP and price is below trend  +  Short term price is below the 90 day trend → Strong entry point")
st.warning("If the models disagree, exercise caution and wait for confirmation")

st.divider()

st.caption("Built with yfinance, statsmodels, plotly and streamlit. Last updated 1st April 2026")
import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(layout="wide", page_title="ASX Gold Screener")
st.title("ASX Gold Screener")
st.caption("EV/oz valuation screener with grade and jurisdiction adjustments")

# ── Hardcoded benchmarks ──────────────────────────────────────────────────
peer_ev_per_oz_producer  = 542
peer_ev_per_oz_developer = 139
peer_ev_per_oz_explorer  = 40

GRADE_ADJUSTMENTS = [
    {"max_gt": 0.6,  "adjustment": -0.40},
    {"max_gt": 1,    "adjustment": -0.20},
    {"max_gt": 2,    "adjustment":  0.00},
    {"max_gt": 3.5,  "adjustment": +0.20},
    {"max_gt": 6,    "adjustment": -0.40},
    {"max_gt": 9999, "adjustment": -0.60},
]

jurisdiction_discounts = {1: 0, 2: 0.15, 3: 0.35, 4: 0.55}

# ── Load CSV ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_companies():
    return pd.read_csv("golddataset.csv")

# ── Live prices ───────────────────────────────────────────────────────────
def get_price(ticker):
    try:
        return yf.Ticker(ticker + ".AX").fast_info["last_price"]
    except:
        return None

# ── Helper functions ──────────────────────────────────────────────────────
def get_grade_adjustment(grade_gt):
    for band in GRADE_ADJUSTMENTS:
        if grade_gt <= band["max_gt"]:
            return band["adjustment"]
    return GRADE_ADJUSTMENTS[-1]["adjustment"]

def get_peer_benchmark(stage):
    if stage == "producer":
        return peer_ev_per_oz_producer
    elif stage == "developer":
        return peer_ev_per_oz_developer
    else:
        return peer_ev_per_oz_explorer

# ── Main calculation ──────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def run_screener():
    df = load_companies()
    results = []

    for i, row in df.iterrows():
        price = get_price(row["ticker"])
        if price is None:
            continue
        market_cap = price * row["shares_total"]
        ev         = market_cap - row["cash_aud"] + row["debt_total"]
        ev_oz      = ev / (row["resource_moz"] * 1_000_000)
        results.append({
            "ticker":            row["ticker"],
            "name":              row["name"],
            "stage":             row["stage"],
            "price":             price,
            "market_cap":        market_cap,
            "ev":                ev,
            "resource_moz":      row["resource_moz"],
            "grade_gt":          row["grade_gt"],
            "jurisdiction_tier": row["jurisdiction_tier"],
            "ev_oz":             ev_oz,
        })

    results_df = pd.DataFrame(results)

    # grade and jurisdiction adjustments
    for i, row in results_df.iterrows():
        jur_discount = jurisdiction_discounts[row["jurisdiction_tier"]]
        peers = results_df[
            (results_df["stage"] == row["stage"]) &
            (results_df["ticker"] != row["ticker"])
        ]["ev_oz"]
        base_peer = peers.mean() if len(peers) > 0 else get_peer_benchmark(row["stage"])
        grade_adj = 0.0 if row["stage"] == "producer" else get_grade_adjustment(row["grade_gt"])
        adj_peer  = base_peer * (1 + grade_adj) * (1 - jur_discount)
        results_df.at[i, "grade_adj"]      = grade_adj
        results_df.at[i, "jur_discount"]   = jur_discount
        results_df.at[i, "adj_peer_ev_oz"] = adj_peer

    # signals
    for i, row in results_df.iterrows():
        discount_pct = ((row["adj_peer_ev_oz"] - row["ev_oz"]) / row["adj_peer_ev_oz"]) * 100
        if discount_pct > 20:
            signal = "CHEAP ✅"
        elif discount_pct < -20:
            signal = "RICH 🚩"
        else:
            signal = "FAIR ⚠️"
        results_df.at[i, "discount_pct"] = discount_pct
        results_df.at[i, "signal"]       = signal

    return results_df.sort_values("discount_pct", ascending=False).reset_index(drop=True)

# ── Run and display ───────────────────────────────────────────────────────
with st.spinner("Fetching live prices and calculating..."):
    results_df = run_screener()

# summary metrics
cheap = len(results_df[results_df["signal"] == "CHEAP ✅"])
fair  = len(results_df[results_df["signal"] == "FAIR ⚠️"])
rich  = len(results_df[results_df["signal"] == "RICH 🚩"])

col1, col2, col3 = st.columns(3)
col1.metric("Cheap", cheap)
col2.metric("Fair",  fair)
col3.metric("Rich",  rich)

st.divider()

# filter by stage
stages = ["All"] + sorted(results_df["stage"].unique().tolist())
selected_stage = st.selectbox("Filter by stage", stages)
if selected_stage != "All":
    display_df = results_df[results_df["stage"] == selected_stage]
else:
    display_df = results_df

# format display columns
display = display_df[[
    "ticker", "name", "stage", "price", "market_cap",
    "ev", "resource_moz", "grade_gt", "ev_oz", "adj_peer_ev_oz", "discount_pct", "signal"
]].copy()

display["price"]        = display["price"].map("A${:.2f}".format)
display["market_cap"] = (display["market_cap"] / 1e9).map("A${:.2f}B".format)
display["ev"]         = (display["ev"] / 1e9).map("A${:.2f}B".format)
display["ev_oz"]        = display["ev_oz"].map("A${:.0f}/oz".format)
display["adj_peer_ev_oz"] = display["adj_peer_ev_oz"].map("A${:.0f}/oz".format)
display["discount_pct"] = display["discount_pct"].map("{:+.1f}%".format)

display.columns = [
    "Ticker", "Name", "Stage", "Price", "Mkt Cap (M)",
    "EV (M)", "Resource (Moz)", "Grade (g/t)", "EV/oz", "Peer EV/oz", "Discount", "Signal"
]

st.dataframe(display, use_container_width=True, hide_index=True)

st.caption("Prices fetched live from Yahoo Finance · Ranked by discount to peers")
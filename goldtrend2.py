#!/usr/bin/env python3
"""
Gold Trend Filter – Use to determine if gold is in a significant uptrend/downtrend
before buying gold stocks for a 3–6 month hold.

Usage examples:
    python gold_trend_filter.py                # 200-day lookback, alpha=0.10
    python gold_trend_filter.py --days 120     # 120-day lookback
    python gold_trend_filter.py --alpha 0.05   # stricter significance level
    python gold_trend_filter.py --raw          # use raw prices instead of log
"""

import argparse
import warnings
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
from scipy import stats

# Suppress harmless urllib3 LibreSSL warning on macOS (optional)
warnings.filterwarnings("ignore", category=UserWarning, module="urllib3")

def get_trend_signal(data, alpha=0.10, use_log=True):
    """
    Perform linear regression: price ~ time.
    Returns slope, p-value, R², and a signal string.
    """
    if len(data) < 5:
        return None, None, None, "Insufficient data points."

    # Use closing prices, ensure 1D array
    prices = data['Close'].values.squeeze()
    if use_log:
        # Log transform to linearize exponential growth
        prices = np.log(prices)

    time_idx = np.arange(len(prices))
    slope, intercept, r_value, p_value, std_err = stats.linregress(time_idx, prices)
    r_squared = r_value ** 2

    # Determine signal based on slope and p-value
    if p_value < alpha:
        if slope > 0:
            signal = "BUY"
        else:
            signal = "AVOID"
    else:
        signal = "NEUTRAL"

    return slope, p_value, r_squared, signal

def main():
    parser = argparse.ArgumentParser(
        description="Gold trend detection for multi‑month investment decisions."
    )
    parser.add_argument("--days", type=int, default=200,
                        help="Lookback period in days (default: 200)")
    parser.add_argument("--alpha", type=float, default=0.10,
                        help="Significance level for trend detection (default: 0.10)")
    parser.add_argument("--raw", action="store_true",
                        help="Use raw prices instead of log prices (not recommended)")
    args = parser.parse_args()

    print(f"Fetching gold data (last {args.days} days)...")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=args.days)

    # Download daily data
    data = yf.download("GC=F", start=start_date, end=end_date,
                       interval="1d", progress=False)

    if data.empty:
        print("No data retrieved. Check your internet connection.")
        return

    # Extract current and start prices as floats
    current_price = float(data['Close'].values[-1])
    start_price = float(data['Close'].values[0])

    price_change = current_price - start_price
    pct_change = (price_change / start_price) * 100

    print("\n" + "="*60)
    print(f"Gold Price Analysis – {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    print(f"Current Price:        ${current_price:.2f}")
    print(f"Price {args.days} days ago:  ${start_price:.2f}")
    print(f"Change:               ${price_change:.2f} ({pct_change:.2f}%)")
    print(f"Data points used:      {len(data)} days")

    # Get trend and signal
    slope, p_val, r2, signal = get_trend_signal(data, alpha=args.alpha, use_log=not args.raw)

    print(f"\nLinear Regression (Price ~ Time):")
    if not args.raw:
        # Convert log-slope to approximate % per day for interpretation
        pct_per_day = (np.exp(slope) - 1) * 100
        print(f"  Daily growth rate:   {pct_per_day:.3f}% per day (log slope = {slope:.6f})")
    else:
        print(f"  Daily slope:         ${slope:.4f} per day")
    print(f"  R-squared:           {r2:.4f}")
    print(f"  p-value:             {p_val:.6f}")
    print(f"  Significance level:  α = {args.alpha}")

    # Output recommendation
    print("\n" + "="*60)
    if signal == "BUY":
        print(f"📈 SIGNAL: {signal} – Gold is in a significant uptrend.")
        print("   Suitable for buying gold stocks with a multi‑month horizon.")
    elif signal == "AVOID":
        print(f"📉 SIGNAL: {signal} – Gold is in a significant downtrend.")
        print("   Avoid buying; consider waiting for trend reversal.")
    else:
        print(f"⚖️  SIGNAL: {signal} – No statistically significant trend.")
        print("   Gold is range‑bound or trending weakly. Proceed with caution.")
    print("="*60)

if __name__ == "__main__":
    main()
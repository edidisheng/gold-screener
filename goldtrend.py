import yfinance as yf
import pandas as pd
import numpy as np
from pathlib import Path
import statsmodels.api as sm
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# ── Config ───────────────────────────────────────────────────────────────
DATA_FILE     = "gold_daily.csv"
TICKER        = "GC=F"
FX_TICKER     = "AUDUSD=X"
WINDOW_DAYS   = 90
POLY_DEGREE   = 2
# ─────────────────────────────────────────────────────────────────────────


def fetch_and_append():
    """Download recent gold and AUD/USD data, append to local CSV."""

    # Gold price
    df = yf.download(TICKER, period="6mo", interval="1d", auto_adjust=True)
    df = df[["Close"]]
    df.columns = ["price"]
    df.index = pd.to_datetime(df.index).tz_localize(None)
    df.index.name = "date"
    df = df[df.index.dayofweek < 5]

    # AUD/USD rate
    fx = yf.download(FX_TICKER, period="6mo", interval="1d", auto_adjust=True)
    fx = fx[["Close"]]
    fx.columns = ["audusd"]
    fx.index = pd.to_datetime(fx.index).tz_localize(None)
    fx.index.name = "date"
    fx = fx[fx.index.dayofweek < 5]

    # Flatten any multi-level columns yfinance may have added
    df.columns = df.columns.get_level_values(0) if hasattr(df.columns, "levels") else df.columns
    fx.columns = fx.columns.get_level_values(0) if hasattr(fx.columns, "levels") else fx.columns

    # Merge and convert to AUD
    df = df.join(fx, how="left")
    df["audusd"] = df["audusd"].ffill()
    df["price_aud"] = df["price"] / df["audusd"]

    if Path(DATA_FILE).exists():
        try:
            existing = pd.read_csv(DATA_FILE, index_col="date", parse_dates=True)
            df = pd.concat([existing, df])
            df = df[~df.index.duplicated(keep="last")]
        except Exception:
            pass

    df.sort_index(inplace=True)
    df.to_csv(DATA_FILE)
    return df

def fit_trend(prices: pd.Series, degree: int = POLY_DEGREE):
    """
    Fit polynomial regression using statsmodels.
    Returns model, X index, scaled X, and fitted values.
    """
    X = np.arange(len(prices)).astype(float)
    X_scaled = (X - X.mean()) / X.std()

    # Build polynomial features
    poly_cols = [X_scaled ** i for i in range(1, degree + 1)]
    X_poly = np.column_stack(poly_cols)
    X_poly = sm.add_constant(X_poly)

    model = sm.OLS(prices.values, X_poly).fit()
    return model, X, X_scaled, model.fittedvalues


def compute_slope(X_scaled, model, degree: int = POLY_DEGREE):
    """Slope at today via finite difference on the scaled index."""
    def predict_at(i):
        x = np.array([X_scaled[i] ** d for d in range(1, degree + 1)])
        x = np.concatenate([[1], x])
        return model.params @ x

    return predict_at(-1) - predict_at(-2)


def analyse():
    print(f"\n{'='*50}")
    print(f"  Gold trend analysis  —  {datetime.today().strftime('%d %b %Y')}")
    print(f"{'='*50}")

    # 1. Load data
    df = fetch_and_append()
    df = df.asfreq("B").ffill()

    if len(df) < WINDOW_DAYS:
        print(f"Not enough data yet ({len(df)} days). Need {WINDOW_DAYS}.")
        return

    # 2. Rolling window — use AUD price
    window     = df["price_aud"].iloc[-WINDOW_DAYS:].copy()
    window_usd = df["price"].iloc[-WINDOW_DAYS:].copy()
    audusd_now = df["audusd"].iloc[-1]

    # 3. Fit trend
    model, X, X_scaled, fitted = fit_trend(window)
    fitted_series = pd.Series(fitted, index=window.index)

    # 4. Slope
    slope_per_day   = compute_slope(X_scaled, model)
    slope_per_month = slope_per_day * 21

    # 5. Residual
    latest_price   = window.iloc[-1]
    latest_fitted  = fitted_series.iloc[-1]
    residual       = latest_price - latest_fitted
    residual_pct   = (residual / latest_fitted) * 100

    # 6. R² and p-value
    r_squared = model.rsquared
    p_trend   = model.pvalues[1]  # p-value on the linear term

    # 7. Trend direction
    if slope_per_day > 0.5:
        direction       = "UP"
        direction_emoji = "↑"
    elif slope_per_day < -0.5:
        direction       = "DOWN"
        direction_emoji = "↓"
    else:
        direction       = "FLAT"
        direction_emoji = "→"

    # 8. Deviation label
    if residual_pct > 2:
        deviation_label = "above trend (extended)"
    elif residual_pct < -2:
        deviation_label = "below trend (discounted)"
    else:
        deviation_label = "near trend (neutral)"

    # ── Print summary ─────────────────────────────────────────────────
    print(f"\n  AUD/USD rate    : {audusd_now:.4f}")
    print(f"\n Lookback Period : {WINDOW_DAYS:.4f}")
    print(f"\n  Current price   : A${latest_price:,.2f}")
    print(f"  USD equivalent  : US${window_usd.iloc[-1]:,.2f}")
    print(f"  Trend (fitted)  : A${latest_fitted:,.2f}")
    print(f"\n  Direction       : {direction_emoji}  {direction}")
    print(f"  Slope           : A${slope_per_day:+.2f}/day  "
          f"(A${slope_per_month:+.2f}/month)")
    print(f"\n  Deviation       : A${residual:+.2f}  "
          f"({residual_pct:+.2f}%)  →  {deviation_label}")
    print(f"\n  R²              : {r_squared:.4f}")
    print(f"  P-value (trend) : {p_trend:.4f}", end="  →  ")
    if p_trend < 0.05:
        print("statistically significant")
    else:
        print("not statistically significant (trend may be noise)")
    print()

    # ── Signal ────────────────────────────────────────────────────────
    if direction == "UP" and residual_pct < 2:
        print("  Signal: Uptrend, price near or below trend → favourable")
    elif direction == "UP" and residual_pct >= 2:
        print("  Signal: Uptrend, but price extended above trend → wait for pullback")
    elif direction == "DOWN":
        print("  Signal: Downtrend → wait before buying gold stocks")
    else:
        print("  Signal: No clear trend → neutral, watch closely")

    print(f"\n{'='*50}\n")

    # ── Plot ──────────────────────────────────────────────────────────
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 7),
                                    gridspec_kw={"height_ratios": [3, 1]})
    fig.suptitle("Gold price — medium-term trend (AUD)", fontsize=14)

    ax1.plot(window.index, window.values,
             label="Daily close (AUD)", color="#d4a017", alpha=0.85, linewidth=1.5)
    ax1.plot(fitted_series.index, fitted_series.values,
             label=f"Poly trend (deg {POLY_DEGREE})", color="#333",
             linewidth=2, linestyle="--")
    ax1.axhline(latest_fitted, color="gray", linewidth=0.7, linestyle=":")
    ax1.set_ylabel("Price (AUD)")
    ax1.legend()
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b '%y"))
    ax1.grid(True, alpha=0.3)

    residuals = window.values - fitted
    colors = ["#c0392b" if r < 0 else "#27ae60" for r in residuals]
    ax2.bar(window.index, residuals, color=colors, width=1.2, alpha=0.7)
    ax2.axhline(0, color="black", linewidth=0.8)
    ax2.set_ylabel("Deviation (AUD)")
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%b '%y"))
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("gold_trend.png", dpi=150)
    plt.show()
    print("  Chart saved → gold_trend.png")


if __name__ == "__main__":
    analyse()

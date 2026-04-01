import streamlit as st
import pandas as pd
import statsmodels.api as sm
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(layout="wide", page_title="Gold Trend Model 1 Year")
st.title("Gold Trend Model (AUD)")
st.caption("Polynomial trend regression on gold price vs AUD")

@st.cache_data(ttl=3600)
def load_data():
    gold   = yf.download('GC=F', start='2025-01-01', auto_adjust=True)['Close'].squeeze()
    audusd = yf.download('AUDUSD=X', start='2025-01-01', auto_adjust=True)['Close'].squeeze()
    df = pd.DataFrame({'gp': gold, 'audusd': audusd})
    df['gp_aud'] = df['gp'] / df['audusd']
    df = df.dropna()
    df['t']  = range(len(df))
    df['t2'] = df['t'] ** 2
    return df

df = load_data()

X = sm.add_constant(df[['t', 't2']])
y = df['gp_aud']
model = sm.OLS(y, X).fit()
df['trend']     = model.fittedvalues
df['deviation'] = df['gp_aud'] - df['trend']

current   = df['gp_aud'].iloc[-1]
trend_val = df['trend'].iloc[-1]
dev_val   = df['deviation'].iloc[-1]
dev_pct   = (dev_val / trend_val) * 100

col1, col2, col3 = st.columns(3)
col1.metric("Current Price (AUD)", f"${current:,.2f}")
col2.metric("Trend Value (AUD)",   f"${trend_val:,.2f}")
col3.metric("Deviation",           f"${dev_val:,.2f}", f"{dev_pct:+.2f}%")

if dev_val < 0:
    st.success("Signal: BUY — price is below trend")
else:
    st.warning("Signal: TAKE CAUTION — price is above trend")

fig = make_subplots(rows=2, cols=1, shared_xaxes=False,
                    row_heights=[0.75, 0.25],
                    vertical_spacing=0.08,
                    subplot_titles=("Gold Price vs Trend (AUD)", "Deviation from Trend (AUD)"))

# main price chart — matching the gold colour and style from the other model
fig.add_trace(go.Scatter(
    x=df.index, y=df['gp_aud'],
    name='Daily Close (AUD)',
    line=dict(color='#d4a017', width=1.5),
    opacity=0.85
), row=1, col=1)

fig.add_trace(go.Scatter(
    x=df.index, y=df['trend'],
    name='Poly Trend',
    line=dict(color='#cccccc', dash='dash', width=2)
), row=1, col=1)

# horizontal line at latest trend value — matching ax1.axhline
fig.add_hline(y=trend_val, line=dict(color='gray', width=0.7, dash='dot'), row=1, col=1)

# residual bar chart — matching the red/green colours from the other model
fig.add_trace(go.Bar(
    x=df.index, y=df['deviation'],
    name='Deviation',
    showlegend=False,
    marker_color=['#27ae60' if x > 0 else '#c0392b' for x in df['deviation']],
    opacity=0.7
), row=2, col=1)

# zero line on residual chart — matching ax2.axhline(0)
fig.add_hline(y=0, line=dict(color='white', width=0.8), row=2, col=1)

fig.update_layout(
    height=800,
    template='plotly_dark',
    showlegend=True,
    paper_bgcolor='#111111',
    plot_bgcolor='#111111',
    font=dict(color='white', size=13),
    margin=dict(l=60, r=40, t=60, b=40),
    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
)

# gridlines matching ax1.grid(True, alpha=0.3)
fig.update_xaxes(showgrid=True, gridcolor='rgba(255,255,255,0.15)', tickformat="%b '%y")
fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.15)')

fig.update_yaxes(title_text="Price (AUD)", row=1, col=1)
fig.update_yaxes(title_text="Deviation (AUD)", row=2, col=1)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Biggest Deviation Weeks")
key_dates = df['deviation'].abs().resample('W').max().sort_values(ascending=False).head(5)
st.dataframe(key_dates.rename("Deviation (AUD)").reset_index(), use_container_width=True)
# utils.py — save in repo root alongside goldapp.py

import pandas as pd
import yfinance as yf
import requests
import zipfile
import io
import streamlit as st
from fredapi import Fred
import statsmodels.api as sm


def zscore(series):
    return (series - series.mean()) / series.std()


def signal_box(text, color, border):
    st.markdown(
        f'''<div style="
            background-color:{color};
            padding:12px 14px;
            border-radius:8px;
            color:#1a1a1a;
            font-size:13px;
            border-left: 4px solid {border};
            margin-top:4px;
        ">{text}</div>''',
        unsafe_allow_html=True
    )


def get_colors(z, bullish_high):
    if bullish_high:
        if z >= 2:    return "#d4edda", "#28a745", "Strong tailwind — very bullish"
        elif z >= 1:  return "#e8f5e9", "#66bb6a", "Mild tailwind — bullish"
        elif z <= -2: return "#fde8e8", "#e53935", "Strong headwind — very bearish"
        elif z <= -1: return "#fff3e0", "#ffa726", "Mild headwind — bearish"
        else:         return "#f5f5f5", "#bdbdbd", "Neutral"
    else:
        if z >= 2:    return "#fde8e8", "#e53935", "Strong headwind — very bearish"
        elif z >= 1:  return "#fff3e0", "#ffa726", "Mild headwind — bearish"
        elif z <= -2: return "#d4edda", "#28a745", "Strong tailwind — very bullish"
        elif z <= -1: return "#e8f5e9", "#66bb6a", "Mild tailwind — bullish"
        else:         return "#f5f5f5", "#bdbdbd", "Neutral"


@st.cache_data(ttl=3600)
def load_macro():
    fred  = Fred(api_key=st.secrets["FRED_API_KEY"])
    tips  = fred.get_series('DFII10', observation_start='2003-01-01')
    infl  = fred.get_series('T5YIE',  observation_start='2003-01-01')
    dxy   = yf.download('DX-Y.NYB', start='2003-01-01', auto_adjust=True)['Close'].squeeze()
    dxy.index = pd.to_datetime(dxy.index).normalize()
    return tips, infl, dxy.dropna()


@st.cache_data(ttl=3600)
def load_gold(start):
    gold   = yf.download('GC=F', start=start, auto_adjust=True)['Close'].squeeze()
    audusd = yf.download('AUDUSD=X', start=start, auto_adjust=True)['Close'].squeeze()
    gold.index   = pd.to_datetime(gold.index).normalize()
    audusd.index = pd.to_datetime(audusd.index).normalize()
    df = pd.DataFrame({'gp': gold, 'audusd': audusd})
    df['gp_aud'] = df['gp'] / df['audusd']
    df = df.dropna()
    df['t']  = range(len(df))
    df['t2'] = df['t'] ** 2
    return df


@st.cache_data(ttl=86400)
def load_cot():
    all_data = []
    for year in range(2010, 2027):
        url = f"https://www.cftc.gov/files/dea/history/fut_disagg_txt_{year}.zip"
        try:
            r = requests.get(url, timeout=10)
            with zipfile.ZipFile(io.BytesIO(r.content)) as z:
                fname = z.namelist()[0]
                df = pd.read_csv(z.open(fname), encoding='latin1', low_memory=False)
                gold = df[df['Market_and_Exchange_Names'] == 'GOLD - COMMODITY EXCHANGE INC.']
                all_data.append(gold)
        except:
            pass
    raw = pd.concat(all_data, ignore_index=True)
    df = raw[['Report_Date_as_YYYY-MM-DD',
              'M_Money_Positions_Long_All',
              'M_Money_Positions_Short_All']].copy()
    df.columns = ['date', 'long', 'short']
    df['date'] = pd.to_datetime(df['date'])
    df['net_position'] = df['long'] - df['short']
    df = df.sort_values('date').reset_index(drop=True)
    df['zscore'] = zscore(df['net_position'])
    return df


def fit_trend(df):
    X = sm.add_constant(df[['t', 't2']])
    model = sm.OLS(df['gp_aud'], X).fit()
    df = df.copy()
    df['trend']     = model.fittedvalues
    df['deviation'] = df['gp_aud'] - df['trend']
    return df
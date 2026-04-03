from fredapi import Fred
import pandas as pd
import yfinance as yf 


# Initialize API
fred = Fred(api_key='8a6e3189e98d5e2ef8d874f86116861d')

series_id1 = 'T5YIE'
series_id2 = 'DFII10'

# Fetch the data
# You can specify observation_start and end dates as needed
inflation_data = fred.get_series(series_id1, observation_start='2003-01-01')
dollarindex = yf.download('DX-Y.NYB', start = '2003-01-01', auto_adjust=True)['Close'].squeeze()
tips_yield_data = fred.get_series(series_id2, observation_start='2003-01-01')

## REAL YIELD BLOCK

df = pd.DataFrame({
    'yield' : tips_yield_data
})
df['zscore'] = (df['yield'] - df['yield'].mean()) / df['yield'].std()
print("--- Real Yield ---")
print(f" Current z score : {df['zscore'].iloc[-1]:,.2f}")
print(f" Current yield : {df['yield'].iloc[-1]:,.2f}")

def results():
    z = df['zscore'].iloc[-1]
    if -1 <= z <= 1:
        print("neutral zone")
    elif 1 < z < 2:
        print("mild headwind, bearish on gold")
    elif -2 < z < -1:
        print("mild tailwind, bullish on gold")
    elif z >= 2:
        print("strong headwind, very bearish on gold")
    elif z <= -2:
        print("strong tailwind, very bullish on gold")
results()

##INFLATION BLOCK
df = pd.DataFrame({
    'inflation' : inflation_data
})

df['zscore2'] = (df['inflation'] - df['inflation'].mean()) / df['inflation'].std()
print("--- Inflation ---")
print(f" Current z score : {df['zscore2'].iloc[-1]:,.2f}")
print(f" 5 year breakeven inflation rate : {df['inflation'].iloc[-1]:,.2f}")

def results():
    z = df['zscore2'].iloc[-1]
    if -1 <= z <= 1:
        print("neutral zone")
    elif 1 < z < 2:
        print("mild tailwind, bullish on gold")
    elif -2 < z < -1:
        print("mild headwind, bearish on gold")
    elif z >= 2:
        print("strong tailwind, very bullish on gold")
    elif z <= -2:
        print("strong headwind, very bearish on gold")
results()

##DOLLAR INDEX BLOCK
df = pd.DataFrame({
    'DI' : dollarindex,
    
    })

df['zscore3'] = (df['DI'] - df['DI'].mean()) / df['DI'].std()

print("--- Dollarindex ---")

print(f" Current Dollar index : {df['DI'].iloc[-1]:,.2f}")

print(f" Current z score : {df['zscore3'].iloc[-1]:,.2f}")


def results():
    z = df['zscore3'].iloc[-1]
    if -1 <= z <= 1:
        print("neutral zone")
    elif 1 < z < 2:
        print("mild headwind, bearish on gold")
    elif -2 < z < -1:
        print("mild tailwind, bullish on gold")
    elif z >= 2:
        print("strong headwind, very bearish on gold")
    elif z <= -2:
        print("strong tailwind, very bullish on gold")
results()
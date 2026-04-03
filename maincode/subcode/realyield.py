from fredapi import Fred
import pandas as pd
import yfinance as yf 


# Initialize API
fred = Fred(api_key='8a6e3189e98d5e2ef8d874f86116861d')

series_id = 'DFII10'

# Fetch the data
# You can specify observation_start and end dates as needed
tips_yield_data = fred.get_series(series_id, observation_start='2003-01-01')



df = pd.DataFrame({
    'yield' : tips_yield_data
})

df['zscore'] = (df['yield'] - df['yield'].mean()) / df['yield'].std()

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

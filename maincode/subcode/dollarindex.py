import pandas as pd 
import yfinance as yf 

dollarindex = yf.download('DX-Y.NYB', start = '2003-01-01', auto_adjust=True)['Close'].squeeze()

##['Close'].squeeze() 

df = pd.DataFrame({
    'DI' : dollarindex,
    
    })

df['zscore'] = (df['DI'] - df['DI'].mean()) / df['DI'].std()

print(f" Current Dollar index : {df['DI'].iloc[-1]:,.2f}")

print(f" Current z score : {df['zscore'].iloc[-1]:,.2f}")


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
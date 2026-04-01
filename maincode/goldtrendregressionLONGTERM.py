import pandas as pd 
import statsmodels.api as sm
import yfinance as yf 
import matplotlib.pyplot as plt

gold_price = yf.download('GC=F', start = '2025-01-01', auto_adjust=True)['Close'].squeeze()
AUD_USDconversion = yf.download('AUDUSD=X', start = '2025-01-01', auto_adjust=True)['Close'].squeeze()
##['Close'].squeeze() 

df = pd.DataFrame({
    'gp' : gold_price,
    'audusd': AUD_USDconversion
    })

##CONVERSION TO AUD
df['gp_aud'] = df['gp'] / df['audusd']
df = df.dropna() ##some zeroes because of different trading days

##time index IMPORTANT THAT THIS IS AFTER DROPNA
df['t']= range(len(df))
df['t2']= df['t']**2

X = sm.add_constant(df[['t', 't2']])
y = df['gp_aud']
model = sm.OLS(y,X).fit()

print (model.summary())

df['trend'] = model.fittedvalues
df['deviation'] = df['gp_aud'] - df['trend']

print(f"Current value AUD : ${df['gp_aud'].iloc[-1]:,.2f}")
print(f"Trend : ${df['trend'].iloc[-1]:,.2f}")
print(f"Deviation : ${df['deviation'].iloc[-1]:,.2f}")

key_dates = df['deviation'].abs().resample('W').max().sort_values(ascending=False).head(5) ## resample w to taek weekly deviation
print(key_dates.to_string())

def results():
    if df['deviation'].iloc[-1] < 0: ##iloc brings most recent data 
        print("BUY")
    elif df['deviation'].iloc[-1] > 0:
        print("TAKE CAUTION")
results()

##CODE FOR MAIN PLOT WITHOUT VOLUME SUBPLOT
##plt.plot(X,y,label = "name") BASIC STRUCTURE 
##plt.plot(df.index, df['gp_aud'], label = "Gold Price") ## USE df.index
##plt.plot(df.index, df['trend'], label = "Trend Line")
##plt.legend()
##plt.title('Trend Regression Gold Price')
##plt.show()

##SUBPLOT
fig, (ax1, ax2) = plt.subplots(2, 1)
ax1.plot(df.index, df['gp_aud'], label = "Gold Price")
ax1.plot(df.index, df['trend'], label = "Trend Line")
ax1.legend()
ax1.set_title('Trend Regression Gold Price')

colors = ['green' if x > 0 else 'red' for x in df['deviation']]
ax2.bar(df.index, df['deviation'], color=colors)
plt.tight_layout()##adjusts for window size

plt.show()



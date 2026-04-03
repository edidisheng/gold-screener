import requests
import pandas as pd
import zipfile
import io

def fetch_cot_gold():
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
            print(f"  fetched {year}")
        except Exception as e:
            print(f"  skipped {year}: {e}")
    return pd.concat(all_data, ignore_index=True)

df = fetch_cot_gold()


df = df[['Report_Date_as_YYYY-MM-DD',
         'M_Money_Positions_Long_All',
         'M_Money_Positions_Short_All']].copy()

df.columns = ['date', 'long', 'short']
df['date'] = pd.to_datetime(df['date'])
df['net_position'] = df['long'] - df['short']
df = df.sort_values('date').reset_index(drop=True)

df['zscore'] = (df['net_position'] - df['net_position'].mean()) / df['net_position'].std()

print(f"\nNet position : {df['net_position'].iloc[-1]:,.0f} contracts")
print(f"Z-score      : {df['zscore'].iloc[-1]:.2f}")

z = df['zscore'].iloc[-1]
if z > 2:
    print("Crowded long — contrarian bearish, caution")
elif z > 1:
    print("Elevated long — mild caution")
elif z < -2:
    print("Crowded short — contrarian bullish, strong entry signal")
elif z < -1:
    print("Elevated short — mild bullish signal")
else:
    print("Neutral positioning")
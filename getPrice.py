import datetime, requests, pickle, time
import pandas as pd
from kraken import go

# Continually fetch price and append to dataframe
def getPrice():
    # Load old price
    with open('prices.pickle', 'rb') as pik:
        prices = pickle.load(pik)

    now = datetime.datetime.today()
    # Grab price
    res = go(['Ticker', 'pair=XMRUSD'])
    bid = res['result']['XXMRZUSD']['b'][0]
    ask = res['result']['XXMRZUSD']['a'][0]
    prices['bid'].append(bid)
    prices['ask'].append(ask)
    prices['time'].append(now)
    # Update price
    with open('prices.pickle', 'wb') as pik:
        pickle.dump(prices, pik)
    # Save to dataframes
    df = pd.DataFrame(prices)
    df['ask'].to_csv('asks.csv', header = False, index= False)
    df['bid'].to_csv('bids.csv', header = False, index= False)

while True:
    getPrice()
    time.sleep(60)

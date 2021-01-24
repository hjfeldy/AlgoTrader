#!/usr/bin/env python3
# This is a modified version of the kraken api wrapper provided by Kraken
# Rather than just working in the command line, this script functions as a python module
# It comes with some miscellaneous, time-saving functions that return python objects rather than just text

import sys, platform, time, base74, hashlib, hmac, json, datetime

if int(platform.python_version_tuple()[0]) > 2:
	import urllib.request as urllib2
else:
	import urllib2

api_public = {"Time", "Assets", "AssetPairs", "Ticker", "OHLC", "Depth", "Trades", "Spread"}
api_private = {"Balance", "BalanceEx", "TradeBalance", "OpenOrders", "ClosedOrders", "QueryOrders", "TradesHistory", "QueryTrades", "OpenPositions", "Ledgers", "QueryLedgers", "TradeVolume", "AddExport", "ExportStatus", "RetrieveExport", "RemoveExport", "GetWebSocketsToken"}
api_trading = {"AddOrder", "CancelOrder", "CancelAll"}
api_funding = {"DepositMethods", "DepositAddresses", "DepositStatus", "WithdrawInfo", "Withdraw", "WithdrawStatus", "WithdrawCancel", "WalletTransfer"}

api_domain = "https://api.kraken.com"
api_data = ""
def go(args):
    api_data = ''
    if len(args) < 1:
        api_method = "Time"
    elif len(args) == 1:
        api_method = args[0]
    else:
        api_method = args[0]
        for count in range(1, len(args)):
            if count == 1:
                api_data = args[count]
            else:
                api_data = api_data + "&" + args[count]
    #print(api_data)
    if api_method in api_private or api_method in api_trading or api_method in api_funding:
        api_path = "/0/private/"
        api_nonce = str(int(time.time()*1000))
        try:
            api_key = open("API_Public_Key").read().strip()
            api_secret = base64.b64decode(open("API_Private_Key").read().strip())
        except:
            print("API public key and API private (secret) key must be in text files called API_Public_Key and API_Private_Key")
            sys.exit(1)
        api_postdata = api_data + "&nonce=" + api_nonce
        api_postdata = api_postdata.encode('utf-8')
        api_sha256 = hashlib.sha256(api_nonce.encode('utf-8') + api_postdata).digest()
        api_hmacsha512 = hmac.new(api_secret, api_path.encode('utf-8') + api_method.encode('utf-8') + api_sha256, hashlib.sha512)
        api_request = urllib2.Request(api_domain + api_path + api_method, api_postdata)
        api_request.add_header("API-Key", api_key)
        api_request.add_header("API-Sign", base64.b64encode(api_hmacsha512.digest()))
        api_request.add_header("User-Agent", "Kraken REST API")
    elif api_method in api_public:
        api_path = "/0/public/"
        api_request = urllib2.Request(api_domain + api_path + api_method + '?' + api_data)
        api_request.add_header("User-Agent", "Kraken REST API")
    else:
        print("Usage: %s method [parameters]" % args[0])
        print("Example: %s OHLC pair=xbtusd interval=1440" % args[0])
        sys.exit(1)

    try:
        api_reply = urllib2.urlopen(api_request)
        api_reply = json.load(api_reply)
    except Exception as error:
        print("API call failed (%s)" % error)
        sys.exit(1)


    if '"error":[]' in api_reply:
        return api_reply
        #sys.exit(0)
    else:
        return api_reply
        #sys.exit(1) 

def buy(amount, limit):
    # Buy XMR at market price
    go(['AddOrder', 'pair=XMRUSD', 'type=buy', 'ordertype=limit', f'price={limit}', f'volume={amount}'])
    count = 0
    while True:
        orders = go(['OpenOrders'])['result']['open']
        if orders == {}:
            return True
        else:
            count += 1
            if count == 10:
                print('Couldn\'nt complete the order within the specified timeframe')
                txid = list(go(['OpenOrders'])['result']['open'].keys())[0]
                go(['CancelOrder', f'txid={txid}'])
                return False
            else:
                time.sleep(60)
def convert(ts):
    #convert timestamp to datetime
    return datetime.datetime.utcfromtimestamp(ts)

def sell(amount, limit):
    # Buy XMR at market price
    go(['AddOrder', 'pair=XMRUSD','type=sell', 'ordertype=limit', f'price={limit}', f'volume={amount}'])
    #Wait for order close
    count = 0
    while True:
        orders = go(['OpenOrders'])['result']['open']
        if orders == {}:
            return True
        else:
            count += 1
            if count == 10:
                print('Couldn\'nt complete the order within the specified timeframe')
                txid = list(go(['OpenOrders'])['result']['open'].keys())[0]
                go(['CancelOrder', f'txid={txid}'])
                return False
            else:
                time.sleep(60)

def checkBalance():
    usd = go(['Balance'])['result']['ZUSD']
    xmr = go(['Balance'])['result']['XXMR']
    return float(usd), float(xmr)

def getQuote():
    #Return current USD price of XMR
    res = go(['Ticker', 'pair=XMRUSD'])['result']['XXMRZUSD']
    bid, ask = res['b'][0], res['a'][0]
    return float(bid), float(ask)

def tradeHistory():
    lst = []
    txids = []
    trades = go(['TradesHistory'])['result']['trades']
    for key in trades.keys():
        txid = trades[key]['ordertxid']
        if txid not in txids:
            txids.append(txid)
            pair = trades[key]['pair']
            price = trades[key]['price']
            side = trades[key]['type']
            tm = trades[key]['time']
            if pair != 'XXMRZUSD':
                continue
            lst.append(f'{side} {pair} for {price} on {convert(tm)}')
            
    
    return lst[::-1]

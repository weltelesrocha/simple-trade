from test.binance import Client
import json

MARKET = 'BTCUSDT'
ASSET = 'USDT'
API_KEY = ''
API_SECRET = ''
client = Client(API_KEY, API_SECRET)
ohlc = client.futures_klines(symbol=MARKET, interval=Client.KLINE_INTERVAL_30MINUTE, limit=1500)
print(ohlc)
with open('./binance-ohlc.json', 'w') as outfile:
    json.dump(ohlc, outfile)
from binance.client import Client
import json

MARKET = 'BTCUSDT'
ASSET = 'USDT'
API_KEY = 'nloqXskw8UQPIzEt6TvkZXIlac45y3TUa92Wjotj9WhLaoGTqhZmvAxS2M09ginV'
API_SECRET = 'YyQVnIGVILPjkp4lBTEFipO83E80K6dYLaIZ3TCOI5oUmjXyfVwQ6tl9gcqP5Gt6'
client = Client(API_KEY, API_SECRET)
ohlc = client.futures_klines(symbol=MARKET, interval=Client.KLINE_INTERVAL_30MINUTE, limit=1500)
print(ohlc)
with open('binance-ohlc.json', 'w') as outfile:
    json.dump(ohlc, outfile)
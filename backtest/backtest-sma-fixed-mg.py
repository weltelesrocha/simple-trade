import pandas
import tulipy as ti
import numpy as np
binance_data = pandas.read_csv('data/binance-btc-usd.csv')
CLOSE = []
POSITION = {
    'price': 0,
    'side': '',
    'date': ''
}
TRADES = []
OHLC = []
MARTINGALE = 0
MAX_MARTINGALE = 0
MAX_AMOUNT = 0
DISTANCE = 0.01
AMOUNT = 20
AMOUNT_NOW = AMOUNT
LOSE = 0
WINS = 0
LOSSES = 0
for index, row in binance_data.iterrows():
    OHLC.append({
        'open': row.Open,
        'high': row.High,
        'low': row.Low,
        'close': row.Close,
        'date': row.Date
    })


def reset_position():
    global POSITION
    POSITION = {
        'price': 0,
        'side': '',
        'date': ''
    }


def martingale():
    global MARTINGALE, AMOUNT, AMOUNT_NOW, LOSE
    MARTINGALE += 1
    LOSE = LOSE + AMOUNT_NOW
    AMOUNT_NOW = (LOSE / 2) + AMOUNT
    max_martingale()


def max_martingale():
    global MARTINGALE, MAX_MARTINGALE, MAX_AMOUNT
    if MARTINGALE > MAX_MARTINGALE:
        MAX_MARTINGALE = MARTINGALE
        MAX_AMOUNT = AMOUNT_NOW


def reset_martingale():
    global MARTINGALE, AMOUNT, AMOUNT_NOW, LOSE
    MARTINGALE = 0
    LOSE = 0
    AMOUNT_NOW = AMOUNT


def is_close_position(ohlc):
    global WINS, LOSSES
    if POSITION['price'] == 0:
        return
    price = POSITION['price']
    price_long = price * (1 + DISTANCE)
    price_short = price * (1 - DISTANCE)
    if POSITION['side'] == "BUY":
        if ohlc['high'] >= price_long:
            TRADES.append({
                'open': price,
                'close': ohlc['high'],
                'date_open': POSITION['date'],
                'date_close': ohlc['date'],
                'type': 'WIN',
                'side': 'BUY',
                'amount': AMOUNT_NOW
            })
            reset_position()
            reset_martingale()
            WINS += 1
        elif ohlc['low'] <= price_short:
            TRADES.append({
                'open': price,
                'close': ohlc['low'],
                'date_open': POSITION['date'],
                'date_close': ohlc['date'],
                'type': 'LOOSE',
                'side': 'BUY',
                'amount': AMOUNT_NOW
            })
            reset_position()
            martingale()
            LOSSES += 1
    else:
        if ohlc['low'] <= price_short:
            TRADES.append({
                'open': price,
                'close': ohlc['low'],
                'date_open': POSITION['date'],
                'date_close': ohlc['date'],
                'type': 'WIN',
                'side': 'SELL',
                'amount': AMOUNT_NOW
            })
            reset_position()
            reset_martingale()
            WINS += 1
        elif ohlc['high'] >= price_long:
            TRADES.append({
                'open': price,
                'close': ohlc['high'],
                'date_open': POSITION['date'],
                'date_close': ohlc['date'],
                'type': 'LOOSE',
                'side': 'SELL',
                'amount': AMOUNT_NOW
            })
            reset_position()
            martingale()
            LOSSES += 1


#
# for index, row in binance_data.iterrows():
#     CLOSE.append(row.Close)
#     print(row.Close)
#     ma1 = ti.sma(np.array(CLOSE), period=1)
#     ma2 = ti.sma(np.array(CLOSE), period=2)
#     print(ti.crossover(ma1, ma2))


for row in OHLC[::-1]:
    # print(row['close'])
    CLOSE.insert(0, row['close'])
    if len(CLOSE) < 50:
        continue
    ma1 = ti.sma(np.array(CLOSE), period=10)
    ma2 = ti.sma(np.array(CLOSE), period=20)
    # print(ti.crossover(ma1, ma2))
    is_close_position(row)
    if POSITION['price'] > 0:
        continue
    if ti.crossover(ma1, ma2)[0]:
        POSITION['price'] = row['close']
        POSITION['side'] = 'BUY'
        POSITION['date'] = row['date']
    elif ti.crossover(ma2, ma1)[0]:
        POSITION['price'] = row['close']
        POSITION['side'] = 'SELL'
        POSITION['date'] = row['date']

# print(TRADES)
print('MAX_MARTINGALE', MAX_MARTINGALE)
print('MAX_AMOUNT', MAX_AMOUNT)
print('WINS', WINS)
print('LOSSES', LOSSES)
# print('TRADES', len(TRADES))
# print('RESULT', len(WINS)*AMOUNT)
# CLOSE.append(row.Close)
# self.ma1 = self.I(SMA, price, 10)
# self.ma2 = self.I(SMA, price, 20)
# print(MACD(CLOSE, fastperiod=12, slowperiod=26, signalperiod=9))

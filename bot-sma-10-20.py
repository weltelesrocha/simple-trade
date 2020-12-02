from binance.client import Client
import time
import datetime
import tulipy as ti
import numpy as np

MARKET = 'BTCUSDT'
ASSET = 'USDT'
API_KEY = ''
API_SECRET = ''
AMOUNT = 10
AMOUNT_NOW = AMOUNT
LOSE = 0
DISTANCE = 0.01
POSITION = {
    'price': 0,
    'side': '',
    'date': '',
    'orderId': '',
    'roe': 0,
    'amount': 0
}


class BinanceClient(Client):
    ORDER_TYPE_TAKE_PROFIT_MARKET = 'TAKE_PROFIT_MARKET'

    def __init__(self, api_key=None, api_secret=None, requests_params=None, tld='com'):
        self.API_URL = self.API_URL.format(tld)
        self.WITHDRAW_API_URL = self.WITHDRAW_API_URL.format(tld)
        self.MARGIN_API_URL = self.MARGIN_API_URL.format(tld)
        self.WEBSITE_URL = self.WEBSITE_URL.format(tld)
        self.FUTURES_URL = self.FUTURES_URL.format(tld)

        self.API_KEY = api_key
        self.API_SECRET = api_secret
        self.session = self._init_session()
        self._requests_params = requests_params
        self.response = None

        # init DNS and SSL cert
        self.ping()

    def transfer_spot_to_futures(self, **params):
        """Post future to spot transfer
          """
        params['type'] = 1
        return self._request_margin_api('post', 'futures/transfer', True, data=params)

    def transfer_futures_to_spot(self, **params):
        """Post future to spot transfer
          """
        params['type'] = 2
        return self._request_margin_api('post', 'futures/transfer', True, data=params)

    def futures_account_balance(self, **params):
        """Get futures account balance

        https://binance-docs.github.io/apidocs/futures/en/#future-account-balance-user_data

        """
        return self._request_futures_api('get', 'balance', True, data=params)


client = BinanceClient(API_KEY, API_SECRET)


def place_win_order():
    AMOUNT_TO_SPOT = POSITION['amount'] - AMOUNT
    client.transfer_futures_to_spot(asset=ASSET, amount=AMOUNT_TO_SPOT)
    reset_position()


def place_lose_order():
    martingale()
    client.transfer_spot_to_futures(asset=ASSET, amount=AMOUNT_NOW)
    reset_position()


def martingale():
    global AMOUNT, AMOUNT_NOW, LOSE
    LOSE = LOSE + AMOUNT_NOW
    AMOUNT_NOW = (LOSE / 2) + AMOUNT


def reset_martingale():
    global AMOUNT, AMOUNT_NOW, LOSE
    LOSE = 0
    AMOUNT_NOW = AMOUNT


def create_position(**params):
    global POSITION
    if params['side'] == Client.SIDE_BUY:
        stopPrice = params['price'] * (1 + DISTANCE)
    else:
        stopPrice = params['price'] * (1 - DISTANCE)
    order = client.futures_create_order(symbol=MARKET,
                                        side=params['side'],
                                        type=Client.ORDER_TYPE_TAKE_PROFIT_MARKET,
                                        quantity=AMOUNT_NOW * 100,
                                        stopPrice=stopPrice)
    params['orderId'] = order['orderId']
    params['amount'] = AMOUNT_NOW * 100
    POSITION = params


def reset_position():
    global POSITION
    POSITION = {
        'price': 0,
        'side': '',
        'date': '',
        'orderId': '',
        'roe': 0,
        'amount': 0
    }


def is_close_position():
    if POSITION['price'] > 0:
        _position = client.futures_position_information()
        if len(_position) == 0:
            liquidation_orders = client.futures_liquidation_orders(symbol=MARKET)
            if filter(lambda n: n['orderId'] == POSITION['orderId'], liquidation_orders):
                place_lose_order()
                return
            else:
                place_win_order()
                return
        else:
            return


def start():
    while True:
        # [
        #     1499040000000,      // Open time
        #     "0.01634790",       // Open
        #     "0.80000000",       // High
        #     "0.01575800",       // Low
        #     "0.01577100",       // Close
        #     "148976.11427815",  // Volume
        #     1499644799999,      // Close time
        #     "2434.19055334",    // Quote asset volume
        #     308,                // Number of trades
        #     "1756.87402397",    // Taker buy base asset volume
        #     "28.46694368",      // Taker buy quote asset volume
        #     "17928899.62484339" // Ignore
        # ]
        now = datetime.datetime.now()
        is_close_position()
        if (now.minute == 0 and now.second == 0) or (now.minute == 30 and now.second == 0):
            print(now, 'UPDATE DATA OHLC')
            ohlc = client.futures_klines(symbol=MARKET, interval=Client.KLINE_INTERVAL_30MINUTE)
            close = []
            for row in ohlc:
                close.append(float(row[4]))
            ma1 = ti.sma(np.array(close), period=10)
            ma2 = ti.sma(np.array(close), period=20)
            if POSITION['price'] == 0:
                if ti.crossover(ma1, ma2)[0]:
                    create_position(price=row['close'], side=Client.SIDE_BUY, date=now)
                elif ti.crossover(ma2, ma1)[0]:
                    create_position(price=row['close'], side=Client.SIDE_SELL, date=now)

        print(now, 'GET POSITION ENTRY_PRICE[{}] ROE[{}] AMOUNT[{}] SIDE[{}]'.format(POSITION['price'],
                                                                                     POSITION['roe'],
                                                                                     POSITION['amount'],
                                                                                     POSITION['side']))
        time.sleep(1)


start()

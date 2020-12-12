from .simple_trade_side import SimpleTradeSide
from .simple_trade_interval import SimpleTradeInterval
from .simple_trade_database import SimpleTradeDatabase
from .simple_trade_log import SimpleTradeLog
from .simple_trade_config import SimpleTradeConfig
from .simple_trade_helper import isset, round_decimals_down
from .simple_trade_result import SimpleTradeResult
from client.binance_client import BinanceClient
import traceback
import sys
import time
import datetime
import numpy as np


class SimpleTradeHandler:
    def __init__(
            self,
            simple_trade_config: SimpleTradeConfig,
            simple_trade_strategy
    ):
        self.log = SimpleTradeLog(simple_trade_config.log_level)
        self.log.silly('Load log module')
        self.config = simple_trade_config
        self.log.silly('Load config module')
        self.strategy = simple_trade_strategy(self)
        self.log.silly('Load strategy module')
        self.database = SimpleTradeDatabase(
            host=simple_trade_config.database_host
        )
        self.log.silly('Load database module')
        self.client = BinanceClient(
            api_key=simple_trade_config.api_key,
            api_secret=simple_trade_config.api_secret
        )
        self.log.silly('Load exchange client')
        self.interval_candle = SimpleTradeInterval(self.config.interval_candle)
        self.log.silly('Load candle interval')
        self.interval_log = SimpleTradeInterval(self.config.interval_log)
        self.log.silly('Load log interval')
        self.interval_check_position = SimpleTradeInterval(self.config.interval_check_position)
        self.log.silly('Load check position interval')
        self.balance = 0
        self.candles = []
        self.position = {}
        self.close = []
        self.trades = []
        self.amount = simple_trade_config.amount
        self.amount_now = self.amount
        self.lose = 0
        self.price = 0
        self.tick_price = 0.01

    def balance_futures(self):
        balance = self.client.futures_account_balance()
        balance_asset = list(filter(lambda x: x['asset'] == self.config.asset, balance))[0]
        return float(balance_asset['availableBalance'])

    def balance_spot(self):
        balance = self.client.get_asset_balance(asset=self.config.asset)
        return float(balance['free'])

    def if_the_balance_is_bigger(self, amount):
        amount_to_transfer = self.balance - amount
        self.log.info(
            'The future balance is greater, transferring {} {} from future to the spot'.format(
                amount_to_transfer, self.config.asset))
        self.client.transfer_futures_to_spot(asset=self.config.asset, amount=amount_to_transfer)
        self.log.silly('Transferred {} {} to spot.'.format(amount_to_transfer, self.config.asset))
        self.balance = amount

    def if_the_balance_is_smaller(self, amount):
        amount_to_transfer = amount - self.balance
        self.log.info(
            'The future balance is smaller, transferring {} {} from spot to the future'.format(
                amount_to_transfer, self.config.asset))
        balance_spot = self.balance_spot()
        self.log.silly('Load balance spot.')
        if balance_spot < amount_to_transfer:
            self.log.info('There is not enough balance')
            self.stop()
        self.client.transfer_spot_to_futures(asset=self.config.asset, amount=amount_to_transfer)
        self.log.silly('Transferred {} {} to future'.format(amount_to_transfer, self.config.asset))
        self.balance = amount

    def check_balance_futures(self, amount=None):
        if amount is None:
            amount = self.config.amount
        self.log.silly('Check balance futures')
        self.balance = self.balance_futures()
        self.log.silly('Load balance futures')
        if round_decimals_down(self.balance) > round_decimals_down(amount):
            return self.if_the_balance_is_bigger(amount)
        if round_decimals_down(amount) > round_decimals_down(self.balance):
            return self.if_the_balance_is_smaller(amount)

    def update_candle(self):
        self.candles = self.client.futures_klines(
            symbol="BTCUSDT",
            interval=self.config.interval_candle)
        close = []
        for row in self.candles:
            close.append(float(row[4]))
        self.close = np.array(close)
        self.price = self.close[-1]
        self.log.silly('Updated Candles')

    def delta_leverage(self):
        return (self.config.leverage / self.config.distance) / 100

    def delta_quantity(self):
        ticker = self.client.futures_ticker(symbol=self.config.market)
        quantity = (self.amount_now / float(ticker['lastPrice'])) * self.delta_leverage()
        return round_decimals_down((quantity - (quantity * self.tick_price)), 3)

    def delta_price_take_profit(self, side: str, price: float):
        if side == SimpleTradeSide.BUY:
            return round(price * (1 + self.config.distance), 2)
        return round(price * (1 - self.config.distance), 2)

    def create_order(self, side: str, quantity: float):
        return self.client.futures_create_order(symbol=self.config.market,
                                                side=side,
                                                type=BinanceClient.ORDER_TYPE_MARKET,
                                                quantity=quantity)

    def create_order_take_profit(self, side: str, quantity: float, stop_price: float):
        sideTakeProfit = SimpleTradeSide.BUY
        if side == SimpleTradeSide.BUY:
            sideTakeProfit = SimpleTradeSide.SELL
        return self.client.futures_create_order(symbol=self.config.market,
                                                side=sideTakeProfit,
                                                type=BinanceClient.ORDER_TYPE_TAKE_PROFIT_MARKET,
                                                quantity=quantity,
                                                stopPrice=stop_price)

    def update_position(self):
        if self.has_created_position():
            self.log.silly('Position updated')
            self.position['closed'] = True
            position = self.client.futures_position_information(symbol=self.config.market)
            if float(position[0]['entryPrice']) > 0:
                self.position['closed'] = False
                self.position['entry_price'] = float(position[0]['entryPrice'])
                self.position['last_price'] = float(position[0]['markPrice'])
                self.position['liquidation_price'] = float(position[0]['liquidationPrice'])

    def notification(self):
        if self.has_created_position():
            self.log.info('POSITION entry price is {}, amount {}, side {}'.format(
                "{:.2f}".format(self.position['entry_price']),
                "{:.2f}".format(self.position['amount']),
                self.position['side']
            ))

    def take_profit_strategy(self, side: str, entry_price: float, quantity: float):
        price_take_profit = self.delta_price_take_profit(side, entry_price)
        self.create_order_take_profit(side, quantity, price_take_profit)

    def create_position(self, side: str = None):
        entry_price = self.last_price()
        if self.has_created_position():
            self.log.info('Most uncreated available position')
            return
        self.log.info('Creating {} position input value at {} quantity {}, market is {}'.format(
            side,
            "{:.2f}".format(entry_price),
            "{:.2f}".format(self.amount_now),
            self.config.market
        ))
        quantity = self.delta_quantity()
        order = self.create_order(side, quantity)
        self.take_profit_strategy(side, entry_price, quantity)
        self.position = {
            'closed': False,
            'order_id': order['orderId'],
            'entry_price': entry_price,
            'date_open': datetime.datetime.now(),
            'amount': self.amount_now,
            'side': side
        }

    def has_created_position(self):
        return isset(self.position, 'side')

    def last_price(self):
        return float(self.price)

    def buy(self):
        self.create_position(SimpleTradeSide.BUY)

    def sell(self):
        self.create_position(SimpleTradeSide.SELL)

    def price_strategy(self, price_strategy):
        strategy = price_strategy(self)
        strategy.calculate_price()
        self.lose = strategy.lose()
        self.amount_now = strategy.amount_now()

    def price_reset(self):
        self.lose = 0
        self.amount_now = self.amount

    def close_position(self):
        trades = self.client.futures_account_trades(symbol=self.config.market)
        last_trade = trades[-1]
        trade = {
            'order_id': self.position['order_id'],
            'side': self.position['side'],
            'open': self.position['entry_price'],
            'close': float(last_trade['price']),
            'date_open': self.position['date_open'],
            'date_close': datetime.datetime.now(),
            'amount': self.position['amount'],
            'result': SimpleTradeResult.WIN
        }
        if float(last_trade['realizedPnl']) < 0:
            trade['result'] = SimpleTradeResult.LOSS
        self.trades.append(trade)
        self.position = {}

    def listener(self):
        while True:
            try:
                now = datetime.datetime.now()
                if self.interval_check_position.is_update(now):
                    self.update_position()
                    if self.has_created_position() and self.position['closed']:
                        self.close_position()
                        self.strategy.on_close_position()
                        self.check_balance_futures(self.amount_now)

                if self.interval_candle.is_update(now):
                    self.update_candle()
                    self.strategy.on_candle_update()

                if self.interval_log.is_update(now):
                    self.notification()
                time.sleep(1)
            except:
                traceback.print_exc()
                time.sleep(10)

    def stop(self):
        sys.exit()

    def start(self):
        self.log.info('Simple trade bot start')
        self.check_balance_futures()
        self.listener()

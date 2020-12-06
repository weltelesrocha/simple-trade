from library import SimpleTradeStrategyInterface, SimpleTradeConfig, SimpleTradeDatabase, SimpleTradeLog, SimpleTradeInterval
from client.binance_client import BinanceClient
import sys
import time


class SimpleTradeHandler:
    def __init__(self, simple_trade_config: SimpleTradeConfig, simple_trade_strategy: SimpleTradeStrategyInterface):
        self.log = SimpleTradeLog(simple_trade_config.log_level)
        self.log.silly('Load log module')
        self.config = simple_trade_config
        self.log.silly('Load config module')
        self.strategy = simple_trade_strategy
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
        self.balance = 0

    def balance_futures(self):
        balance = self.client.futures_account_balance()
        balance_asset = list(filter(lambda x: x['asset'] == self.config.asset, balance))[0]
        return float(balance_asset['availableBalance'])

    def balance_spot(self):
        balance = self.client.get_asset_balance(asset=self.config.asset)
        return float(balance['free'])

    def if_the_balance_is_bigger(self):
        amount_to_transfer = self.balance - self.config.amount
        self.log.info(
            'The future balance is greater, transferring {} {} from future to the spot'.format(
                amount_to_transfer, self.config.asset))
        self.client.transfer_futures_to_spot(asset=self.config.asset, amount=amount_to_transfer)
        self.log.silly('Transferred {} {} to spot.'.format(amount_to_transfer, self.config.asset))
        self.balance = self.config.amount

    def if_the_balance_is_smaller(self):
        amount_to_transfer = self.config.amount - self.balance
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
        self.balance = self.config.amount

    def check_balance_futures(self):
        self.log.silly('Check balance futures')
        self.balance = self.balance_futures()
        self.log.silly('Load balance futures')
        if self.balance > self.config.amount:
            return self.if_the_balance_is_bigger()
        if self.config.amount > self.balance:
            return self.if_the_balance_is_smaller()

    def get_candles(self):
        pass

    def listener(self):
        while True:
            if self.interval_candle.is_update():
                self.log.info('Candle update')
            if self.interval_log.is_update():
                self.log.info('Log update')
            pass
            time.sleep(1)

    def stop(self):
        sys.exit()

    def start(self):
        self.log.info('Simple trade bot start')
        # self.check_balance_futures()
        self.listener()
        pass

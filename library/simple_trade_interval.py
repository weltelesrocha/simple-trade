from client import BinanceClient
from .simple_trade_helper import isset


class SimpleTradeInterval:
    __INTERVAL = {
        BinanceClient.KLINE_INTERVAL_1SECOND: {'second': 1},
        BinanceClient.KLINE_INTERVAL_10SECOND: {'second': 10},
        BinanceClient.KLINE_INTERVAL_1MINUTE: {'minute': 1},
        BinanceClient.KLINE_INTERVAL_5MINUTE: {'minute': 5},
        BinanceClient.KLINE_INTERVAL_15MINUTE: {'minute': 15},
        BinanceClient.KLINE_INTERVAL_30MINUTE: {'minute': 30},
        BinanceClient.KLINE_INTERVAL_1HOUR: {'hour': 0},
        BinanceClient.KLINE_INTERVAL_2HOUR: {'hour': 2},
        BinanceClient.KLINE_INTERVAL_4HOUR: {'hour': 4} 
    }

    def __init__(self, interval=None):
        self.interval = self.__INTERVAL[interval]

    def is_update(self, now):
        if isset(self.interval, 'second') and now.second % self.interval['second'] == 0:
            return True
        if isset(self.interval, 'minute') and now.minute % self.interval['minute'] == 0 and now.second == 0:
            return True
        if isset(self.interval, 'hour') and now.hour % self.interval['hour'] == 0 and now.second == 0:
            return True
        return False

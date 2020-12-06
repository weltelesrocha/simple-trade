from .simple_trade_log import SimpleTradeLog
from .simple_trade_asset import SimpleTradeAsset
from client import BinanceClient
from client import BinanceMarket


class SimpleTradeConfig:
    def __init__(
            self,
            api_key=None,
            api_secret=None,
            amount=10,
            distance=1,
            leverage=100,
            database_host: str = None,
            log_level=SimpleTradeLog.LEVEL_SILLY,
            market=BinanceMarket.BTC_USDT,
            asset=SimpleTradeAsset.USDT,
            interval_candle=BinanceClient.KLINE_INTERVAL_1MINUTE,
            interval_log=BinanceClient.KLINE_INTERVAL_1SECOND
    ):
        self.api_key = api_key
        self.api_secret = api_secret
        self.amount = amount
        self.distance = distance
        self.leverage = leverage
        self.database_host = database_host
        self.log_level = log_level
        self.market = market
        self.asset = asset
        self.interval_candle = interval_candle
        self.interval_log = interval_log

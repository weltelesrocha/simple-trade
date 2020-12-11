from library import SimpleTradeConfig, SimpleTradeHandler
from strategy import StrategySMA1020MGI

simple_trade_handler = SimpleTradeHandler(
    SimpleTradeConfig(
        api_key='',
        api_secret=''
    ),
    StrategySMA1020MGI
)
simple_trade_handler.start()

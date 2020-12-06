from library import SimpleTradeConfig, SimpleTradeHandler
from strategy import StrategySMA1020

simple_trade_handler = SimpleTradeHandler(
    SimpleTradeConfig(
        api_key='',
        api_secret=''
    ),
    StrategySMA1020()
)
simple_trade_handler.start()

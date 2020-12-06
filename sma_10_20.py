from library import SimpleTradeConfig, SimpleTradeHandler
from strategy import StrategySMA1020

simple_trade_handler = SimpleTradeHandler(
    SimpleTradeConfig(
        api_key='zTli0qrCrzcxmmuT5zJNNt7n1LBDqbkmBF3oXFvGysfCqpYAB7E2o2ybgawYRdeu',
        api_secret='eS63dbBsiJuo02eJgdjE4HaNw4fWuqTJ5K5pXJVtVUBDg9jCLEeB2WjLW1terSUX'
    ),
    StrategySMA1020()
)
simple_trade_handler.start()

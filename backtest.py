from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import pandas
from backtesting.test import SMA, GOOG


binance_data = pandas.read_csv('./binance-btc-usd.csv')

class SmaCross(Strategy):
    def init(self):
        price = self.data.Close
        self.ma1 = self.I(SMA, price, 10)
        self.ma2 = self.I(SMA, price, 20)

    def next(self):
        if crossover(self.ma1, self.ma2):
            self.buy()
        elif crossover(self.ma2, self.ma1):
            self.sell()


bt = Backtest(GOOG, SmaCross, commission=.002, exclusive_orders=True, cash=10_000)
stats = bt.run()
print(stats)
# bt.plot()

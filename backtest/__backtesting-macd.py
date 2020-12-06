from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import pandas
from backtesting.test import MACD, GOOG

binance_data = pandas.read_csv('backtest/data/binance-btc-usd.csv')


class MacdCross(Strategy):
    def init(self):
        price = self.data.Close
        self.macd, self.macd_signal, self.macd_histogram = self.I(MACD, price, 12, 26, 9)

    def next(self):
        if crossover(self.macd, self.macd_signal):
            self.buy()
        elif crossover(self.macd_signal, self.macd):
            self.sell()


bt = Backtest(binance_data, MacdCross, commission=.002, exclusive_orders=True, cash=10_000)
stats = bt.run()
print(stats)
# bt.plot()

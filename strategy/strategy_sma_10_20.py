from library import SimpleTradeStrategy, SimpleTradeResult
from price_strategy import MartingaleLight
import tulipy as ti


class StrategySMA1020(SimpleTradeStrategy):
    def on_candle_update(self):
        """Load in the file for extracting text."""
        ma1 = ti.sma(self.handler.close, period=10)
        ma2 = ti.sma(self.handler.close, period=20)
        if ti.crossover(ma1, ma2)[0]:
            self.handler.buy()
        elif ti.crossover(ma2, ma1)[0]:
            self.handler.sell()

    def on_close_position(self):
        """On close position."""
        last_trade = self.handler.trades[-1]
        if last_trade['result'] == SimpleTradeResult.LOSS:
            self.handler.price_strategy(MartingaleLight)
            return
        self.handler.price_reset()

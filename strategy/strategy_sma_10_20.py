from library import SimpleTradeHandler
import tulipy as ti


class StrategySMA1020:
    def __init__(self, handler: SimpleTradeHandler):
        self.handler = handler

    def on_candle_update(self):
        """Load in the file for extracting text."""
        ma1 = ti.sma(self.handler.close, period=10)
        ma2 = ti.sma(self.handler.close, period=20)
        # self.handler.buy()
        if ti.crossover(ma1, ma2)[0]:
            self.handler.buy()
        elif ti.crossover(ma2, ma1)[0]:
            self.handler.sell()

    def on_close_position(self):
        """On close position."""
        self.handler.martingale()

from library import SimpleTradeStrategy, SimpleTradeResult, SimpleTradeSide
from price_strategy import MartingaleLight
import tulipy as ti


class StrategySMA1020MGI(SimpleTradeStrategy):
    def on_candle_update(self):
        ma1 = ti.sma(self.handler.close, period=10)
        ma2 = ti.sma(self.handler.close, period=20)
        if ti.crossover(ma1, ma2)[0]:
            self.handler.buy()
        elif ti.crossover(ma2, ma1)[0]:
            self.handler.sell()

    def on_close_position(self):
        last_trade = self.handler.trades[-1]
        if last_trade['result'] == SimpleTradeResult.LOSS:
            self.handler.price_strategy(MartingaleLight)
            if last_trade['side'] == SimpleTradeSide.BUY:
                self.handler.buy()
                return
            self.handler.sell()
            return
        self.handler.price_reset()

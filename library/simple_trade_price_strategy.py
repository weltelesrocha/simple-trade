from .simple_trade_handler import SimpleTradeHandler


class SimpleTradePriceStrategy:
    def __init__(self, handler: SimpleTradeHandler):
        self.handler = handler

    def calculate_price(self):
        pass

    def lose(self):
        pass

    def amount_now(self):
        pass

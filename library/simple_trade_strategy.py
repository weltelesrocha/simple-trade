from .simple_trade_handler import SimpleTradeHandler


class SimpleTradeStrategy:
    def __init__(self, handler: SimpleTradeHandler):
        self.handler = handler

    def on_candle_update(self):
        """Load in the file for extracting text."""
        pass

    def on_close_position(self):
        """On close position."""
        pass

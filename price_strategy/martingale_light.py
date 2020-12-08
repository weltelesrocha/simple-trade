from library import SimpleTradePriceStrategy


class MartingaleLight(SimpleTradePriceStrategy):
    def calculate_price(self):
        self.handler.lose = self.handler.lose + self.handler.amount_now
        self.handler.amount_now = (self.handler.lose / 2) + self.handler.amount

    def lose(self):
        return self.handler.lose

    def amount_now(self):
        return self.handler.amount_now

from client import BinanceClient
import unittest


class TestBinanceClient(unittest.TestCase):
    def test_delta_liquidation_price(self):
        binance_client = BinanceClient()
        result_long = binance_client.delta_liquidation_price(
            side=BinanceClient.SIDE_BUY,
            wallet_balance=10,
            position_size=0.05,
            entry_price=10000
        )
        self.assertEqual(result_long, 9839.36)

        result_short = binance_client.delta_liquidation_price(
            side=BinanceClient.SIDE_SELL,
            wallet_balance=10,
            position_size=0.05,
            entry_price=10000
        )
        self.assertEqual(result_short, 10159.36)

        result_long = binance_client.delta_liquidation_price(
            side=BinanceClient.SIDE_BUY,
            wallet_balance=1.93,
            position_size=0.01,
            entry_price=19101.82
        )
        print(result_long)
        self.assertEqual(result_long, 18984.83)



if __name__ == '__main__':
    unittest.main()

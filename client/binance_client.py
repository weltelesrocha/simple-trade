from binance.client import Client
from decimal import Decimal


class BinanceClient(Client):
    KLINE_INTERVAL_1SECOND = '1s'
    KLINE_INTERVAL_10SECOND = '10s'
    ORDER_TYPE_TAKE_PROFIT_MARKET = 'TAKE_PROFIT_MARKET'
    FUTURES_API_VERSION_V2 = 'v2'

    def __init__(self, api_key=None, api_secret=None, requests_params=None, tld='com'):
        self.API_URL = self.API_URL.format(tld)
        self.WITHDRAW_API_URL = self.WITHDRAW_API_URL.format(tld)
        self.MARGIN_API_URL = self.MARGIN_API_URL.format(tld)
        self.WEBSITE_URL = self.WEBSITE_URL.format(tld)
        self.FUTURES_URL = self.FUTURES_URL.format(tld)

        self.API_KEY = api_key
        self.API_SECRET = api_secret
        self.session = self._init_session()
        self._requests_params = requests_params
        self.response = None

        # init DNS and SSL cert
        self.ping()

    def transfer_spot_to_futures(self, **params):
        """Post future to spot transfer"""
        params['type'] = 1
        return self._request_margin_api('post', 'futures/transfer', True, data=params)

    def transfer_futures_to_spot(self, **params):
        """Post future to spot transfer"""
        params['type'] = 2
        return self._request_margin_api('post', 'futures/transfer', True, data=params)

    def _create_futures_api_uri_v2(self, path):
        """Future API V2"""
        return self.FUTURES_URL + '/' + self.FUTURES_API_VERSION_V2 + '/' + path

    def _request_futures_api_v2(self, method, path, signed=False, **kwargs):
        uri = self._create_futures_api_uri_v2(path)
        return self._request(method, uri, signed, True, **kwargs)

    def futures_account_balance(self, **params):
        """Get futures account balance

        https://binance-docs.github.io/apidocs/futures/en/#future-account-balance-user_data

        """
        return self._request_futures_api_v2('get', 'balance', True, data=params)

    def delta_liquidation_price(self, side: str = None, wallet_balance: float = 0, position_size: float = 0, entry_price: float = 0):
        """Calculate liquidation price"""
        margin_rate = 0.004
        cum_both = 0
        tmm = 0
        upnl = 0
        side_position = -1
        if side == BinanceClient.SIDE_BUY:
            side_position = 1
        delta_liquidate = (wallet_balance - tmm + upnl + cum_both - (side_position * position_size * entry_price)) / ((position_size * margin_rate) - (side_position * position_size))
        return round(delta_liquidate, 2)

from test.binance import Client


class BinanceClient(Client):
    TAKE_PROFIT_MARKET = 'TAKE_PROFIT_MARKET'

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
        """Post future to spot transfer
          """
        params.type = 1
        return self._request_margin_api('post', 'futures/transfer', True, data=params)

    def transfer_futures_to_spot(self, **params):
        """Post future to spot transfer
          """
        params.type = 2
        return self._request_margin_api('post', 'futures/transfer', True, data=params)

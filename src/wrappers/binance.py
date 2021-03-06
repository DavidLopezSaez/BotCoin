'''Binance REST API Wrapper'''
import hashlib
import hmac
import time
import aiohttp
import requests
from aiohttp.client_exceptions import ClientConnectorError, ClientPayloadError


class Binance:
    '''Manage authentication, uris, etc.'''
    def __init__(self, key='', secret=''):
        self._tokens = (key, secret)

        self._base_url = 'https://api.binance.com'
        self._timestamp_offset = 0
        self._headers = {'X-MBX-APIKEY': self._tokens[0]}


    def _set_timestamp_offset(self):
        '''Calculate difference between binance server timestamp and server.'''
        uri = f'{self._base_url}/api/v3/time'
        res = requests.get(uri)
        server_timestamp = res.json()['serverTime']
        self._timestamp_offset = server_timestamp - int(time.time() * 1000)

    def _add_signature(self, params):
        '''Append timestamp and signature tu params.'''
        if not self._timestamp_offset:
            self._set_timestamp_offset()

        timestamp = int(time.time() * 1000 + self._timestamp_offset)
        if not params:
            params = f'timestamp={timestamp}'
        else:
            params += f'&timestamp={timestamp}'

        signature = hmac.new(
            key=bytes(self._tokens[1], 'utf-8'),
            msg=bytes(params, 'utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()

        params += f'&signature={signature}'
        return params

    def _get(self, url, params):
        '''Perform get request to get data from Binance REST API.'''
        return requests.get(f'{url}?{params}', headers=self._headers).json()

    async def _async_get(self, url, params):
        '''Perfrom async get request to get data from Binance REST API.'''
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'{url}?{params}', headers=self._headers) as response:
                    return await response.json()
        except (ClientConnectorError, ClientPayloadError):
            await self._async_get(url, params)


    async def get_klines(self, symbol='XRPUSDT', interval='1m'):
        '''
        Return kline/candlestick bars for a given symbol.
        Docs: https://binance-docs.github.io/apidocs/spot/en/#kline-candlestick-data
        '''
        uri = f'{self._base_url}/api/v3/klines'
        params = f'symbol={symbol}&interval={interval}&limit=1000'
        return await self._async_get(uri, params)

    async def get_account(self):
        '''
        Return account data.
        Docs: https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md#account-information-user_data
        '''
        uri = f'{self._base_url}/api/v3/account'
        params = self._add_signature('')
        return await self._async_get(uri, params)

    async def get_asset_balance(self, asset):
        '''
        Return balance for a single asset.
        '''
        account = await self.get_account()
        balances = account['balances']

        balance = None
        for bal in balances:
            if bal['asset'] == asset:
                balance = bal
                break
        else:
            return {'Error': 'Asset does not exist.'}

        return balance

    def get_avg_price(self, symbol):
        '''Get average price from a given symbol.'''
        uri = f'{self._base_url}/api/v3/avgPrice'
        params = f'symbol={symbol}'
        return self._get(uri, params)

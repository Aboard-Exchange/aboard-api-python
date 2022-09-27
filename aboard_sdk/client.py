import time
from datetime import datetime
import urllib.parse
import aiohttp
import asyncio
from typing import Dict, Optional, List, Tuple
from urllib.parse import urlencode
import logging
from .rest_client import RestClient, Request
from enum import Enum
from .sign import web3_sign
import json
import hmac
import hashlib
import base64


class Security(Enum):
    NONE = 0
    SIGNED = 1
    API_KEY = 2


class AboardRestAPi(RestClient):
    """REST API"""

    def __init__(self):
        super().__init__()

        self.address = ''
        self.api_key = ''
        self.api_secret = ''
        self.keep_alive_count: int = 0
        self.recv_window: int = 5000
        self.time_offset: int = 0

        self.order_count: int = 1_000_000
        self.init_logger()

    def init_logger(self):
        level = logging.INFO
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(level)
        formatter = logging.Formatter(
            "%(asctime)s  %(levelname)s: %(message)s"
        )
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def calc_signed_headers(self, request):

        timestamp: int = int(time.time() * 1000)
        timestamp = str(timestamp)

        # string to sign
        string_to_sign = f'{request.method.upper()}\n{self.host_ip}\n{request.path}\n{timestamp}\n{self.api_key}'
        if request.params:
            string_to_sign += '\n' + urllib.parse.urlencode(sorted(request.params.items()))

        signature = hmac.new(self.api_secret.encode(), string_to_sign.encode("utf-8"), hashlib.sha256).digest()
        signature: str = base64.b64encode(signature).decode()

        headers = {
            "Content-Type": "application/json",
            'ABOARD-API-KEY': self.api_key,
            'ABOARD-TIMESTAMP': timestamp,
            'ABOARD-SIGNATURE': signature,
        }
        request.headers = headers

    def sign(self, request):
        security: Security = request.data.pop("security")
        # add head to request
        # if security in [Security.SIGNED, Security.API_KEY]:
        if security == Security.SIGNED:
            self.calc_signed_headers(request)
        elif security == Security.API_KEY:
            request.headers.update({"Content-Type": "application/json"})
            # self.gateway.write_log(
            #     f'sign request: {request.params}, {request.path}, {request.data}, {request.headers}')
        request.data = json.dumps(request.data)
        return request

    def connect(
        self,
        address: str,  # address
        private_key: str,  # private key
        proxy_host: str,
        proxy_port: int,
        host,
    ) -> None:
        """connect rest api"""

        self.host_ip = urllib.parse.urlparse(host).netloc

        self.address = address
        self.private_key = private_key
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port

        self.init(host, proxy_host, proxy_port)
        self.start()

        self.write_log("REST API connected")
        self.get_token()
        self.write_log("get REST API token")

    # ----------- trading module ---------------

    def get_open_orders(self, req: Dict=None) -> Dict:
        """
        get open orders
        req:  # Not required 
            {
              "symbol": ""  # Not required 
            }
        return: 
            {
              "code": 0,
              "msg": "",
              "data": [
                {
                  "symbol": "BTCUSDT",
                  "side": "BUY",
                  "positionSide": "SHORT",
                  "status": "NEW",
                  "price": "0",
                  "origQty": "0.40",
                  "origType": "TRAILING_STOP_MARKET",
                  "type": "TRAILING_STOP_MARKET",
                  "timeInForce": "GTC",
                  "orderId": "1573346959",
                  "clientOrderId": "abc",
                  "reduceOnly": false,
                  "workingType": "LAST_PRICE",
                  "stopPrice": "9300",
                  "closePosition": false,
                  "activatePrice": "9020",
                  "priceRate": "0.3",
                  "priceProtect": false,
                  "orderTime": 1579276756075,
                  "cumQuote": "0",
                  "executedQty": "0",
                  "avgPrice": "0.00000",
                  "updateTime": 1579276756075,
                  "frozenMargin": "12.34"
                }
              ]
            }
        """
        default_req = {
            "symbol": ""  # Not required 
        }
        data: dict = {"security": Security.SIGNED}

        if req:
            default_req.update(req)

        res = self.request(
            method="GET",
            path="/api/v1/trade/openOrders",
            data=data,
            params=default_req
        )
        return res.json()

    def get_order(self, req: Dict):
        '''
        get order
        req:
            {
              "symbol": "",  # required 
              "orderId": "",
              "clientOrderId": "",
            }
        return:
            {
              "code": 0,
              "msg": "",
              "data": {
                "symbol": "BTCUSDT",
                "side": "BUY",
                "positionSide": "SHORT",
                "status": "NEW",
                "price": "0",
                "origQty": "0.40",
                "origType": "TRAILING_STOP_MARKET",
                "type": "TRAILING_STOP_MARKET",
                "timeInForce": "GTC",
                "orderId": "1573346959",
                "clientOrderId": "abc",
                "reduceOnly": false,
                "workingType": "LAST_PRICE",
                "stopPrice": "9300",
                "closePosition": false,
                "activatePrice": "9020",
                "priceRate": "0.3",
                "priceProtect": false,
                "orderTime": 1579276756075,
                "cumQuote": "0",
                "executedQty": "0",
                "avgPrice": "0.00000",
                "updateTime": 1579276756075
              }
            }
        '''
        default_req = {
            "symbol": "",  # required 
            "orderId": "",  # orderId or clientOrderId is required
            "clientOrderId": "",
        }
        data: dict = {"security": Security.SIGNED}
        if req:
            default_req.update(req)
        res = self.request(
            method="GET",
            path="/api/v1/trade/order",
            data=data,
            params=default_req
        )
        return res.json()

    def get_history_orders(self, req: Dict):
        '''
        get history orders
        req:
            {
              "symbol": "ETHUSDT",  # required
              "orderId": "",
              "startTime": 1628575642000,
              "endTime": 1628585642000,
              "limit": 100,
            }
        return:
            {
              "code": 0,
              "msg": "",
              "data": [
                {
                  "symbol": "ETHUSDT",
                  "side": "BUY",
                  "positionSide": "SHORT",
                  "status": "NEW",
                  "price": "0",
                  "origQty": "0.40",
                  "origType": "TRAILING_STOP_MARKET",
                  "type": "TRAILING_STOP_MARKET",
                  "timeInForce": "GTC",
                  "orderId": "1573346959",
                  "clientOrderId": "abc",
                  "reduceOnly": false,
                  "workingType": "LAST_PRICE",
                  "stopPrice": "9300",
                  "closePosition": false,
                  "activatePrice": "9020",
                  "priceRate": "0.3",
                  "priceProtect": false,
                  "orderTime": 1579276756075,
                  "cumQuote": "0",
                  "executedQty": "0",
                  "avgPrice": "0.00000",
                  "updateTime": 1579276756075
                }
              ]
            }
        '''
        default_req = {
            "symbol": "",  # required
            "orderId": "",
            "startTime": 0,
            "endTime": 0,
            "limit": 100,
        }
        data: dict = {"security": Security.SIGNED}
        if req:
            default_req.update(req)
        res = self.request(
            method="GET",
            path="/api/v1/trade/historyOrders",
            data=data,
            params=default_req
        )
        return res.json()

    def get_history_trades(self, req: Dict):
        '''
        get history trades
        req:
            {
              "symbol": "ETHUSDT",  # required
              "fromId": "",
              "startTime": 1628575642000,
              "endTime": 1628585642000,
              "limit": 100,
            }
        return:
            {
              "code": 0,
              "msg": "",
              "data": [
                {
                  "symbol": "ETHUSDT",
                  "side": "SELL",
                  "positionSide": "SHORT",
                  "orderId": 25851813,
                  "id": "698759",
                  "price": "7819.01",
                  "qty": "0.002",
                  "quoteQty": "15.63802",
                  "realizedPnl": "-0.91539999",
                  "commission": "-0.07819010",
                  "commissionAsset": "USDT",
                  "maker": false,
                  "doneTime": 1569514978020,
                  "tradeType": "Standard"
                }
              ]
            }
        '''
        default_req = {
            "symbol": "",  # required
            "fromId": "",
            "startTime": 0,
            "endTime": 0,
            "limit": 100,
        }
        data: dict = {"security": Security.SIGNED}
        if req:
            default_req.update(req)
        res = self.request(
            method="GET",
            path="/api/v1/trade/historyTrades",
            data=data,
            params=default_req
        )
        return res.json()

    def send_order(self, req: Dict) -> Dict:
        """
        send order
        req: {  # required
            'symbol': 'BTC-USDC', 
            'side': 'BUY', 
            'type': 'LIMIT', 
            'price': 1000, 
            'quantity': 1, 
            'clientOrderId': 'xxx',  # client order id
        }
        return:
            {
              "code": 0,
              "msg": "",
              "data": {
                "clientOrderId": "",
                "orderId": ""
              }
            }
        """
        default_req = {
            "symbol": '',
            "side": '',
            "type": '',
            "price": '',
            "quantity": '',
            "clientOrderId": '',
            "reduceOnly": "FALSE",
            "stopPrice": 0,
            "positionSide": "",
            "closePosition": "FALSE",
            "activationPrice": 0,
            "callbackRate": 0.0,
            "timeInForce": "GTC",
            "workingType": "LAST_PRICE",
            "priceProtect": "FALSE"
        }
        data: dict = {
            "security": Security.SIGNED
        }
        if req:
            default_req.update(req)

        if req.get('timeInForce'):
            default_req["timeInForce"] = req['timeInForce']
        elif req['type'] == 'LIMIT':
            default_req["timeInForce"] = "GTC"

        data.update(default_req)

        res = self.request(
            method="POST",
            path="/api/v1/trade/order",
            data=data,
        )
        return res.json()

    def batch_send_orders(self, reqs: List):
        '''
        reqs:
        [
            {
                'symbol': 'BTC-USDC', 
                'side': 'BUY', 
                'type': 'LIMIT', 
                'price': 1000, 
                'quantity': 1, 
                'clientOrderId': 'xxx',
            }
        ]
        return:
            {
              "code": 0,
              "msg": "",
              "data": [
                {
                  "clientOrderId": "",
                  "orderId": "",
                  "code": 0,
                  "msg": ""
                }
              ]
            }
        '''
        default_req = {
            "symbol": '',
            "side": '',
            "type": '',
            "price": '',
            "quantity": '',
            "clientOrderId": '',
            "reduceOnly": "FALSE",
            "stopPrice": 0,
            "positionSide": "",
            "closePosition": "FALSE",
            "activationPrice": 0,
            "callbackRate": 0.0,
            "timeInForce": "GTC",
            "workingType": "LAST_PRICE",
            "priceProtect": "FALSE"
        }
        data: dict = {
            "security": Security.SIGNED
        }

        params = []
        for req in reqs:
            _default_req = default_req.copy()
            _default_req.update(req)
            if req.get('timeInForce'):
                _default_req["timeInForce"] = req['timeInForce']
            elif req['type'] == 'LIMIT':
                _default_req["timeInForce"] = "GTC"
            params.append(_default_req)

        data.update(params)
        res = self.request(
            method="POST",
            path="/api/v1/trade/batchOrders",
            data=data,
        )
        return res.json()

    def cancel_order(self, req: Dict) -> Dict:
        """
        cancel order
        req: {
            'symbol':'BTC-USDC',
            'clientOrderId':'xxx',
            'orderId':'xxx',
        }
        return:
            {
              "code": 0,
              "msg": ""
            }
        """
        default_req = {
            'symbol': '',
            'clientOrderId': '',
            'orderId': '',
        }
        data: dict = {"security": Security.SIGNED}
        if req:
            default_req.update(req)
        data.update(default_req)

        res = self.request(
            method="POST",
            path="/api/v1/trade/cancelOrder",
            data=data,
        )
        return res.json()

    def batch_cancel_order(self, reqs: List[Dict]) -> Dict:
        """
        batch cancel order
        reqs: {
            [
            'symbol':'BTC-USDC',
            'clientOrderId':'xxx',
            'orderId':'xxx',
            ]
        }
        return:
            {
              "code": 0,
              "msg": "",
              "data": [
                {
                  "clientOrderId": "",
                  "orderId": "",
                  "code": 0,
                  "msg": ""
                }
              ]
            }
        """
        default_req = {
            'symbol': '',
            'clientOrderId': '',
            'orderId': '',
        }
        data: dict = {"security": Security.SIGNED}

        params = []
        for req in reqs:
            _default_req = default_req.copy()
            _default_req.update(req)
            params.append(_default_req)
        data.update(default_req)

        res = self.request(
            method="POST",
            path="/api/v1/trade/batchCancelOrders",
            data=data,
        )
        return res.json()

    # ----------- account data ---------------

    def get_token(self):
        """
        get api_key, api_secret when login
        """
        data: dict = {
            "security": Security.API_KEY
        }

        timestemp = str(int(datetime.now().timestamp() * 1000))
        msg = 'action:\nAboard Authentication\nonlySignOn:\nhttps://aboard.exchange\ntimestamp:\n{}'.format(
            timestemp)
        signature = web3_sign(self.private_key, msg)

        headers: dict = {
            "ABOARD-SIGNATURE": signature,  # signed string
            'ABOARD-ADDRESS': self.address,   # wallet address
            'ABOARD-TIMESTAMP': timestemp,  # ms
        }

        path: str = "/api/v1/account/login"
        res = self.request(
            method="POST",
            path=path,
            data=data,
            headers=headers,
        )
        data = res.json()
        self.api_key = data['data']["apiKey"]
        self.api_secret = data['data']["apiSecret"]
        return self.api_key, self.api_secret

    def get_position(self, req: Dict=None) -> Dict:
        """
        get position
        req: 
            {
              "symbol": "",  # not required
            }
        return:
            {
              "code": 0,
              "msg": "",
              "data": [
                {
                  "symbol": "BTCUSDT",
                  "positionSide": "NET",
                  "marginType": "CROSSED",
                  "positionAmt": "-234.78",
                  "availableAmt": "200",
                  "leverage": "10",
                  "openPrice": "0.00000",
                  "unRealizedProfit": "0.00",
                  "positionMargin": "0.00",
                  "isAutoAddMargin": "false",
                  "isolatedMargin": "0.00",
                  "markPrice": "6679.50671178",
                  "liquidationPrice": "0",
                  "marginRate": "0",
                  "updateTime": 1625474304765
                }
              ]
            }
        """
        default_req = {
            "symbol": "",  # not required
        }

        data: dict = {"security": Security.SIGNED}
        if req:
            default_req.update(req)
        res = self.request(
            method="GET",
            path="/api/v1/account/positions",
            data=data,
            params=default_req
        )
        return res.json()

    def get_trading_fee(self, req: Dict=None) -> Dict:
        """
        get trading fee
        req: 
            {
              "symbol": "",  # not required
            }
        return:
            {
              "code": 0,
              "msg": "",
              "data": {
                "symbol": "",
                "makerCommissionRate": "0.0002",
                "takerCommissionRate": "0.0004",
                "withdrawFee": "5"
              }
            }
        """
        default_req = {
            "symbol": "",  # not required
        }
        data: dict = {"security": Security.SIGNED}
        if req:
            default_req.update(req)

        res = self.request(
            method="GET",
            path="/api/v1/account/commissionRate",
            data=data,
            params=default_req
        )
        return res.json()

    def get_account(self) -> Dict:
        """
        get account
        return:
            {
              "code": 0,
              "msg": "",
              "data": {
                "totalWalletBalance": "23.72469206",
                "totalUnrealizedProfit": "0.00000000",
                "totalMarginBalance": "23.72469206",
                "totalPositionMargin": "0.00000000",
                "totalFrozenMargin": "0.00000000",
                "totalFrozenMoney": "0.00000000",
                "totalAvailableBalance": "23.72469206",
                "assets": [
                  {
                    "asset": "USDT",
                    "walletBalance": "23.72469206",
                    "unrealizedProfit": "0.00000000",
                    "marginBalance": "23.72469206",
                    "positionMargin": "0.00000000",
                    "frozenMargin": "0.00000000",
                    "frozenMoney": "0.00000000",
                    "availableBalance": "23.72469206",
                    "updateTime": 1625474304765
                  }
                ]
              }
            }
        """
        data: dict = {"security": Security.SIGNED}

        res = self.request(
            method="GET",
            path="/api/v1/account/balance",
            data=data
        )
        return res.json()

    def get_bills(self, req: Dict=None) -> Dict:
        """
        get bills
        req: 
            {  # all not required
              "symbol": "ETH-USDC",
              "billType": "REALIZED_PNL",  # DEPOSIT, WITHDRAW, REALIZED_PNL，FUNDING_FEE, COMMISSION, LIQUIDATION
              "startTime": 1628575642000,
              "endTime": 1628585642000,
              "limit": 100,  # default: 100 max: 500
            }
        return:
            {
              "code": 0,
              "msg": "",
              "data": [
                {
                  "symbol": "ETHUSDT",
                  "billType": "REALIZED_PNL",
                  "amount": "-0.37500000",
                  "asset": "USDT",
                  "info": "REALIZED_PNL",
                  "insertTime": 1570608000000,
                  "id": "9689322392"
                }
              ]
            }
        """
        default_req = {  # all not reuqred
            "symbol": "",
            "billType": "",  # DEPOSIT, WITHDRAW, REALIZED_PNL，FUNDING_FEE, COMMISSION, LIQUIDATION
            "startTime": 0,
            "endTime": 0,
            "limit": 100,  # default: 100 max: 500
        }

        data: dict = {"security": Security.SIGNED}
        if req:
            default_req.update(req)

        res = self.request(
            method="GET",
            path="/api/v1/account/bills",
            data=data,
            params=default_req
        )
        return res.json()

    # ------------ market data ----------------

    def get_tickers(self) -> Dict:
        """
        get tickers
        return:
            {
              "code": 0,
              "msg": "",
              "data": [
                {
                  "symbol": "BTCUSDT",
                  "priceChange": "-94.99999800",
                  "priceChangePercent": "-95.960",
                  "lastPrice": "4.00000200",
                  "lastQty": "200.00000000",
                  "openPrice": "99.00000000",
                  "highPrice": "100.00000000",
                  "lowPrice": "0.10000000",
                  "volume": "8913.30000000",
                  "quoteVolume": "15.30000000",
                  "count": 76
                }
              ]
            }
        """
        data: dict = {"security": Security.NONE}
        res = self.request(
            method="GET",
            path="/api/v1/market/tickers",
            data=data
        )
        return res.json()

    def get_ticker(self, req: Dict) -> Dict:
        """
        get ticker
        req:
            {
              "symbol": "BTCUSDT"
            }
        return:
            {
              "code": 0,
              "msg": "",
              "data": {
                "symbol": "BTCUSDT",
                "priceChange": "-94.99999800",
                "priceChangePercent": "-95.960",
                "lastPrice": "4.00000200",
                "lastQty": "200.00000000",
                "openPrice": "99.00000000",
                "highPrice": "100.00000000",
                "lowPrice": "0.10000000",
                "volume": "8913.30000000",
                "quoteVolume": "15.30000000",
                "count": 76
              }
            }
        """
        default_req = {
            "symbol": ""
        }
        data: dict = {"security": Security.NONE}
        if req:
            default_req.update(req)

        res = self.request(
            method="GET",
            path="/api/v1/market/ticker",
            data=data,
            params=default_req
        )
        return res.json()

    def get_depth(self, req: Dict) -> Dict:
        """
        get depth
        req:
            {
              "symbol": "",  # required
              "limit": 20  # depth default 20
            }
        return:
            {
              "code": 0,
              "msg": "",
              "data": {
                "bids": [
                  {
                    "0": "4.00000000",
                    "1": "431.00000000"
                  }
                ],
                "asks": [
                  {
                    "0": "4.00000200",
                    "1": "12.00000000"
                  }
                ],
                "time": 1569514978020
              }
            }
        """
        default_req = {
            "symbol": "",  # required
            "limit": 20  # depth，default20
        }
        data: dict = {"security": Security.NONE}
        if req:
            default_req.update(req)

        res = self.request(
            method="GET",
            path="/api/v1/market/depth",
            data=data,
            params=default_req
        )
        return res.json()

    def get_klines(self, req: Dict) -> Dict:
        """
        get klines
        req:
            {
              "symbol": "ETHUSDT",  # required
              "interval": "15m",  # required
              "startTime": 1628575642000,
              "endTime": 1628585642000,
              "limit": 100
            }
        return:
            {
              "code": 0,
              "msg": "",
              "data": [
                {
                  "0": 1499040000000,
                  "1": "0.01634790",
                  "2": "0.80000000",
                  "3": "0.01575800",
                  "4": "0.01577100",
                  "5": "148976.11427815",
                  "6": "2434.19055334",
                  "7": 308
                }
              ]
            }
        """
        default_req = {
            "symbol": "",  # required
            "interval": "",  # required
            "startTime": 0,
            "endTime": 0,
            "limit": 100
            # "endTime": int(datetime.now().timestamp() * 1000),
        }
        data: dict = {"security": Security.NONE}
        if req:
            default_req.update(req)

        res = self.request(
            method="GET",
            path="/api/v1/market/klines",
            data=data,
            params=default_req
        )
        return res.json()

    def get_trades(self, req: Dict) -> Dict:
        """
        get trades
        req:
            {
              "symbol": "",  # required
              "limit": 100
            }
        return:
            {
              "code": 0,
              "msg": "",
              "data": [
                {
                  "id": "28457",
                  "price": "4.00000100",
                  "qty": "12.00000000",
                  "time": 1499865549590,
                  "side": "SELL",
                  "maker": false
                }
              ]
            }
        """
        default_req = {
            "symbol": "",  # required
            "limit": 100
        }
        data: dict = {"security": Security.NONE}
        if req:
            default_req.update(req)

        res = self.request(
            method="GET",
            path="/api/v1/market/trades",
            data=data,
            params=default_req
        )
        return res.json()

    # ----------------- public data ----------------
    def get_index_oracle_funding(self, req: Dict=None) -> Dict:
        """
        get_index_oracle_funding
        req:
            {
              "symbol": "",  # not required
            }
        return:
            {
              "code": 0,
              "msg": "",
              "data": [
                {
                  "symbol": "ETHUSDT",
                  "indexPrice": "2004.26",
                  "oraclePrice": "2005.26",
                  "fundingRate": "0.00056",
                  "time": 1597370495002
                }
              ]
            }
        """
        default_req = {
            "symbol": "",  # not required
        }
        data: dict = {"security": Security.NONE}
        if req:
            default_req.update(req)
        res = self.request(
            method="GET",
            path="/api/v1/public/indexOracleFunding",
            data=data,
            params=default_req
        )
        return res.json()

    def get_history_funding_rate(self, req: Dict=None) -> Dict:
        """
        get history funding rate
        req:
            {
                "symbol": "",  # not required
                "startTime": 0,
                "endTime": 0,
                "limit": 100
            }
        return:
            {
              "code": 0,
              "msg": "",
              "data": [
                {
                  "symbol": "BTCUSDT",
                  "fundingRate": "-0.03750000",
                  "fundingTime": 1570608000000
                }
              ]
            }
        """
        default_req = {
            "symbol": "",  # not required
            "startTime": 0,
            "endTime": 0,
            "limit": 100
        }
        data: dict = {"security": Security.NONE}
        if req:
            default_req.update(req)
        res = self.request(
            method="GET",
            path="/api/v1/public/historyFundingRate",
            data=data,
            params=default_req
        )
        return res.json()

    def get_history_insurance_fund(self, req: Dict=None) -> Dict:
        """
        get history insurance fund
        req:
            {
                "symbol": "",
                "startTime": 0,
                "endTime": 0,
                "limit": 100
            }
        return:
            {
              "code": 0,
              "msg": "",
              "data": [
                {
                  "symbol": "BTCUSDT",
                  "fundingRate": "-0.03750000",
                  "fundingTime": 1570608000000
                }
              ]
            }
        """
        default_req = {
            "symbol": "",
            "startTime": 0,
            "endTime": 0,
            "limit": 100
        }
        data: dict = {"security": Security.NONE}
        if req:
            default_req.update(req)
        res = self.request(
            method="GET",
            path="/api/v1/public/historyFundingRate",
            data=data,
            params=default_req
        )
        return res.json()

    def get_instruments(self, req: Dict=None) -> Dict:
        """
        get instruments
        req:
            {
                symbol": "",  # not required
            }
        return:
            {
              "code": 0,
              "msg": "",
              "data": [
                {
                  "symbol": "BTC-USDC",
                  "asset": "USDC",
                  "initMarginRate": "",
                  "maintainMarginRate": "",
                  "maxLeverage": "",
                  "minOrderSize": "",
                  "maxOrderSize": "",
                  "maxPositionSize": "",
                  "priceTick": "",
                  "quantityStep": ""
                }
              ]
            }
        """
        default_req = {
            "symbol": "",  # not required
        }
        data: dict = {"security": Security.NONE}
        if req:
            default_req.update(req)
        res = self.request(
            method="GET",
            path="/api/v1/public/instruments",
            data=data,
            params=default_req
        )
        return res.json()

    def request_withdrawal(self, req: Dict=None) -> Dict:
        '''
        req:
            {
              "asset": "USDC",
              "amount": "1000",
              "destination": "0x2222...",  # destination only support the same withdraw address
            }
        return:
            {
              "code": 0,
              "msg": ""
            }
        '''
        data: dict = {"security": Security.SIGNED}
        if req:
            data.update(req)
        res = self.request(
            method="POST",
            path="/api/v1/account/withdraw",
            data=data
        )
        return res.json()

    # ----------------- others ----------------
    def _new_order_id(self) -> int:
        """generate a new client orderid"""
        self.order_count += 1
        return self.order_count

    def write_log(self, msg):
        self.logger.log(level=logging.INFO, msg=msg)

    def generate_private_websocket_header(self, url=None):
        request = Request(method='GET', path='/users/self/verify', headers={}, data={}, params={})
        self.calc_signed_headers(request)
        headers = request.headers
        return headers

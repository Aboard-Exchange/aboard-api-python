# import time
# from datetime import datetime
import urllib.parse
import aiohttp
import asyncio
from asyncio import run_coroutine_threadsafe
from typing import Dict, Optional, List, Tuple
from .websocket_client import WebsocketClient
from enum import Enum
import json
import logging
# from abc import ABC, abstractmethod, ABCMeta


class UserWebsocketClient(WebsocketClient):
    """docstring for UserWebsocketClient"""

    def __init__(self):
        super(UserWebsocketClient, self).__init__()
        self.init_logger()

    def start(self):
        super().start()
        self.write_log(f'loop: {self._loop} ')
        run_coroutine_threadsafe(self.keep_alive(), loop=self._loop)
        self.write_log('keep alive coroutine start. ')

    async def keep_alive(self):
        while True:
            if self._ws:
                text = 'pong'
                await self._ws.send_str(text)
                # self.write_log('keep alive, send "&"')
            await asyncio.sleep(3)

    def unpack_data(self, data: str):
        """
        json decode string
        """
        if data == 'ping':
            return {}
        return json.loads(data)

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

    def write_log(self, msg):
        self.logger.log(level=logging.INFO, msg=msg)


class PrivateWebsocketApi(UserWebsocketClient):
    """
    Private Websocket API
    """

    def __init__(self) -> None:
        super().__init__()
        self.subscribed_symbols = set()
        self.connected = False

    def connect(self, websocket_trade_host: str, proxy_host: int, proxy_port: int) -> None:
        """Connect Private Websocket"""
        url = websocket_trade_host
        self.init(url, proxy_host, proxy_port)
        self.start()

    def auth(self, api_key, timestamp, signature):
        packet = {
            'op': 'auth',
            'args': [{
                'apiKey': api_key,
                'timestamp': timestamp,
                'signature': signature,
            }]
        }
        self.send_packet(packet)

    def subscribe_account(self, asset='USDC'):
        '''
        subscribe account
        send:
            {
              "op": "subscribe",
              "args": [
                {
                  "channel": "account",
                  "asset": "USDT"
                }
              ]
            }
        '''
        packet = {
            'op': 'subscribe',
            'args': [{
                'channel': 'account',
                'asset': asset,
            }]
        }
        self.send_packet(packet)
        self.write_log(
            'subscribe acount, asset: USDC, channel: account')

    def subscribe_position(self, symbol: str):
        '''
        subscribe position
        send:
            {
              "op": "subscribe",
              "args": [
                {
                  "channel": "position",
                  "symbol": "BTCUSDT"
                }
              ]
            }
        '''
        packet = {
            'op': 'subscribe',
            'args': [
                {
                    'channel': 'position',
                    'symbol': symbol,
                }
            ]
        }
        self.send_packet(packet)
        self.write_log(f'subscribe position, {symbol}')

    def subscribe_order(self, symbol: str):
        '''
        subscribe order
        send:
            {
              "op": "subscribe",
              "args": [
                {
                  "channel": "order",
                  "symbol": "BTCUSDT"
                }
              ]
            }
        '''
        packet = {
            'op': 'subscribe',
            'args': [
                {
                    'channel': 'order',
                    'symbol': symbol,
                }
            ]
        }
        self.send_packet(packet)
        self.write_log(f'subscribe order, {symbol}')

    def on_connected(self) -> None:
        """on connected success"""
        self.connected = True  # sign of connected. Check it before sending package.
        self.write_log("Private Websocket API connected. ")

    def on_disconnected(self):
        '''reload this method to reconnect'''
        self.connected = False

    def on_packet(self, packet: dict) -> None:
        """handle data received"""
        # self.write_log(f'trade packet: {packet}')
        channel = packet.get('channel')
        if not channel:
            if packet.get('event') == 'auth':
                self.on_auth(packet)
            return

        if channel == "account":
            self.on_account(packet)
        elif channel == "position":
            self.on_position(packet)
        elif channel == "order":
            self.on_order(packet)

    def on_auth(self, packet):
        '''on auth
        receive:
            {
              "event": "auth",
              "code": 0,
              "msg": ""
            }
        '''
        pass

    def on_account(self, packet: dict) -> None:
        """account data handler
        receive:
        {
          "arg": {
            "channel": "account",
            "asset": "USDT"
          },
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
        pass

    def on_position(self, packet: dict) -> None:
        '''position handler
        receive:
        {
          "arg": {
            "channel": "position",
            "symbol": "BTCUSDT"
          },
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

        '''
        pass

    def on_order(self, packet: dict) -> None:
        """order handler
        receive:
        {
          "arg": {
            "channel": "order",
            "symbol": "BTCUSDT"
          },
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
              "time": 1579276756075,
              "cumQuote": "0",
              "executedQty": "0",
              "avgPrice": "0.00000",
              "updateTime": 1579276756075,
              "frozenMargin": "12.34"
            }
          ]
        }
        """
        pass


class PublicWebsocketApi(UserWebsocketClient):
    """Public Websocket API"""

    def __init__(self) -> None:
        super().__init__()

        self.subscribed: Dict[str, Dict] = {}
        self.reqid: int = 0
        self.connected = False

    def connect(self, websocket_data_host: str, proxy_host: str, proxy_port: int):
        """connect public websocket"""
        self.init(websocket_data_host, proxy_host, proxy_port)
        self.start()

    def on_connected(self) -> None:
        """on connected"""
        self.write_log("Public Websocket API connected")
        self.connected = True
        # for req in list(self.subscribed.values()):
        #     self.subscribe(req)  # subscribe again after reconnected/connected

    def on_disconnected(self):
        self.connected = False

    def send_heartbeat(self):
        '''ping pong'''
        packet = {"ping": ""}
        self.send_packet(packet)

    def subscribe_all_tickers(self):
        '''
        subscribe all tickers
        send:
            {
                "op": "subscribe",
                "args": [
                      {
                          "channel": "tickers"
                      }
                ]
            }
        '''
        self.reqid += 1
        packet = {
            "op": "subscribe",
            "args": [
                  {
                      "channel": "tickers"
                  }
            ]
        }
        self.send_packet(packet)

    def subscribe_ticker(self, symbol: str):
        '''
        subscribe ticker
        send:
            {
              "op": "subscribe",
              "args": [
                {
                  "channel": "ticker",
                  "symbol": "BTCUSDT"
                }
              ]
            }
        '''
        packet = {
            "op": "subscribe",
            "args": [
              {
                  "channel": "ticker",
                  "symbol": symbol
              }
            ]
        }
        self.send_packet(packet)

    def subscribe_depth(self, symbol: str, level=5):
        '''subscribe depth
        level: 5,10,20
        push snapshot each 200ms
        send:
            {
                "op": "subscribe",
                "args": [
                  {
                      "channel": "depth{}".format(level),
                      "symbol": symbol
                  }
                ]
            }
        '''
        packet = {
            "op": "subscribe",
            "args": [
              {
                  "channel": "depth{}".format(level),
                  "symbol": symbol
              }
            ]
        }
        self.send_packet(packet)

    def subscribe_kline(self, symbol, bar='1m'):
        '''subscribe kline
        bar: 1m,5m,15m,30m,1h,4h,1d
        send:
            {
                "op": "subscribe",
                "args": [
                  {
                      "channel": "kline{}".format(bar),
                      "symbol": symbol
                  }
                ]
            }
        '''

        packet = {
            "op": "subscribe",
            "args": [
              {
                  "channel": "kline{}".format(bar),
                  "symbol": symbol
              }
            ]
        }
        self.send_packet(packet)

    def subscribe_trade(self, symbol) -> None:
        '''
        subscribe latest trade
        send:
            {
                "op": "subscribe",
                "args": [
                  {
                      "channel": "trade",
                      "symbol": symbol
                  }
                ]
            }
        '''
        packet = {
            "op": "subscribe",
            "args": [
              {
                  "channel": "trade",
                  "symbol": symbol
              }
            ]
        }
        self.send_packet(packet)

    def subscribe_oracle(self, symbol):
        '''
        subscribe oracle
        send:
            {
                "op": "subscribe",
                "args": [
                   {
                      "channel": "oracle",
                      "symbol": symbol
                   }
                ]
            }
        '''
        packet = {
            "op": "subscribe",
            "args": [
              {
                  "channel": "oracle",
                  "symbol": symbol
              }
            ]
        }
        self.send_packet(packet)

    def subscribe_index(self, symbol):
        '''
        subscribe index
        send:
            {
                "op": "subscribe",
                "args": [
                  {
                      "channel": "index",
                      "symbol": symbol
                  }
                ]
            }
        '''
        packet = {
            "op": "subscribe",
            "args": [
              {
                  "channel": "index",
                  "symbol": symbol
              }
            ]
        }
        self.send_packet(packet)

    def subscribe_funding(self, symbol):
        '''
        subscribe funding fee
        send:
            {
                "op": "subscribe",
                "args": [
                  {
                      "channel": "funding",
                      "symbol": symbol
                  }
                ]
            }
        '''
        packet = {
            "op": "subscribe",
            "args": [
              {
                  "channel": "funding",
                  "symbol": symbol
              }
            ]
        }
        self.send_packet(packet)

    def on_packet(self, packet: dict) -> None:
        """推送数据回报"""
        self.write_log(f'public packet: {packet}')
        channel = packet.get('channel')
        if not channel:
            return

        data: dict = packet['data']
        if isinstance(data, str):
            data = json.loads(data)

        if channel == "ticker":
            self.on_ticker(data)
        elif channel == "tickers":
            self.on_tickers(data)
        elif channel.startswith('depth'):
            self.on_depth(data)
        elif channel.startswith('kline'):
            self.on_kline(data)
        elif channel == 'trade':
            self.on_trade(data)
        elif channel == 'oracle':
            self.on_oracle(data)
        elif channel == 'index':
            self.on_index(data)
        elif channel == 'funding':
            self.on_funding(data)

    def on_ticker(self, data):
        '''
        receive:
            {
              "arg": {
                "channel": "ticker",
                "symbol": "BTCUSDT"
              },
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
        '''
        pass

    def on_tickers(self, data):
        '''
        receive:
            {
              "arg": {
                "channel": "tickers"
              },
              "data": [
                {
                  "symbol": "BTCUSDT",
                  "lastPrice": "4.00000200",
                  "priceChangePercent": "-95.960"
                }
              ]
            }
        '''
        pass

    def on_depth(self, data):
        '''
        receive:
            {
              "arg": {
                "channel": "depth5",
                "symbol": "BTCUSDT"
              },
              "action": "snapshot",
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
        '''
        pass

    def on_kline(self, data):
        '''
        receive:
            {
              "arg": {
                "channel": "kline15m",
                "symbol": "BTCUSDT"
              },
              "data": {
                "0": 1499040000000,
                "1": "0.01634790",
                "2": "0.80000000",
                "3": "0.01575800",
                "4": "0.01577100",
                "5": "148976.11427815",
                "6": "2434.19055334",
                "7": 308
              }
            }
        '''
        pass

    def on_trade(self, data):
        '''
        receive:
            {
              "arg": {
                "channel": "trade",
                "symbol": "BTCUSDT"
              },
              "data": {
                "symbol": "BTCUSDT",
                "id": "28457",
                "price": "4.00000100",
                "qty": "12.00000000",
                "time": 1499865549590,
                "side": "SELL",
                "maker": false
              }
            }
        '''
        pass

    def on_oracle(self, data):
        '''
        receive:
            {
              "arg": {
                "channel": "oracle",
                "symbol": "BTCUSDT"
              },
              "data": {
                "symbol": "BTCUSDT",
                "oraclePrice": "28457",
                "time": 1499865549590
              }
            }
        '''
        pass

    def on_index(self, data):
        '''
        receive:
            {
              "arg": {
                "channel": "index",
                "symbol": "BTCUSDT"
              },
              "data": {
                "symbol": "BTCUSDT",
                "indexPrice": "28457",
                "time": 1499865549590
              }
            }
        '''
        pass

    def on_funding(self, data):
        '''
        receive:
            {
              "arg": {
                "channel": "funding",
                "symbol": "BTCUSDT"
              },
              "data": {
                "symbol": "BTCUSDT",
                "fundingRate": "0.0008",
                "time": 1499865549590
              }
            }
        '''
        pass



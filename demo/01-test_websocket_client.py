
import time
from aboard_sdk.stream import PublicWebsocketApi, PrivateWebsocketApi
from aboard_sdk.client import AboardRestAPi, WEBSOCKET_TRADE_HOST, WEBSOCKET_DATA_HOST, HOST


class PrivateApi(PrivateWebsocketApi):
    """docstring for PrivateApi"""

    def on_account(self, packet: dict) -> None:
        print(packet)

    def on_position(self, packet: dict) -> None:
        print(packet)

    def on_order(self, packet: dict) -> None:
        print(packet)


class PublicApi(PublicWebsocketApi):
    """docstring for PublicApi"""

    def __init__(self):
        super(PublicApi, self).__init__()

    def on_ticker(self, data):
        print('on_ticker', data)

    def on_tickers(self, data):
        print('on_tickers', data)

    def on_depth(self, data):
        print('on_depth', data)

    def on_kline(self, data):
        print('on_kline', data)

    def on_trade(self, data):
        print('on_trade', data)

    def on_oracle(self, data):
        print('on_oracle', data)

    def on_index(self, data):
        print('on_index', data)

    def on_funding(self, data):
        print('on_funding', data)


def main():

    address = 'xxxx'
    private_key = 'xxxx'
    proxy_host = ''
    proxy_port = 0

    client = AboardRestAPi()
    client.connect(address, private_key, proxy_host, proxy_port)

    # private trade websocket
    # token = client.token
    # print('token: ', token)
    # websocket_trade_host = WEBSOCKET_TRADE_HOST.format(HOST)
    # trade_api = PrivateApi()
    # trade_api.connect(websocket_trade_host, token, proxy_host, proxy_port)

    # while not trade_api.connected:  # wait for websocket connected
    #     time.sleep(0.1)

    # symbol = 'BTC-USDC'
    # trade_api.subscribe_account()  # then subscribe private data
    # trade_api.subscribe_position(symbol)
    # trade_api.subscribe_order(symbol)

    # time.sleep(3)

    # clientOrderId = 'manual-349960229'
    # req = {
    #     'symbol': 'BTC-USDC',
    #     'side': 'SELL',
    #     'type': 'LIMIT',
    #     'price': 1001,
    #     'quantity': 0.01,
    #     'clientOrderId': clientOrderId,
    # }
    # res = client.send_order(req)
    # print(res)

    # time.sleep(3)

    # public websocket
    websocket_data_host = WEBSOCKET_DATA_HOST.format(HOST)
    public_api = PublicApi()
    public_api.connect(websocket_data_host, proxy_host, proxy_port)
    while not public_api.connected:  # wait for websocket connected
        time.sleep(0.1)

    symbol = 'BTC-USDC'
    public_api.subscribe_all_tickers()
    public_api.subscribe_ticker(symbol)
    public_api.subscribe_depth(symbol, level=5)
    public_api.subscribe_kline(symbol, bar='1m')
    public_api.subscribe_trade(symbol)
    public_api.subscribe_oracle(symbol)
    public_api.subscribe_index(symbol)
    public_api.subscribe_funding(symbol)

    while True:
        time.sleep(10)


if __name__ == '__main__':
    main()

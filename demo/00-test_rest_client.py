import time
from aboard_sdk.client import AboardRestAPi
from aboard_sdk.wallet import Wallet


def main():
    client = AboardRestAPi()

    address = 'xxxxx'
    private_key = 'xxxxxx'
    proxy_host = ''
    proxy_port = 0

    host = 'https://api.aboard.exchange/arbitrum'
    # host = 'https://api.aboard.exchange/avalanche'
    client.connect(address, private_key, proxy_host, proxy_port, host)

    # ------------------------------------
    # res = client.get_position()
    # print(res)

    # ------------------------------------
    res = client.get_account()
    print(res)

    # ------------------------------------
    # req = {
    #         "symbol": "BTC-USDC",
    #     }
    # res = client.get_trading_fee(req)
    # print(res)

    # ------------------------------------
    # req = {
    #     "symbol": "",
    #     "billType": "",
    #     "startTime": 0,
    #     "endTime": 0,
    #     "limit": 100,
    # }
    # res = client.get_bills(req)
    # print(res)

    # --------------- withdraw ---------------------
    # req = {
    #     "asset": "USDC",
    #     "amount": "11",
    #     # destination only support the same withdraw address
    #     "destination": "xxxx",
    # }
    # client.connect(address, private_key, proxy_host, proxy_port, host)
    # res = client.request_withdrawal(req)
    # print(res)
    # signature = res['data']['signature']
    # withdrawId = res['data']['withdrawId']
    # timestamp = res['data']['expiringTimestamp']

    # wallet = Wallet()
    # wallet.connect('arbitrum', private_key=private_key)
    # res = wallet.withdraw(token_symbol=req['asset'], amount=req['amount'], withdrawid=withdrawId, timestamp=timestamp, **signature, )
    # print(res)

    # ------------------------------------
    # req = {
    #     "symbol": "BTC-USDC",  #
    #     'orderId': '000000004404431'
    # }
    # res = client.get_order(req)
    # print(res)

    # ------------------------------------
    # req = {
    #     'symbol': 'BTC-USDC'
    # }
    # res = client.get_open_orders(req)
    # print(res)
    # res = client.get_open_orders()
    # print(res)

    # ------------------------------------
    # req = {
    #     'symbol': 'BTC-USDC'
    # }
    # res = client.get_history_trades(req)
    # print(res)

    # ------------------------------------
    # req = {
    #     'symbol': 'BTC-USDC'
    # }
    # res = client.get_history_orders(req)
    # print(res)

    # ------------------------------------
    # req = {
    #     'symbol': 'BTC-USDC',
    #     'side': 'BUY',
    #     'type': 'LIMIT',
    #     'price': 1001,
    #     'quantity': 1,
    #     'clientOrderId': 'manual-34996022',
    # }
    # res = client.send_order(req)
    # print(res)

    # ------------------------------------
    # req = {
    #     'symbol': 'ETH-USDC',
    #     'clientOrderId': 'manual-34996022',
    #     'orderId': '000000004404432',
    # }
    # res = client.cancel_order(req)
    # print(res)

    # res = client.get_tickers()
    # print(res)

    # ------------------------------------
    # req = {"symbol": "BTC-USDC"}
    # res = client.get_ticker(req)
    # print(res)

    # ------------------------------------
    # req = {
    #         "symbol": "BTC-USDC",  #
    #         "limit": 20
    #     }
    # res = client.get_depth(req)
    # print(res)

    # ------------------------------------
    # req = {
    #     "symbol": "BTC-USDC",  #
    #     "interval": "15m",  #
    #     "startTime": 0,
    #     "endTime": 0,
    #     "limit": 100
    # }
    # res = client.get_klines(req)
    # print(res)

    # ------------------------------------
    # req = {
    #     "symbol": "BTC-USDC",  #
    # }
    # res = client.get_trades(req)
    # print(res)

    # res = client.get_index_oracle_funding()
    # print(res)

    # ------------------------------------
    # req = {
    #         "symbol": "BTC-USDC",
    #         "startTime": 0,
    #         "endTime": 0,
    #         "limit": 100
    #     }
    # res = client.get_history_funding_rate(req)
    # print(res)

    # ------------------------------------
    # req = {
    #         "symbol": "BTC-USDC",
    #         "startTime": 0,
    #         "endTime": 0,
    #         "limit": 100
    #     }
    # res = client.get_history_insurance_fund(req)
    # print(res)

    # res = client.get_instruments()
    # print(res)

    time.sleep(100)
    client.stop()


if __name__ == '__main__':
    main()

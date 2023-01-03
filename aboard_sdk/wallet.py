import web3
from web3 import Web3
from web3.middleware import geth_poa_middleware
import json
from typing import Optional, Dict, List
import os

GAS_LIMIT = 1220000
ARBITRUM_TESTNET_URL = "https://rinkeby.arbitrum.io/rpc"
ARBITRUM_MAINNET_URL = "https://arb1.arbitrum.io/rpc"
BSC_TESTNET_URL = 'https://data-seed-prebsc-1-s1.binance.org:8545'
BSC_MAINNET_URL = 'https://bsc-dataseed.binance.org/'
APPROVE_AMOUNT = "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"

prodContractAddressMap = {"arbitrum": "0xf06dbfa371ced8796baf15ec37e2ea35cdae42b4",
                          "bsc": "0xf06dbfa371ced8796baf15ec37e2ea35cdae42b4"
                          }
testContractAddressMap = {"arbitrum": "0x6f2B2451A98ADC50e998ABd36347e7D7e10bC0E0",
                          "bsc": "0x8437CF451076A27b74D72A2dEBC189331431377B",
                          }

# /contract address
ardata = {
    'Decimals': 6,
    'Symbol': "USDC",
    'TokenAddress': "0xff970a61a04b1ca14834a43f5de4533ebddb5cc8",
}
bscData = {
    'Decimals': 18,
    'Symbol': "BUSD",
    'TokenAddress': "0xe9e7cea3dedca5984780bafc599bd69add087d56",
}

testArbitrumData = {
    'Decimals': 6,
    'Symbol': "USDC",
    'TokenAddress': "0x3a7836b4499ee6aabd1793eb539784e3fa3e8075",
}

testBscData = {
    'Decimals': 18,
    'Symbol': "BUSD",
    'TokenAddress': "0xb3a4ec7d0b14b57002a8afbf352e3779187dd971",
}

RPC_URL = dict(
    arbitrum_test="https://rinkeby.arbitrum.io/rpc",
    arbitrum="https://arb1.arbitrum.io/rpc",
    avalanche='https://api.avax.network/ext/bc/C/rpc',
    avalanche_test='https://api.avax-test.network/ext/bc/C/rpc',
)

ABOARD_CONTRACT_ADDRESS = dict(
    arbitrum_test="0x6f2B2451A98ADC50e998ABd36347e7D7e10bC0E0",
    arbitrum="0xf06dbfa371ced8796baf15ec37e2ea35cdae42b4",
    avalanche='0xd8b0D18faE7eA29F2AD95d01FFb479E0021a9A5e',
    avalanche_test='0x6f2B2451A98ADC50e998ABd36347e7D7e10bC0E0',
)

TOKEN_DATA = {
    'arbitrum': {
        'ETH': {'TokenAddress': '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE', 'Decimal': 18, 'Symbol': 'ETH'},
        'WBTC': {'TokenAddress': '0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f', 'Decimal': 8, 'Symbol': 'WBTC'},
        'USDT': {'TokenAddress': '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9', 'Decimal': 6, 'Symbol': 'USDT'},
        'USDC': {'TokenAddress': '0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8', 'Decimal': 6, 'Symbol': 'USDC'},
    },
    'avalanche': {
        'AVAX': {'TokenAddress': '0x0000000000000000000000000000000000000000', 'Decimals': 18, 'Symbol': 'AVAX', },
        'BTC.b': {'TokenAddress': '0x152b9d0FdC40C096757F570A51E494bd4b943E50', 'Decimals': 8, 'Symbol': 'BTC.b', },
        'WETH.e': {'TokenAddress': '0x49D5c2BdFfac6CE2BFdB6640F4F80f226bc10bAB', 'Decimals': 18, 'Symbol': 'WETH.e', },
        'USDT': {'TokenAddress': '0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7', 'Decimals': 6, 'Symbol': 'USDT', },
        'USDC': {'TokenAddress': '0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E', 'Decimals': 6, 'Symbol': 'USDC', },
    },
    'avalanche_test': {
        'AVAX': {'TokenAddress': '0x0000000000000000000000000000000000000000', 'Decimals': 18, 'Symbol': 'AVAX', },
        # 'BTC.b': {'TokenAddress': '0x152b9d0FdC40C096757F570A51E494bd4b943E50', 'Decimals': 8, 'Symbol': 'BTC.b', },
        # 'WETH.e': {'TokenAddress': '0x49D5c2BdFfac6CE2BFdB6640F4F80f226bc10bAB', 'Decimals': 18, 'Symbol': 'WETH.e', },
        # 'USDT': {'TokenAddress': '0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7', 'Decimals': 6, 'Symbol': 'USDT', },
        'USDC': {'TokenAddress': '0x71b30e9c54662036c48f2F5bA1ed5F37b6411905', 'Decimals': 6, 'Symbol': 'USDC', },
    },
}


class Wallet(object):
    def __init__(self):
        self.private_key = ''
        self.account = None
        self.token_data = None
        self.contract_address = None
        self.usdc_abi = None
        self.aboard_abi = None

    def connect(self, chain_name: str = 'arbitrum', private_key: str = ''):
        '''
        chain_name: avalanche / arbitrum
        '''

        rpc_url = RPC_URL[chain_name]
        self.contract_address = ABOARD_CONTRACT_ADDRESS[chain_name]
        self.token_data = TOKEN_DATA[chain_name]
        self.private_key = private_key
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.account = self.w3.eth.account.from_key(self.private_key)
        print('connected: ', self.w3.isConnected())

        self.load_abi()
        print('load abi. ')

    def approve(self, token_symbol):
        usdc_contract_address = self.token_data[token_symbol]['TokenAddress']
        usdc_contract = self.w3.eth.contract(
            self.w3.toChecksumAddress(usdc_contract_address), abi=self.usdc_abi)
        # approve
        account = self.account.address
        nonce = self.w3.eth.get_transaction_count(account)
        transaction = usdc_contract.functions.approve(self.contract_address, int(
            APPROVE_AMOUNT, 16)).buildTransaction({'nonce': nonce, 'from': account, })
        signed_txn = self.w3.eth.account.sign_transaction(
            transaction, self.private_key)
        res = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return res

    # def deposit(self, amount):
    def deposit(self, token_symbol, amount):
        contract = self.w3.eth.contract(self.w3.toChecksumAddress(
            self.contract_address), abi=self.aboard_abi)
        account = self.account.address
        nonce = self.w3.eth.get_transaction_count(account)
        deposit_amount = amount * 10**self.token_data[token_symbol]['Decimals']
        transaction = contract.functions.deposit(
            account, token_symbol, deposit_amount).buildTransaction({'nonce': nonce, 'from': account, })
        signed_txn = self.w3.eth.account.sign_transaction(
            transaction, self.private_key)
        res = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return res

    def withdraw(self, token_symbol, amount, withdrawid, timestamp, r, s, v, ):
        '''
        withdraw use rest request
        '''
        contract = self.w3.eth.contract(self.w3.toChecksumAddress(
            self.contract_address), abi=self.aboard_abi)
        account = self.account.address
        nonce = self.w3.eth.get_transaction_count(account)
        amount = amount * 10**self.token_data[token_symbol]['Decimals']

        withdrawid = int(withdrawid)
        r = Web3.toBytes(hexstr=r)
        s = Web3.toBytes(hexstr=s)
        v = Web3.toInt(hexstr=v)
        # print(r,s,v)
        # v = int(v, 16)

        transaction = contract.functions.withdraw(
            token_symbol, amount, withdrawid, timestamp, r, s, v).buildTransaction({'nonce': nonce, 'from': account, })
        signed_txn = self.w3.eth.account.sign_transaction(
            transaction, self.private_key)
        res = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        # breakpoint()
        return res

    def load_abi(self):
        path = os.path.split(__file__)[0]
        with open(os.path.join(path, 'abi/BEP20Token_usdc_abi.json'), 'r') as f:
            abi = json.load(f)
        self.usdc_abi = abi['abi']
        with open(os.path.join(path, 'abi/aboard_abi.json'), 'r') as f:
            abi = json.load(f)
        self.aboard_abi = abi

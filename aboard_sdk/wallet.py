import web3
from web3 import Web3
from web3.middleware import geth_poa_middleware
import json
from typing import Optional, Dict, List
import os

GAS_LIMIT = 1220000
ARBITRUM_TESTNET_URL = "https://rinkeby.arbitrum.io/rpc";
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


class Wallet(object):
    def __init__(self):
        super(Wallet, self).__init__()
        self.private_key = ''
        self.account = None
        self.token_data = None
        self.contract_address = None
        self.usdc_abi = None
        self.aboard_abi = None

    def connect(self, chain_name: str='bsc', chain_type: str='test', private_key: str=''):
        '''
        chain_type: test / main
        chain_name: bsc / arbitrum
        '''
        if chain_type == 'test':
            contract_address = testContractAddressMap[chain_name]
            if chain_name == 'arbitrum':
                token_data = testArbitrumData
                url = ARBITRUM_TESTNET_URL
            else:
                token_data = testBscData
                url = BSC_TESTNET_URL
        else:
            contract_address = prodContractAddressMap[chain_name]
            if chain_name == 'arbitrum':
                token_data = ardata
                url = ARBITRUM_MAINNET_URL
            else:
                token_data = bscData
                url = BSC_MAINNET_URL

        self.contract_address = contract_address
        self.token_data = token_data
        self.private_key = private_key
        self.w3 = Web3(Web3.HTTPProvider(url))
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.account = self.w3.eth.account.from_key(self.private_key)
        print('connected: ', self.w3.isConnected())

        self.load_abi()
        print('load abi. ')

    def approve(self):
        usdc_contract_address = self.token_data['TokenAddress']
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

    def deposit(self, amount):
        contract = self.w3.eth.contract(self.w3.toChecksumAddress(
            self.contract_address), abi=self.aboard_abi)
        account = self.account.address
        nonce = self.w3.eth.get_transaction_count(account)
        deposit_amount = amount * 10**self.token_data['Decimals']
        transaction = contract.functions.deposit(
            account, deposit_amount).buildTransaction({'nonce': nonce, 'from': account, })
        signed_txn = self.w3.eth.account.sign_transaction(
            transaction, self.private_key)
        res = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return res

    def withdraw(self, amount):
        '''
        withdraw use rest request
        '''
        pass

    def load_abi(self):
        path = os.path.split(__file__)[0]
        with open(os.path.join(path, 'abi/BEP20Token_usdc_abi.json'), 'r') as f:
            abi = json.load(f)
        self.usdc_abi = abi['abi']
        with open(os.path.join(path, 'abi/aboard_abi.json'), 'r') as f:
            abi = json.load(f)
        self.aboard_abi = abi['abi']

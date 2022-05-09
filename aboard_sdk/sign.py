from web3.auto import w3
from eth_account.messages import encode_defunct

def web3_sign(private_key, msg):
    # private_key = private_key
    private_key = bytes(bytearray.fromhex(private_key))
    message = encode_defunct(text=msg)
    # breakpoint()
    signed_message = w3.eth.account.sign_message(
        message, private_key=private_key)
    signed_message = signed_message.signature.hex()
    return signed_message

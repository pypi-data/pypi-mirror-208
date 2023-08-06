from eth_typing import ChecksumAddress


def get_enable_module_typed_data(safe_address: ChecksumAddress,
                                 chain_id: int,
                                 enable_module_tx_data: str) -> dict:
    types = {
        "EIP712Domain": [{"name": "chainId", "type": "uint256"}, {"name": "verifyingContract", "type": "address"}],
        "SafeTx": [
            {"name": "to", "type": "address"},
            {"name": "value", "type": "uint256"},
            {"name": "data", "type": "bytes"},
            {"name": "operation", "type": "uint8"},
            {"name": "safeTxGas", "type": "uint256"},
            {"name": "baseGas", "type": "uint256"},
            {"name": "gasPrice", "type": "uint256"},
            {"name": "gasToken", "type": "address"},
            {"name": "refundReceiver", "type": "address"},
            {"name": "nonce", "type": "uint256"},
        ],
    }
    message = {
        "to": safe_address,
        "value": 0,
        "data": bytes.fromhex(enable_module_tx_data[2:]),
        "operation": 0,
        "safeTxGas": 0,
        "baseGas": 0,
        "dataGas": 0,
        "gasPrice": 0,
        "gasToken": '0x0000000000000000000000000000000000000000',
        "refundReceiver": '0x0000000000000000000000000000000000000000',
        "nonce": 0,
    }

    payload = {
        "types": types,
        "primaryType": "SafeTx",
        "domain": {"verifyingContract": safe_address, "chainId": chain_id},
        "message": message,
    }

    return payload

from typing import Optional, Union, List, TypedDict
from eth_typing import Address, ChecksumAddress
from web3 import Web3
from web3.types import TxParams
from eulith_web3.contract_bindings.pendle.swap_data import SwapData
from eulith_web3.contract_bindings.pendle.token_input import TokenInput
from eulith_web3.contract_bindings.pendle.approx_params import ApproxParams
from eulith_web3.contract_bindings.pendle.token_output import TokenOutput


def serialize_struct(d) -> tuple:
    if isinstance(d, dict):
        return tuple(serialize_struct(v) for v in d.values())
    elif isinstance(d, (list, tuple)):
        return tuple(serialize_struct(x) for x in d)
    else:
        return d


class ContractAddressNotSet(Exception):
    pass


class IPActionMintRedeem:
    def __init__(self, web3: Web3, contract_address: Optional[Union[Address, ChecksumAddress]] = None):
        self.address: Optional[Union[Address, ChecksumAddress]] = contract_address
        self.abi = [{'anonymous': False, 'inputs': [{'indexed': True, 'internalType': 'address', 'name': 'caller', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'receiver', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'YT', 'type': 'address'}, {'indexed': False, 'internalType': 'uint256', 'name': 'netSyIn', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'netPyOut', 'type': 'uint256'}], 'name': 'MintPyFromSy', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': True, 'internalType': 'address', 'name': 'caller', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'tokenIn', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'YT', 'type': 'address'}, {'indexed': False, 'internalType': 'address', 'name': 'receiver', 'type': 'address'}, {'indexed': False, 'internalType': 'uint256', 'name': 'netTokenIn', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'netPyOut', 'type': 'uint256'}], 'name': 'MintPyFromToken', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': True, 'internalType': 'address', 'name': 'caller', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'tokenIn', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'SY', 'type': 'address'}, {'indexed': False, 'internalType': 'address', 'name': 'receiver', 'type': 'address'}, {'indexed': False, 'internalType': 'uint256', 'name': 'netTokenIn', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'netSyOut', 'type': 'uint256'}], 'name': 'MintSyFromToken', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': True, 'internalType': 'address', 'name': 'caller', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'receiver', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'YT', 'type': 'address'}, {'indexed': False, 'internalType': 'uint256', 'name': 'netPyIn', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'netSyOut', 'type': 'uint256'}], 'name': 'RedeemPyToSy', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': True, 'internalType': 'address', 'name': 'caller', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'tokenOut', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'YT', 'type': 'address'}, {'indexed': False, 'internalType': 'address', 'name': 'receiver', 'type': 'address'}, {'indexed': False, 'internalType': 'uint256', 'name': 'netPyIn', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'netTokenOut', 'type': 'uint256'}], 'name': 'RedeemPyToToken', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': True, 'internalType': 'address', 'name': 'caller', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'tokenOut', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'SY', 'type': 'address'}, {'indexed': False, 'internalType': 'address', 'name': 'receiver', 'type': 'address'}, {'indexed': False, 'internalType': 'uint256', 'name': 'netSyIn', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'netTokenOut', 'type': 'uint256'}], 'name': 'RedeemSyToToken', 'type': 'event'}, {'inputs': [{'internalType': 'address', 'name': 'receiver', 'type': 'address'}, {'internalType': 'address', 'name': 'YT', 'type': 'address'}, {'internalType': 'uint256', 'name': 'netSyIn', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'minPyOut', 'type': 'uint256'}], 'name': 'mintPyFromSy', 'outputs': [{'internalType': 'uint256', 'name': 'netPyOut', 'type': 'uint256'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'receiver', 'type': 'address'}, {'internalType': 'address', 'name': 'YT', 'type': 'address'}, {'internalType': 'uint256', 'name': 'minPyOut', 'type': 'uint256'}, {'components': [{'internalType': 'address', 'name': 'tokenIn', 'type': 'address'}, {'internalType': 'uint256', 'name': 'netTokenIn', 'type': 'uint256'}, {'internalType': 'address', 'name': 'tokenMintSy', 'type': 'address'}, {'internalType': 'address', 'name': 'bulk', 'type': 'address'}, {'internalType': 'address', 'name': 'pendleSwap', 'type': 'address'}, {'components': [{'internalType': 'enum SwapType', 'name': 'swapType', 'type': 'uint8'}, {'internalType': 'address', 'name': 'extRouter', 'type': 'address'}, {'internalType': 'bytes', 'name': 'extCalldata', 'type': 'bytes'}, {'internalType': 'bool', 'name': 'needScale', 'type': 'bool'}], 'internalType': 'struct SwapData', 'name': 'swapData', 'type': 'tuple'}], 'internalType': 'struct TokenInput', 'name': 'input', 'type': 'tuple'}], 'name': 'mintPyFromToken', 'outputs': [{'internalType': 'uint256', 'name': 'netPyOut', 'type': 'uint256'}], 'stateMutability': 'payable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'receiver', 'type': 'address'}, {'internalType': 'address', 'name': 'SY', 'type': 'address'}, {'internalType': 'uint256', 'name': 'minSyOut', 'type': 'uint256'}, {'components': [{'internalType': 'address', 'name': 'tokenIn', 'type': 'address'}, {'internalType': 'uint256', 'name': 'netTokenIn', 'type': 'uint256'}, {'internalType': 'address', 'name': 'tokenMintSy', 'type': 'address'}, {'internalType': 'address', 'name': 'bulk', 'type': 'address'}, {'internalType': 'address', 'name': 'pendleSwap', 'type': 'address'}, {'components': [{'internalType': 'enum SwapType', 'name': 'swapType', 'type': 'uint8'}, {'internalType': 'address', 'name': 'extRouter', 'type': 'address'}, {'internalType': 'bytes', 'name': 'extCalldata', 'type': 'bytes'}, {'internalType': 'bool', 'name': 'needScale', 'type': 'bool'}], 'internalType': 'struct SwapData', 'name': 'swapData', 'type': 'tuple'}], 'internalType': 'struct TokenInput', 'name': 'input', 'type': 'tuple'}], 'name': 'mintSyFromToken', 'outputs': [{'internalType': 'uint256', 'name': 'netSyOut', 'type': 'uint256'}], 'stateMutability': 'payable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'user', 'type': 'address'}, {'internalType': 'address[]', 'name': 'sys', 'type': 'address[]'}, {'internalType': 'address[]', 'name': 'yts', 'type': 'address[]'}, {'internalType': 'address[]', 'name': 'markets', 'type': 'address[]'}], 'name': 'redeemDueInterestAndRewards', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'receiver', 'type': 'address'}, {'internalType': 'address', 'name': 'YT', 'type': 'address'}, {'internalType': 'uint256', 'name': 'netPyIn', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'minSyOut', 'type': 'uint256'}], 'name': 'redeemPyToSy', 'outputs': [{'internalType': 'uint256', 'name': 'netSyOut', 'type': 'uint256'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'receiver', 'type': 'address'}, {'internalType': 'address', 'name': 'YT', 'type': 'address'}, {'internalType': 'uint256', 'name': 'netPyIn', 'type': 'uint256'}, {'components': [{'internalType': 'address', 'name': 'tokenOut', 'type': 'address'}, {'internalType': 'uint256', 'name': 'minTokenOut', 'type': 'uint256'}, {'internalType': 'address', 'name': 'tokenRedeemSy', 'type': 'address'}, {'internalType': 'address', 'name': 'bulk', 'type': 'address'}, {'internalType': 'address', 'name': 'pendleSwap', 'type': 'address'}, {'components': [{'internalType': 'enum SwapType', 'name': 'swapType', 'type': 'uint8'}, {'internalType': 'address', 'name': 'extRouter', 'type': 'address'}, {'internalType': 'bytes', 'name': 'extCalldata', 'type': 'bytes'}, {'internalType': 'bool', 'name': 'needScale', 'type': 'bool'}], 'internalType': 'struct SwapData', 'name': 'swapData', 'type': 'tuple'}], 'internalType': 'struct TokenOutput', 'name': 'output', 'type': 'tuple'}], 'name': 'redeemPyToToken', 'outputs': [{'internalType': 'uint256', 'name': 'netTokenOut', 'type': 'uint256'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'receiver', 'type': 'address'}, {'internalType': 'address', 'name': 'SY', 'type': 'address'}, {'internalType': 'uint256', 'name': 'netSyIn', 'type': 'uint256'}, {'components': [{'internalType': 'address', 'name': 'tokenOut', 'type': 'address'}, {'internalType': 'uint256', 'name': 'minTokenOut', 'type': 'uint256'}, {'internalType': 'address', 'name': 'tokenRedeemSy', 'type': 'address'}, {'internalType': 'address', 'name': 'bulk', 'type': 'address'}, {'internalType': 'address', 'name': 'pendleSwap', 'type': 'address'}, {'components': [{'internalType': 'enum SwapType', 'name': 'swapType', 'type': 'uint8'}, {'internalType': 'address', 'name': 'extRouter', 'type': 'address'}, {'internalType': 'bytes', 'name': 'extCalldata', 'type': 'bytes'}, {'internalType': 'bool', 'name': 'needScale', 'type': 'bool'}], 'internalType': 'struct SwapData', 'name': 'swapData', 'type': 'tuple'}], 'internalType': 'struct TokenOutput', 'name': 'output', 'type': 'tuple'}], 'name': 'redeemSyToToken', 'outputs': [{'internalType': 'uint256', 'name': 'netTokenOut', 'type': 'uint256'}], 'stateMutability': 'nonpayable', 'type': 'function'}]
        self.bytecode = ''
        self.w3 = web3
            
    def deploy(self):
        contract = self.w3.eth.contract(abi=self.abi, bytecode=self.bytecode)
        tx_hash = contract.constructor().transact()
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        self.address = tx_receipt.contractAddress
        
    def mint_py_from_sy(self, receiver: str, y_t: str, net_sy_in: int, min_py_out: int, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.mintPyFromSy(receiver, y_t, net_sy_in, min_py_out).build_transaction(override_tx_parameters)

    def mint_py_from_token(self, receiver: str, y_t: str, min_py_out: int, input: TokenInput, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.mintPyFromToken(receiver, y_t, min_py_out, serialize_struct(input)).build_transaction(override_tx_parameters)

    def mint_sy_from_token(self, receiver: str, s_y: str, min_sy_out: int, input: TokenInput, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.mintSyFromToken(receiver, s_y, min_sy_out, serialize_struct(input)).build_transaction(override_tx_parameters)

    def redeem_due_interest_and_rewards(self, user: str, sys: List[str], yts: List[str], markets: List[str], override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.redeemDueInterestAndRewards(user, sys, yts, markets).build_transaction(override_tx_parameters)

    def redeem_py_to_sy(self, receiver: str, y_t: str, net_py_in: int, min_sy_out: int, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.redeemPyToSy(receiver, y_t, net_py_in, min_sy_out).build_transaction(override_tx_parameters)

    def redeem_py_to_token(self, receiver: str, y_t: str, net_py_in: int, output: TokenOutput, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.redeemPyToToken(receiver, y_t, net_py_in, serialize_struct(output)).build_transaction(override_tx_parameters)

    def redeem_sy_to_token(self, receiver: str, s_y: str, net_sy_in: int, output: TokenOutput, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.redeemSyToToken(receiver, s_y, net_sy_in, serialize_struct(output)).build_transaction(override_tx_parameters)

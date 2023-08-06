from typing import Optional, Union, List, TypedDict
from eth_typing import Address, ChecksumAddress
from web3 import Web3
from web3.types import TxParams
from eulith_web3.contract_bindings.pendle.swap_data import SwapData
from eulith_web3.contract_bindings.pendle.token_input import TokenInput
from eulith_web3.contract_bindings.pendle.approx_params import ApproxParams
from eulith_web3.contract_bindings.pendle.token_output import TokenOutput
from eulith_web3.contract_bindings.pendle.multi_approval import MultiApproval
from eulith_web3.contract_bindings.pendle.call3 import Call3


def serialize_struct(d) -> tuple:
    if isinstance(d, dict):
        return tuple(serialize_struct(v) for v in d.values())
    elif isinstance(d, (list, tuple)):
        return tuple(serialize_struct(x) for x in d)
    else:
        return d


class ContractAddressNotSet(Exception):
    pass


class IPBulkSeller:
    def __init__(self, web3: Web3, contract_address: Optional[Union[Address, ChecksumAddress]] = None):
        self.address: Optional[Union[Address, ChecksumAddress]] = contract_address
        self.abi = [{'anonymous': False, 'inputs': [{'indexed': False, 'internalType': 'uint256', 'name': 'newFeeRate', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'oldFeeRate', 'type': 'uint256'}], 'name': 'FeeRateUpdated', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': False, 'internalType': 'uint256', 'name': 'newRateTokenToSy', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'newRateSyToToken', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'oldRateTokenToSy', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'oldRateSyToToken', 'type': 'uint256'}], 'name': 'RateUpdated', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': False, 'internalType': 'uint256', 'name': 'netSyRedeem', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'netTokenFromSy', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'newTokenProp', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'oldTokenProp', 'type': 'uint256'}], 'name': 'ReBalanceSyToToken', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': False, 'internalType': 'uint256', 'name': 'netTokenDeposit', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'netSyFromToken', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'newTokenProp', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'oldTokenProp', 'type': 'uint256'}], 'name': 'ReBalanceTokenToSy', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': False, 'internalType': 'uint256', 'name': 'totalToken', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'totalSy', 'type': 'uint256'}], 'name': 'ReserveUpdated', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': False, 'internalType': 'address', 'name': 'receiver', 'type': 'address'}, {'indexed': False, 'internalType': 'uint256', 'name': 'netSyIn', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'netTokenOut', 'type': 'uint256'}], 'name': 'SwapExactSyForToken', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': False, 'internalType': 'address', 'name': 'receiver', 'type': 'address'}, {'indexed': False, 'internalType': 'uint256', 'name': 'netTokenIn', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'netSyOut', 'type': 'uint256'}], 'name': 'SwapExactTokenForSy', 'type': 'event'}, {'inputs': [], 'name': 'SY', 'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'readState', 'outputs': [{'components': [{'internalType': 'uint256', 'name': 'rateTokenToSy', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'rateSyToToken', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'totalToken', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'totalSy', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'feeRate', 'type': 'uint256'}], 'internalType': 'struct BulkSellerState', 'name': '', 'type': 'tuple'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'receiver', 'type': 'address'}, {'internalType': 'uint256', 'name': 'exactSyIn', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'minTokenOut', 'type': 'uint256'}, {'internalType': 'bool', 'name': 'swapFromInternalBalance', 'type': 'bool'}], 'name': 'swapExactSyForToken', 'outputs': [{'internalType': 'uint256', 'name': 'netTokenOut', 'type': 'uint256'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'receiver', 'type': 'address'}, {'internalType': 'uint256', 'name': 'netTokenIn', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'minSyOut', 'type': 'uint256'}], 'name': 'swapExactTokenForSy', 'outputs': [{'internalType': 'uint256', 'name': 'netSyOut', 'type': 'uint256'}], 'stateMutability': 'payable', 'type': 'function'}, {'inputs': [], 'name': 'token', 'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}], 'stateMutability': 'view', 'type': 'function'}]
        self.bytecode = ''
        self.w3 = web3
            
    def deploy(self):
        contract = self.w3.eth.contract(abi=self.abi, bytecode=self.bytecode)
        tx_hash = contract.constructor().transact()
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        self.address = tx_receipt.contractAddress
        
    def s_y(self) -> str:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.SY().call()

    def read_state(self) -> tuple:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.readState().call()

    def swap_exact_sy_for_token(self, receiver: str, exact_sy_in: int, min_token_out: int, swap_from_internal_balance: bool, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.swapExactSyForToken(receiver, exact_sy_in, min_token_out, swap_from_internal_balance).build_transaction(override_tx_parameters)

    def swap_exact_token_for_sy(self, receiver: str, net_token_in: int, min_sy_out: int, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.swapExactTokenForSy(receiver, net_token_in, min_sy_out).build_transaction(override_tx_parameters)

    def token(self) -> str:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.token().call()

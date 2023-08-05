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


class IPActionMisc:
    def __init__(self, web3: Web3, contract_address: Optional[Union[Address, ChecksumAddress]] = None):
        self.address: Optional[Union[Address, ChecksumAddress]] = contract_address
        self.abi = [{'inputs': [{'components': [{'internalType': 'address[]', 'name': 'tokens', 'type': 'address[]'}, {'internalType': 'address', 'name': 'spender', 'type': 'address'}], 'internalType': 'struct IPActionMisc.MultiApproval[]', 'name': '', 'type': 'tuple[]'}], 'name': 'approveInf', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'components': [{'internalType': 'bool', 'name': 'allowFailure', 'type': 'bool'}, {'internalType': 'bytes', 'name': 'callData', 'type': 'bytes'}], 'internalType': 'struct IPActionMisc.Call3[]', 'name': 'calls', 'type': 'tuple[]'}], 'name': 'batchExec', 'outputs': [{'components': [{'internalType': 'bool', 'name': 'success', 'type': 'bool'}, {'internalType': 'bytes', 'name': 'returnData', 'type': 'bytes'}], 'internalType': 'struct IPActionMisc.Result[]', 'name': 'returnData', 'type': 'tuple[]'}], 'stateMutability': 'nonpayable', 'type': 'function'}]
        self.bytecode = ''
        self.w3 = web3
            
    def deploy(self):
        contract = self.w3.eth.contract(abi=self.abi, bytecode=self.bytecode)
        tx_hash = contract.constructor().transact()
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        self.address = tx_receipt.contractAddress
        
    def approve_inf(self, a0: List[MultiApproval], override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.approveInf(serialize_struct(a0)).build_transaction(override_tx_parameters)

    def batch_exec(self, calls: List[Call3], override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.batchExec(serialize_struct(calls)).build_transaction(override_tx_parameters)

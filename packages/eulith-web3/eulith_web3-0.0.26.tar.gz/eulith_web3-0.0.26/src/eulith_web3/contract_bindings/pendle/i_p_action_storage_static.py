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


class IPActionStorageStatic:
    def __init__(self, web3: Web3, contract_address: Optional[Union[Address, ChecksumAddress]] = None):
        self.address: Optional[Union[Address, ChecksumAddress]] = contract_address
        self.abi = [{'anonymous': False, 'inputs': [{'indexed': True, 'internalType': 'address', 'name': 'previousOwner', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'newOwner', 'type': 'address'}], 'name': 'OwnershipTransferred', 'type': 'event'}, {'inputs': [], 'name': 'claimOwnership', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [], 'name': 'getBulkSellerFactory', 'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'getDefaultApproxParams', 'outputs': [{'components': [{'internalType': 'uint256', 'name': 'guessMin', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'guessMax', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'guessOffchain', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'maxIteration', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'eps', 'type': 'uint256'}], 'internalType': 'struct ApproxParams', 'name': '', 'type': 'tuple'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'getOwnerAndPendingOwner', 'outputs': [{'internalType': 'address', 'name': '_owner', 'type': 'address'}, {'internalType': 'address', 'name': '_pendingOwner', 'type': 'address'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_bulkSellerFactory', 'type': 'address'}], 'name': 'setBulkSellerFactory', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'components': [{'internalType': 'uint256', 'name': 'guessMin', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'guessMax', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'guessOffchain', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'maxIteration', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'eps', 'type': 'uint256'}], 'internalType': 'struct ApproxParams', 'name': 'params', 'type': 'tuple'}], 'name': 'setDefaultApproxParams', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'newOwner', 'type': 'address'}, {'internalType': 'bool', 'name': 'direct', 'type': 'bool'}, {'internalType': 'bool', 'name': 'renounce', 'type': 'bool'}], 'name': 'transferOwnership', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}]
        self.bytecode = ''
        self.w3 = web3
            
    def deploy(self):
        contract = self.w3.eth.contract(abi=self.abi, bytecode=self.bytecode)
        tx_hash = contract.constructor().transact()
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        self.address = tx_receipt.contractAddress
        
    def claim_ownership(self, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.claimOwnership().build_transaction(override_tx_parameters)

    def get_bulk_seller_factory(self) -> str:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getBulkSellerFactory().call()

    def get_default_approx_params(self) -> tuple:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getDefaultApproxParams().call()

    def get_owner_and_pending_owner(self) -> (str, str):
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getOwnerAndPendingOwner().call()

    def set_bulk_seller_factory(self, _bulk_seller_factory: str, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.setBulkSellerFactory(_bulk_seller_factory).build_transaction(override_tx_parameters)

    def set_default_approx_params(self, params: ApproxParams, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.setDefaultApproxParams(serialize_struct(params)).build_transaction(override_tx_parameters)

    def transfer_ownership(self, new_owner: str, direct: bool, renounce: bool, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.transferOwnership(new_owner, direct, renounce).build_transaction(override_tx_parameters)

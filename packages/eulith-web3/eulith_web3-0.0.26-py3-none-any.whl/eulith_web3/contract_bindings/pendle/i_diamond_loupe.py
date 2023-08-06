from typing import Optional, Union, List, TypedDict
from eth_typing import Address, ChecksumAddress
from web3 import Web3
from web3.types import TxParams


class ContractAddressNotSet(Exception):
    pass


class IDiamondLoupe:
    def __init__(self, web3: Web3, contract_address: Optional[Union[Address, ChecksumAddress]] = None):
        self.address: Optional[Union[Address, ChecksumAddress]] = contract_address
        self.abi = [{'inputs': [{'internalType': 'bytes4', 'name': '_functionSelector', 'type': 'bytes4'}], 'name': 'facetAddress', 'outputs': [{'internalType': 'address', 'name': 'facetAddress_', 'type': 'address'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'facetAddresses', 'outputs': [{'internalType': 'address[]', 'name': 'facetAddresses_', 'type': 'address[]'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_facet', 'type': 'address'}], 'name': 'facetFunctionSelectors', 'outputs': [{'internalType': 'bytes4[]', 'name': 'facetFunctionSelectors_', 'type': 'bytes4[]'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'facets', 'outputs': [{'components': [{'internalType': 'address', 'name': 'facetAddress', 'type': 'address'}, {'internalType': 'bytes4[]', 'name': 'functionSelectors', 'type': 'bytes4[]'}], 'internalType': 'struct IDiamondLoupe.Facet[]', 'name': 'facets_', 'type': 'tuple[]'}], 'stateMutability': 'view', 'type': 'function'}]
        self.bytecode = ''
        self.w3 = web3
            
    def deploy(self):
        contract = self.w3.eth.contract(abi=self.abi, bytecode=self.bytecode)
        tx_hash = contract.constructor().transact()
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        self.address = tx_receipt.contractAddress
        
    def facet_address(self, _function_selector: None) -> str:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.facetAddress(_function_selector).call()

    def facet_addresses(self) -> List[str]:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.facetAddresses().call()

    def facet_function_selectors(self, _facet: str) -> List[None]:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.facetFunctionSelectors(_facet).call()

    def facets(self) -> List[tuple]:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.facets().call()

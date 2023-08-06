from typing import Optional, Union, List
from eth_typing import Address, ChecksumAddress
from web3 import Web3
from web3.types import TxParams


class ContractAddressNotSet(Exception):
    pass


class IRouter:
    def __init__(self, web3: Web3, contract_address: Optional[Union[Address, ChecksumAddress]] = None):
        self.address: Optional[Union[Address, ChecksumAddress]] = contract_address
        self.abi = [{'inputs': [{'internalType': 'address', 'name': '_plugin', 'type': 'address'}], 'name': 'approvePlugin', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_msgsender', 'type': 'address'}, {'internalType': 'address', 'name': '_plugin', 'type': 'address'}], 'name': 'approvedPlugins', 'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_account', 'type': 'address'}, {'internalType': 'address', 'name': '_collateralToken', 'type': 'address'}, {'internalType': 'address', 'name': '_indexToken', 'type': 'address'}, {'internalType': 'uint256', 'name': '_collateralDelta', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '_sizeDelta', 'type': 'uint256'}, {'internalType': 'bool', 'name': '_isLong', 'type': 'bool'}, {'internalType': 'address', 'name': '_receiver', 'type': 'address'}], 'name': 'pluginDecreasePosition', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_account', 'type': 'address'}, {'internalType': 'address', 'name': '_collateralToken', 'type': 'address'}, {'internalType': 'address', 'name': '_indexToken', 'type': 'address'}, {'internalType': 'uint256', 'name': '_sizeDelta', 'type': 'uint256'}, {'internalType': 'bool', 'name': '_isLong', 'type': 'bool'}], 'name': 'pluginIncreasePosition', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}, {'internalType': 'address', 'name': '_account', 'type': 'address'}, {'internalType': 'address', 'name': '_receiver', 'type': 'address'}, {'internalType': 'uint256', 'name': '_amount', 'type': 'uint256'}], 'name': 'pluginTransfer', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address[]', 'name': '_path', 'type': 'address[]'}, {'internalType': 'uint256', 'name': '_amountIn', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '_minOut', 'type': 'uint256'}, {'internalType': 'address', 'name': '_receiver', 'type': 'address'}], 'name': 'swap', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}]
        self.bytecode = ''
        self.w3 = web3
            
    def deploy(self):
        contract = self.w3.eth.contract(abi=self.abi, bytecode=self.bytecode)
        tx_hash = contract.constructor().transact()
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        self.address = tx_receipt.contractAddress
        
    def approve_plugin(self, _plugin: str, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.approvePlugin(_plugin).build_transaction(override_tx_parameters)

    def approved_plugins(self, _msgsender: str, _plugin: str) -> bool:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.approvedPlugins(_msgsender, _plugin).call()

    def plugin_decrease_position(self, _account: str, _collateral_token: str, _index_token: str, _collateral_delta: int, _size_delta: int, _is_long: bool, _receiver: str, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.pluginDecreasePosition(_account, _collateral_token, _index_token, _collateral_delta, _size_delta, _is_long, _receiver).build_transaction(override_tx_parameters)

    def plugin_increase_position(self, _account: str, _collateral_token: str, _index_token: str, _size_delta: int, _is_long: bool, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.pluginIncreasePosition(_account, _collateral_token, _index_token, _size_delta, _is_long).build_transaction(override_tx_parameters)

    def plugin_transfer(self, _token: str, _account: str, _receiver: str, _amount: int, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.pluginTransfer(_token, _account, _receiver, _amount).build_transaction(override_tx_parameters)

    def swap(self, _path: List[str], _amount_in: int, _min_out: int, _receiver: str, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.swap(_path, _amount_in, _min_out, _receiver).build_transaction(override_tx_parameters)

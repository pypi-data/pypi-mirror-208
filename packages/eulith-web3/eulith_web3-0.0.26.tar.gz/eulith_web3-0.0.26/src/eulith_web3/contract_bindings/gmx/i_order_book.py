from typing import Optional, Union, List, TypedDict
from eth_typing import Address, ChecksumAddress
from web3 import Web3
from web3.types import TxParams


class ContractAddressNotSet(Exception):
    pass


class IOrderBook:
    def __init__(self, web3: Web3, contract_address: Optional[Union[Address, ChecksumAddress]] = None):
        self.address: Optional[Union[Address, ChecksumAddress]] = contract_address
        self.abi = [{'inputs': [{'internalType': 'uint256', 'name': '_orderIndex', 'type': 'uint256'}], 'name': 'cancelDecreaseOrder', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'uint256', 'name': '_orderIndex', 'type': 'uint256'}], 'name': 'cancelIncreaseOrder', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_indexToken', 'type': 'address'}, {'internalType': 'uint256', 'name': '_sizeDelta', 'type': 'uint256'}, {'internalType': 'address', 'name': '_collateralToken', 'type': 'address'}, {'internalType': 'uint256', 'name': '_collateralDelta', 'type': 'uint256'}, {'internalType': 'bool', 'name': '_isLong', 'type': 'bool'}, {'internalType': 'uint256', 'name': '_triggerPrice', 'type': 'uint256'}, {'internalType': 'bool', 'name': '_triggerAboveThreshold', 'type': 'bool'}], 'name': 'createDecreaseOrder', 'outputs': [], 'stateMutability': 'payable', 'type': 'function'}, {'inputs': [{'internalType': 'address[]', 'name': '_path', 'type': 'address[]'}, {'internalType': 'uint256', 'name': '_amountIn', 'type': 'uint256'}, {'internalType': 'address', 'name': '_indexToken', 'type': 'address'}, {'internalType': 'uint256', 'name': '_minOut', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '_sizeDelta', 'type': 'uint256'}, {'internalType': 'address', 'name': '_collateralToken', 'type': 'address'}, {'internalType': 'bool', 'name': '_isLong', 'type': 'bool'}, {'internalType': 'uint256', 'name': '_triggerPrice', 'type': 'uint256'}, {'internalType': 'bool', 'name': '_triggerAboveThreshold', 'type': 'bool'}, {'internalType': 'uint256', 'name': '_executionFee', 'type': 'uint256'}, {'internalType': 'bool', 'name': '_shouldWrap', 'type': 'bool'}], 'name': 'createIncreaseOrder', 'outputs': [], 'stateMutability': 'payable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '', 'type': 'address'}, {'internalType': 'uint256', 'name': '', 'type': 'uint256'}, {'internalType': 'address payable', 'name': '', 'type': 'address'}], 'name': 'executeDecreaseOrder', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '', 'type': 'address'}, {'internalType': 'uint256', 'name': '', 'type': 'uint256'}, {'internalType': 'address payable', 'name': '', 'type': 'address'}], 'name': 'executeIncreaseOrder', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '', 'type': 'address'}, {'internalType': 'uint256', 'name': '', 'type': 'uint256'}, {'internalType': 'address payable', 'name': '', 'type': 'address'}], 'name': 'executeSwapOrder', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_account', 'type': 'address'}, {'internalType': 'uint256', 'name': '_orderIndex', 'type': 'uint256'}], 'name': 'getDecreaseOrder', 'outputs': [{'internalType': 'address', 'name': 'collateralToken', 'type': 'address'}, {'internalType': 'uint256', 'name': 'collateralDelta', 'type': 'uint256'}, {'internalType': 'address', 'name': 'indexToken', 'type': 'address'}, {'internalType': 'uint256', 'name': 'sizeDelta', 'type': 'uint256'}, {'internalType': 'bool', 'name': 'isLong', 'type': 'bool'}, {'internalType': 'uint256', 'name': 'triggerPrice', 'type': 'uint256'}, {'internalType': 'bool', 'name': 'triggerAboveThreshold', 'type': 'bool'}, {'internalType': 'uint256', 'name': 'executionFee', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_account', 'type': 'address'}, {'internalType': 'uint256', 'name': '_orderIndex', 'type': 'uint256'}], 'name': 'getIncreaseOrder', 'outputs': [{'internalType': 'address', 'name': 'purchaseToken', 'type': 'address'}, {'internalType': 'uint256', 'name': 'purchaseTokenAmount', 'type': 'uint256'}, {'internalType': 'address', 'name': 'collateralToken', 'type': 'address'}, {'internalType': 'address', 'name': 'indexToken', 'type': 'address'}, {'internalType': 'uint256', 'name': 'sizeDelta', 'type': 'uint256'}, {'internalType': 'bool', 'name': 'isLong', 'type': 'bool'}, {'internalType': 'uint256', 'name': 'triggerPrice', 'type': 'uint256'}, {'internalType': 'bool', 'name': 'triggerAboveThreshold', 'type': 'bool'}, {'internalType': 'uint256', 'name': 'executionFee', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_account', 'type': 'address'}, {'internalType': 'uint256', 'name': '_orderIndex', 'type': 'uint256'}], 'name': 'getSwapOrder', 'outputs': [{'internalType': 'address', 'name': 'path0', 'type': 'address'}, {'internalType': 'address', 'name': 'path1', 'type': 'address'}, {'internalType': 'address', 'name': 'path2', 'type': 'address'}, {'internalType': 'uint256', 'name': 'amountIn', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'minOut', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'triggerRatio', 'type': 'uint256'}, {'internalType': 'bool', 'name': 'triggerAboveThreshold', 'type': 'bool'}, {'internalType': 'bool', 'name': 'shouldUnwrap', 'type': 'bool'}, {'internalType': 'uint256', 'name': 'executionFee', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}]
        self.bytecode = ''
        self.w3 = web3
            
    def deploy(self):
        contract = self.w3.eth.contract(abi=self.abi, bytecode=self.bytecode)
        tx_hash = contract.constructor().transact()
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        self.address = tx_receipt.contractAddress
        
    def cancel_decrease_order(self, _order_index: int, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.cancelDecreaseOrder(_order_index).build_transaction(override_tx_parameters)

    def cancel_increase_order(self, _order_index: int, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.cancelIncreaseOrder(_order_index).build_transaction(override_tx_parameters)

    def create_decrease_order(self, _index_token: str, _size_delta: int, _collateral_token: str, _collateral_delta: int, _is_long: bool, _trigger_price: int, _trigger_above_threshold: bool, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.createDecreaseOrder(_index_token, _size_delta, _collateral_token, _collateral_delta, _is_long, _trigger_price, _trigger_above_threshold).build_transaction(override_tx_parameters)

    def create_increase_order(self, _path: List[str], _amount_in: int, _index_token: str, _min_out: int, _size_delta: int, _collateral_token: str, _is_long: bool, _trigger_price: int, _trigger_above_threshold: bool, _execution_fee: int, _should_wrap: bool, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.createIncreaseOrder(_path, _amount_in, _index_token, _min_out, _size_delta, _collateral_token, _is_long, _trigger_price, _trigger_above_threshold, _execution_fee, _should_wrap).build_transaction(override_tx_parameters)

    def execute_decrease_order(self, a0: str, a1: int, a2: None, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.executeDecreaseOrder(a0, a1, a2).build_transaction(override_tx_parameters)

    def execute_increase_order(self, a0: str, a1: int, a2: None, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.executeIncreaseOrder(a0, a1, a2).build_transaction(override_tx_parameters)

    def execute_swap_order(self, a0: str, a1: int, a2: None, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.executeSwapOrder(a0, a1, a2).build_transaction(override_tx_parameters)

    def get_decrease_order(self, _account: str, _order_index: int) -> (str, int, str, int, bool, int, bool, int):
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getDecreaseOrder(_account, _order_index).call()

    def get_increase_order(self, _account: str, _order_index: int) -> (str, int, str, str, int, bool, int, bool, int):
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getIncreaseOrder(_account, _order_index).call()

    def get_swap_order(self, _account: str, _order_index: int) -> (str, str, str, int, int, int, bool, bool, int):
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getSwapOrder(_account, _order_index).call()

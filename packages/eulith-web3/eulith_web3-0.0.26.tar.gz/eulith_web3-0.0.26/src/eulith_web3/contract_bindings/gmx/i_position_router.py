from typing import Optional, Union, List
from eth_typing import Address, ChecksumAddress
from web3 import Web3
from web3.types import TxParams


class ContractAddressNotSet(Exception):
    pass


class IPositionRouter:
    def __init__(self, web3: Web3, contract_address: Optional[Union[Address, ChecksumAddress]] = None):
        self.address: Optional[Union[Address, ChecksumAddress]] = contract_address
        self.abi = [{'anonymous': False, 'inputs': [{'indexed': True, 'internalType': 'address', 'name': 'account', 'type': 'address'}, {'indexed': False, 'internalType': 'address[]', 'name': 'path', 'type': 'address[]'}, {'indexed': False, 'internalType': 'address', 'name': 'indexToken', 'type': 'address'}, {'indexed': False, 'internalType': 'uint256', 'name': 'collateralDelta', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'sizeDelta', 'type': 'uint256'}, {'indexed': False, 'internalType': 'bool', 'name': 'isLong', 'type': 'bool'}, {'indexed': False, 'internalType': 'address', 'name': 'receiver', 'type': 'address'}, {'indexed': False, 'internalType': 'uint256', 'name': 'acceptablePrice', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'minOut', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'executionFee', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'blockGap', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'timeGap', 'type': 'uint256'}], 'name': 'CancelDecreasePosition', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': True, 'internalType': 'address', 'name': 'account', 'type': 'address'}, {'indexed': False, 'internalType': 'address[]', 'name': 'path', 'type': 'address[]'}, {'indexed': False, 'internalType': 'address', 'name': 'indexToken', 'type': 'address'}, {'indexed': False, 'internalType': 'uint256', 'name': 'amountIn', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'minOut', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'sizeDelta', 'type': 'uint256'}, {'indexed': False, 'internalType': 'bool', 'name': 'isLong', 'type': 'bool'}, {'indexed': False, 'internalType': 'uint256', 'name': 'acceptablePrice', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'executionFee', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'blockGap', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'timeGap', 'type': 'uint256'}], 'name': 'CancelIncreasePosition', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': True, 'internalType': 'address', 'name': 'account', 'type': 'address'}, {'indexed': False, 'internalType': 'address[]', 'name': 'path', 'type': 'address[]'}, {'indexed': False, 'internalType': 'address', 'name': 'indexToken', 'type': 'address'}, {'indexed': False, 'internalType': 'uint256', 'name': 'collateralDelta', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'sizeDelta', 'type': 'uint256'}, {'indexed': False, 'internalType': 'bool', 'name': 'isLong', 'type': 'bool'}, {'indexed': False, 'internalType': 'address', 'name': 'receiver', 'type': 'address'}, {'indexed': False, 'internalType': 'uint256', 'name': 'acceptablePrice', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'minOut', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'executionFee', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'index', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'queueIndex', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'blockNumber', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'blockTime', 'type': 'uint256'}], 'name': 'CreateDecreasePosition', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': True, 'internalType': 'address', 'name': 'account', 'type': 'address'}, {'indexed': False, 'internalType': 'address[]', 'name': 'path', 'type': 'address[]'}, {'indexed': False, 'internalType': 'address', 'name': 'indexToken', 'type': 'address'}, {'indexed': False, 'internalType': 'uint256', 'name': 'amountIn', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'minOut', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'sizeDelta', 'type': 'uint256'}, {'indexed': False, 'internalType': 'bool', 'name': 'isLong', 'type': 'bool'}, {'indexed': False, 'internalType': 'uint256', 'name': 'acceptablePrice', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'executionFee', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'index', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'queueIndex', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'blockNumber', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'blockTime', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'gasPrice', 'type': 'uint256'}], 'name': 'CreateIncreasePosition', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': True, 'internalType': 'address', 'name': 'account', 'type': 'address'}, {'indexed': False, 'internalType': 'address[]', 'name': 'path', 'type': 'address[]'}, {'indexed': False, 'internalType': 'address', 'name': 'indexToken', 'type': 'address'}, {'indexed': False, 'internalType': 'uint256', 'name': 'collateralDelta', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'sizeDelta', 'type': 'uint256'}, {'indexed': False, 'internalType': 'bool', 'name': 'isLong', 'type': 'bool'}, {'indexed': False, 'internalType': 'address', 'name': 'receiver', 'type': 'address'}, {'indexed': False, 'internalType': 'uint256', 'name': 'acceptablePrice', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'minOut', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'executionFee', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'blockGap', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'timeGap', 'type': 'uint256'}], 'name': 'ExecuteDecreasePosition', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': True, 'internalType': 'address', 'name': 'account', 'type': 'address'}, {'indexed': False, 'internalType': 'address[]', 'name': 'path', 'type': 'address[]'}, {'indexed': False, 'internalType': 'address', 'name': 'indexToken', 'type': 'address'}, {'indexed': False, 'internalType': 'uint256', 'name': 'amountIn', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'minOut', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'sizeDelta', 'type': 'uint256'}, {'indexed': False, 'internalType': 'bool', 'name': 'isLong', 'type': 'bool'}, {'indexed': False, 'internalType': 'uint256', 'name': 'acceptablePrice', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'executionFee', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'blockGap', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'timeGap', 'type': 'uint256'}], 'name': 'ExecuteIncreasePosition', 'type': 'event'}, {'inputs': [], 'name': 'admin', 'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'bytes32', 'name': '_key', 'type': 'bytes32'}, {'internalType': 'address payable', 'name': '_executionFeeReceiver', 'type': 'address'}], 'name': 'cancelDecreasePosition', 'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'bytes32', 'name': '_key', 'type': 'bytes32'}, {'internalType': 'address payable', 'name': '_executionFeeReceiver', 'type': 'address'}], 'name': 'cancelIncreasePosition', 'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address[]', 'name': '_path', 'type': 'address[]'}, {'internalType': 'address', 'name': '_indexToken', 'type': 'address'}, {'internalType': 'uint256', 'name': '_collateralDelta', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '_sizeDelta', 'type': 'uint256'}, {'internalType': 'bool', 'name': '_isLong', 'type': 'bool'}, {'internalType': 'address', 'name': '_receiver', 'type': 'address'}, {'internalType': 'uint256', 'name': '_acceptablePrice', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '_minOut', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '_executionFee', 'type': 'uint256'}, {'internalType': 'bool', 'name': '_withdrawETH', 'type': 'bool'}, {'internalType': 'address', 'name': '_callbackTarget', 'type': 'address'}], 'name': 'createDecreasePosition', 'outputs': [{'internalType': 'bytes32', 'name': '', 'type': 'bytes32'}], 'stateMutability': 'payable', 'type': 'function'}, {'inputs': [{'internalType': 'address[]', 'name': '_path', 'type': 'address[]'}, {'internalType': 'address', 'name': '_indexToken', 'type': 'address'}, {'internalType': 'uint256', 'name': '_amountIn', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '_minOut', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '_sizeDelta', 'type': 'uint256'}, {'internalType': 'bool', 'name': '_isLong', 'type': 'bool'}, {'internalType': 'uint256', 'name': '_acceptablePrice', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '_executionFee', 'type': 'uint256'}, {'internalType': 'bytes32', 'name': '_referralCode', 'type': 'bytes32'}, {'internalType': 'address', 'name': '_callbackTarget', 'type': 'address'}], 'name': 'createIncreasePosition', 'outputs': [{'internalType': 'bytes32', 'name': '', 'type': 'bytes32'}], 'stateMutability': 'payable', 'type': 'function'}, {'inputs': [{'internalType': 'address[]', 'name': '_path', 'type': 'address[]'}, {'internalType': 'address', 'name': '_indexToken', 'type': 'address'}, {'internalType': 'uint256', 'name': '_minOut', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '_sizeDelta', 'type': 'uint256'}, {'internalType': 'bool', 'name': '_isLong', 'type': 'bool'}, {'internalType': 'uint256', 'name': '_acceptablePrice', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '_executionFee', 'type': 'uint256'}, {'internalType': 'bytes32', 'name': '_referralCode', 'type': 'bytes32'}, {'internalType': 'address', 'name': '_callbackTarget', 'type': 'address'}], 'name': 'createIncreasePositionETH', 'outputs': [{'internalType': 'bytes32', 'name': '', 'type': 'bytes32'}], 'stateMutability': 'payable', 'type': 'function'}, {'inputs': [], 'name': 'decreasePositionRequestKeysStart', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'bytes32', 'name': '_key', 'type': 'bytes32'}, {'internalType': 'address payable', 'name': '_executionFeeReceiver', 'type': 'address'}], 'name': 'executeDecreasePosition', 'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'uint256', 'name': '_count', 'type': 'uint256'}, {'internalType': 'address payable', 'name': '_executionFeeReceiver', 'type': 'address'}], 'name': 'executeDecreasePositions', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'bytes32', 'name': '_key', 'type': 'bytes32'}, {'internalType': 'address payable', 'name': '_executionFeeReceiver', 'type': 'address'}], 'name': 'executeIncreasePosition', 'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'uint256', 'name': '_count', 'type': 'uint256'}, {'internalType': 'address payable', 'name': '_executionFeeReceiver', 'type': 'address'}], 'name': 'executeIncreasePositions', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_account', 'type': 'address'}, {'internalType': 'uint256', 'name': '_index', 'type': 'uint256'}], 'name': 'getRequestKey', 'outputs': [{'internalType': 'bytes32', 'name': '', 'type': 'bytes32'}], 'stateMutability': 'pure', 'type': 'function'}, {'inputs': [], 'name': 'increasePositionRequestKeysStart', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'token', 'type': 'address'}], 'name': 'maxGlobalLongSizes', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'token', 'type': 'address'}], 'name': 'maxGlobalShortSizes', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'minExecutionFee', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'minTimeDelayPublic', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'uint256', 'name': '_minBlockDelayKeeper', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '_minTimeDelayPublic', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '_maxTimeDelay', 'type': 'uint256'}], 'name': 'setDelayValues', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}]
        self.bytecode = ''
        self.w3 = web3
            
    def deploy(self):
        contract = self.w3.eth.contract(abi=self.abi, bytecode=self.bytecode)
        tx_hash = contract.constructor().transact()
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        self.address = tx_receipt.contractAddress
        
    def admin(self) -> str:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.admin().call()

    def cancel_decrease_position(self, _key: bytes, _execution_fee_receiver: str, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.cancelDecreasePosition(_key, _execution_fee_receiver).build_transaction(override_tx_parameters)

    def cancel_increase_position(self, _key: bytes, _execution_fee_receiver: str, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.cancelIncreasePosition(_key, _execution_fee_receiver).build_transaction(override_tx_parameters)

    def create_decrease_position(self, _path: List[str], _index_token: str, _collateral_delta: int, _size_delta: int, _is_long: bool, _receiver: str, _acceptable_price: int, _min_out: int, _execution_fee: int, _withdraw_e_t_h: bool, _callback_target: str, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.createDecreasePosition(_path, _index_token, _collateral_delta, _size_delta, _is_long, _receiver, _acceptable_price, _min_out, _execution_fee, _withdraw_e_t_h, _callback_target).build_transaction(override_tx_parameters)

    def create_increase_position(self, _path: List[str], _index_token: str, _amount_in: int, _min_out: int, _size_delta: int, _is_long: bool, _acceptable_price: int, _execution_fee: int, _referral_code: bytes, _callback_target: str, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.createIncreasePosition(_path, _index_token, _amount_in, _min_out, _size_delta, _is_long, _acceptable_price, _execution_fee, _referral_code, _callback_target).build_transaction(override_tx_parameters)

    def create_increase_position_e_t_h(self, _path: List[str], _index_token: str, _min_out: int, _size_delta: int, _is_long: bool, _acceptable_price: int, _execution_fee: int, _referral_code: bytes, _callback_target: str, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.createIncreasePositionETH(_path, _index_token, _min_out, _size_delta, _is_long, _acceptable_price, _execution_fee, _referral_code, _callback_target).build_transaction(override_tx_parameters)

    def decrease_position_request_keys_start(self) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.decreasePositionRequestKeysStart().call()

    def execute_decrease_position(self, _key: bytes, _execution_fee_receiver: str, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.executeDecreasePosition(_key, _execution_fee_receiver).build_transaction(override_tx_parameters)

    def execute_decrease_positions(self, _count: int, _execution_fee_receiver: str, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.executeDecreasePositions(_count, _execution_fee_receiver).build_transaction(override_tx_parameters)

    def execute_increase_position(self, _key: bytes, _execution_fee_receiver: str, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.executeIncreasePosition(_key, _execution_fee_receiver).build_transaction(override_tx_parameters)

    def execute_increase_positions(self, _count: int, _execution_fee_receiver: str, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.executeIncreasePositions(_count, _execution_fee_receiver).build_transaction(override_tx_parameters)

    def get_request_key(self, _account: str, _index: int, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getRequestKey(_account, _index).build_transaction(override_tx_parameters)

    def increase_position_request_keys_start(self) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.increasePositionRequestKeysStart().call()

    def max_global_long_sizes(self, token: str) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.maxGlobalLongSizes(token).call()

    def max_global_short_sizes(self, token: str) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.maxGlobalShortSizes(token).call()

    def min_execution_fee(self) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.minExecutionFee().call()

    def min_time_delay_public(self) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.minTimeDelayPublic().call()

    def set_delay_values(self, _min_block_delay_keeper: int, _min_time_delay_public: int, _max_time_delay: int, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.setDelayValues(_min_block_delay_keeper, _min_time_delay_public, _max_time_delay).build_transaction(override_tx_parameters)

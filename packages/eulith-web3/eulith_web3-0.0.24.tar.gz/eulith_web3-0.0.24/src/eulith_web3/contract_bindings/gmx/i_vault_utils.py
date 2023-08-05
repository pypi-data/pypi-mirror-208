from typing import Optional, Union, List
from eth_typing import Address, ChecksumAddress
from web3 import Web3
from web3.types import TxParams


class ContractAddressNotSet(Exception):
    pass


class IVaultUtils:
    def __init__(self, web3: Web3, contract_address: Optional[Union[Address, ChecksumAddress]] = None):
        self.address: Optional[Union[Address, ChecksumAddress]] = contract_address
        self.abi = [{'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}, {'internalType': 'uint256', 'name': '_usdgAmount', 'type': 'uint256'}], 'name': 'getBuyUsdgFeeBasisPoints', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_collateralToken', 'type': 'address'}, {'internalType': 'address', 'name': '_indexToken', 'type': 'address'}, {'internalType': 'bool', 'name': '_isLong', 'type': 'bool'}], 'name': 'getEntryFundingRate', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}, {'internalType': 'uint256', 'name': '_usdgDelta', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '_feeBasisPoints', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '_taxBasisPoints', 'type': 'uint256'}, {'internalType': 'bool', 'name': '_increment', 'type': 'bool'}], 'name': 'getFeeBasisPoints', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_account', 'type': 'address'}, {'internalType': 'address', 'name': '_collateralToken', 'type': 'address'}, {'internalType': 'address', 'name': '_indexToken', 'type': 'address'}, {'internalType': 'bool', 'name': '_isLong', 'type': 'bool'}, {'internalType': 'uint256', 'name': '_size', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '_entryFundingRate', 'type': 'uint256'}], 'name': 'getFundingFee', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_account', 'type': 'address'}, {'internalType': 'address', 'name': '_collateralToken', 'type': 'address'}, {'internalType': 'address', 'name': '_indexToken', 'type': 'address'}, {'internalType': 'bool', 'name': '_isLong', 'type': 'bool'}, {'internalType': 'uint256', 'name': '_sizeDelta', 'type': 'uint256'}], 'name': 'getPositionFee', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}, {'internalType': 'uint256', 'name': '_usdgAmount', 'type': 'uint256'}], 'name': 'getSellUsdgFeeBasisPoints', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_tokenIn', 'type': 'address'}, {'internalType': 'address', 'name': '_tokenOut', 'type': 'address'}, {'internalType': 'uint256', 'name': '_usdgAmount', 'type': 'uint256'}], 'name': 'getSwapFeeBasisPoints', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_collateralToken', 'type': 'address'}, {'internalType': 'address', 'name': '_indexToken', 'type': 'address'}], 'name': 'updateCumulativeFundingRate', 'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_account', 'type': 'address'}, {'internalType': 'address', 'name': '_collateralToken', 'type': 'address'}, {'internalType': 'address', 'name': '_indexToken', 'type': 'address'}, {'internalType': 'uint256', 'name': '_collateralDelta', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '_sizeDelta', 'type': 'uint256'}, {'internalType': 'bool', 'name': '_isLong', 'type': 'bool'}, {'internalType': 'address', 'name': '_receiver', 'type': 'address'}], 'name': 'validateDecreasePosition', 'outputs': [], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_account', 'type': 'address'}, {'internalType': 'address', 'name': '_collateralToken', 'type': 'address'}, {'internalType': 'address', 'name': '_indexToken', 'type': 'address'}, {'internalType': 'uint256', 'name': '_sizeDelta', 'type': 'uint256'}, {'internalType': 'bool', 'name': '_isLong', 'type': 'bool'}], 'name': 'validateIncreasePosition', 'outputs': [], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_account', 'type': 'address'}, {'internalType': 'address', 'name': '_collateralToken', 'type': 'address'}, {'internalType': 'address', 'name': '_indexToken', 'type': 'address'}, {'internalType': 'bool', 'name': '_isLong', 'type': 'bool'}, {'internalType': 'bool', 'name': '_raise', 'type': 'bool'}], 'name': 'validateLiquidation', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}]
        self.bytecode = ''
        self.w3 = web3
            
    def deploy(self):
        contract = self.w3.eth.contract(abi=self.abi, bytecode=self.bytecode)
        tx_hash = contract.constructor().transact()
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        self.address = tx_receipt.contractAddress
        
    def get_buy_usdg_fee_basis_points(self, _token: str, _usdg_amount: int) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getBuyUsdgFeeBasisPoints(_token, _usdg_amount).call()

    def get_entry_funding_rate(self, _collateral_token: str, _index_token: str, _is_long: bool) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getEntryFundingRate(_collateral_token, _index_token, _is_long).call()

    def get_fee_basis_points(self, _token: str, _usdg_delta: int, _fee_basis_points: int, _tax_basis_points: int, _increment: bool) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getFeeBasisPoints(_token, _usdg_delta, _fee_basis_points, _tax_basis_points, _increment).call()

    def get_funding_fee(self, _account: str, _collateral_token: str, _index_token: str, _is_long: bool, _size: int, _entry_funding_rate: int) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getFundingFee(_account, _collateral_token, _index_token, _is_long, _size, _entry_funding_rate).call()

    def get_position_fee(self, _account: str, _collateral_token: str, _index_token: str, _is_long: bool, _size_delta: int) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getPositionFee(_account, _collateral_token, _index_token, _is_long, _size_delta).call()

    def get_sell_usdg_fee_basis_points(self, _token: str, _usdg_amount: int) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getSellUsdgFeeBasisPoints(_token, _usdg_amount).call()

    def get_swap_fee_basis_points(self, _token_in: str, _token_out: str, _usdg_amount: int) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getSwapFeeBasisPoints(_token_in, _token_out, _usdg_amount).call()

    def update_cumulative_funding_rate(self, _collateral_token: str, _index_token: str, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.updateCumulativeFundingRate(_collateral_token, _index_token).build_transaction(override_tx_parameters)

    def validate_decrease_position(self, _account: str, _collateral_token: str, _index_token: str, _collateral_delta: int, _size_delta: int, _is_long: bool, _receiver: str) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.validateDecreasePosition(_account, _collateral_token, _index_token, _collateral_delta, _size_delta, _is_long, _receiver).build_transaction()

    def validate_increase_position(self, _account: str, _collateral_token: str, _index_token: str, _size_delta: int, _is_long: bool) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.validateIncreasePosition(_account, _collateral_token, _index_token, _size_delta, _is_long).build_transaction()

    def validate_liquidation(self, _account: str, _collateral_token: str, _index_token: str, _is_long: bool, _raise: bool) -> (int, int):
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.validateLiquidation(_account, _collateral_token, _index_token, _is_long, _raise).call()

from typing import Optional, Union, List
from eth_typing import Address, ChecksumAddress
from web3 import Web3
from web3.types import TxParams


class ContractAddressNotSet(Exception):
    pass


class IVaultPriceFeed:
    def __init__(self, web3: Web3, contract_address: Optional[Union[Address, ChecksumAddress]] = None):
        self.address: Optional[Union[Address, ChecksumAddress]] = contract_address
        self.abi = [{'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}], 'name': 'adjustmentBasisPoints', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}], 'name': 'getAmmPrice', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}], 'name': 'getLatestPrimaryPrice', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}, {'internalType': 'bool', 'name': '_maximise', 'type': 'bool'}, {'internalType': 'bool', 'name': '_includeAmmPrice', 'type': 'bool'}, {'internalType': 'bool', 'name': '_useSwapPricing', 'type': 'bool'}], 'name': 'getPrice', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}, {'internalType': 'bool', 'name': '_maximise', 'type': 'bool'}], 'name': 'getPrimaryPrice', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}], 'name': 'isAdjustmentAdditive', 'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}, {'internalType': 'bool', 'name': '_isAdditive', 'type': 'bool'}, {'internalType': 'uint256', 'name': '_adjustmentBps', 'type': 'uint256'}], 'name': 'setAdjustment', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'bool', 'name': '_favorPrimaryPrice', 'type': 'bool'}], 'name': 'setFavorPrimaryPrice', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'bool', 'name': '_isEnabled', 'type': 'bool'}], 'name': 'setIsAmmEnabled', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'bool', 'name': '_isEnabled', 'type': 'bool'}], 'name': 'setIsSecondaryPriceEnabled', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'uint256', 'name': '_maxStrictPriceDeviation', 'type': 'uint256'}], 'name': 'setMaxStrictPriceDeviation', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'uint256', 'name': '_priceSampleSpace', 'type': 'uint256'}], 'name': 'setPriceSampleSpace', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}, {'internalType': 'uint256', 'name': '_spreadBasisPoints', 'type': 'uint256'}], 'name': 'setSpreadBasisPoints', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'uint256', 'name': '_spreadThresholdBasisPoints', 'type': 'uint256'}], 'name': 'setSpreadThresholdBasisPoints', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}, {'internalType': 'address', 'name': '_priceFeed', 'type': 'address'}, {'internalType': 'uint256', 'name': '_priceDecimals', 'type': 'uint256'}, {'internalType': 'bool', 'name': '_isStrictStable', 'type': 'bool'}], 'name': 'setTokenConfig', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'bool', 'name': '_useV2Pricing', 'type': 'bool'}], 'name': 'setUseV2Pricing', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}]
        self.bytecode = ''
        self.w3 = web3
            
    def deploy(self):
        contract = self.w3.eth.contract(abi=self.abi, bytecode=self.bytecode)
        tx_hash = contract.constructor().transact()
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        self.address = tx_receipt.contractAddress
        
    def adjustment_basis_points(self, _token: str) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.adjustmentBasisPoints(_token).call()

    def get_amm_price(self, _token: str) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getAmmPrice(_token).call()

    def get_latest_primary_price(self, _token: str) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getLatestPrimaryPrice(_token).call()

    def get_price(self, _token: str, _maximise: bool, _include_amm_price: bool, _use_swap_pricing: bool) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getPrice(_token, _maximise, _include_amm_price, _use_swap_pricing).call()

    def get_primary_price(self, _token: str, _maximise: bool) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getPrimaryPrice(_token, _maximise).call()

    def is_adjustment_additive(self, _token: str) -> bool:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.isAdjustmentAdditive(_token).call()

    def set_adjustment(self, _token: str, _is_additive: bool, _adjustment_bps: int, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.setAdjustment(_token, _is_additive, _adjustment_bps).build_transaction(override_tx_parameters)

    def set_favor_primary_price(self, _favor_primary_price: bool, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.setFavorPrimaryPrice(_favor_primary_price).build_transaction(override_tx_parameters)

    def set_is_amm_enabled(self, _is_enabled: bool, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.setIsAmmEnabled(_is_enabled).build_transaction(override_tx_parameters)

    def set_is_secondary_price_enabled(self, _is_enabled: bool, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.setIsSecondaryPriceEnabled(_is_enabled).build_transaction(override_tx_parameters)

    def set_max_strict_price_deviation(self, _max_strict_price_deviation: int, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.setMaxStrictPriceDeviation(_max_strict_price_deviation).build_transaction(override_tx_parameters)

    def set_price_sample_space(self, _price_sample_space: int, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.setPriceSampleSpace(_price_sample_space).build_transaction(override_tx_parameters)

    def set_spread_basis_points(self, _token: str, _spread_basis_points: int, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.setSpreadBasisPoints(_token, _spread_basis_points).build_transaction(override_tx_parameters)

    def set_spread_threshold_basis_points(self, _spread_threshold_basis_points: int, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.setSpreadThresholdBasisPoints(_spread_threshold_basis_points).build_transaction(override_tx_parameters)

    def set_token_config(self, _token: str, _price_feed: str, _price_decimals: int, _is_strict_stable: bool, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.setTokenConfig(_token, _price_feed, _price_decimals, _is_strict_stable).build_transaction(override_tx_parameters)

    def set_use_v2_pricing(self, _use_v2_pricing: bool, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.setUseV2Pricing(_use_v2_pricing).build_transaction(override_tx_parameters)

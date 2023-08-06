from typing import Optional, Union, List
from eth_typing import Address, ChecksumAddress
from web3 import Web3
from web3.types import TxParams


class ContractAddressNotSet(Exception):
    pass


class IGlpManager:
    def __init__(self, web3: Web3, contract_address: Optional[Union[Address, ChecksumAddress]] = None):
        self.address: Optional[Union[Address, ChecksumAddress]] = contract_address
        self.abi = [{'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}, {'internalType': 'uint256', 'name': '_amount', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '_minUsdg', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '_minGlp', 'type': 'uint256'}], 'name': 'addLiquidity', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_fundingAccount', 'type': 'address'}, {'internalType': 'address', 'name': '_account', 'type': 'address'}, {'internalType': 'address', 'name': '_token', 'type': 'address'}, {'internalType': 'uint256', 'name': '_amount', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '_minUsdg', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '_minGlp', 'type': 'uint256'}], 'name': 'addLiquidityForAccount', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [], 'name': 'cooldownDuration', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'bool', 'name': 'maximise', 'type': 'bool'}], 'name': 'getAumInUsdg', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'bool', 'name': '_maximise', 'type': 'bool'}], 'name': 'getPrice', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'glp', 'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_account', 'type': 'address'}], 'name': 'lastAddedAt', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_tokenOut', 'type': 'address'}, {'internalType': 'uint256', 'name': '_glpAmount', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '_minOut', 'type': 'uint256'}, {'internalType': 'address', 'name': '_receiver', 'type': 'address'}], 'name': 'removeLiquidity', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_account', 'type': 'address'}, {'internalType': 'address', 'name': '_tokenOut', 'type': 'address'}, {'internalType': 'uint256', 'name': '_glpAmount', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '_minOut', 'type': 'uint256'}, {'internalType': 'address', 'name': '_receiver', 'type': 'address'}], 'name': 'removeLiquidityForAccount', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'uint256', 'name': '_cooldownDuration', 'type': 'uint256'}], 'name': 'setCooldownDuration', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'uint256', 'name': '_shortsTrackerAveragePriceWeight', 'type': 'uint256'}], 'name': 'setShortsTrackerAveragePriceWeight', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [], 'name': 'usdg', 'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'vault', 'outputs': [{'internalType': 'contract IVault', 'name': '', 'type': 'address'}], 'stateMutability': 'view', 'type': 'function'}]
        self.bytecode = ''
        self.w3 = web3
            
    def deploy(self):
        contract = self.w3.eth.contract(abi=self.abi, bytecode=self.bytecode)
        tx_hash = contract.constructor().transact()
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        self.address = tx_receipt.contractAddress
        
    def add_liquidity(self, _token: str, _amount: int, _min_usdg: int, _min_glp: int, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.addLiquidity(_token, _amount, _min_usdg, _min_glp).build_transaction(override_tx_parameters)

    def add_liquidity_for_account(self, _funding_account: str, _account: str, _token: str, _amount: int, _min_usdg: int, _min_glp: int, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.addLiquidityForAccount(_funding_account, _account, _token, _amount, _min_usdg, _min_glp).build_transaction(override_tx_parameters)

    def cooldown_duration(self, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.cooldownDuration().build_transaction(override_tx_parameters)

    def get_aum_in_usdg(self, maximise: bool) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getAumInUsdg(maximise).call()

    def get_price(self, _maximise: bool) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getPrice(_maximise).call()

    def glp(self) -> str:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.glp().call()

    def last_added_at(self, _account: str, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.lastAddedAt(_account).build_transaction(override_tx_parameters)

    def remove_liquidity(self, _token_out: str, _glp_amount: int, _min_out: int, _receiver: str, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.removeLiquidity(_token_out, _glp_amount, _min_out, _receiver).build_transaction(override_tx_parameters)

    def remove_liquidity_for_account(self, _account: str, _token_out: str, _glp_amount: int, _min_out: int, _receiver: str, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.removeLiquidityForAccount(_account, _token_out, _glp_amount, _min_out, _receiver).build_transaction(override_tx_parameters)

    def set_cooldown_duration(self, _cooldown_duration: int, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.setCooldownDuration(_cooldown_duration).build_transaction(override_tx_parameters)

    def set_shorts_tracker_average_price_weight(self, _shorts_tracker_average_price_weight: int, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.setShortsTrackerAveragePriceWeight(_shorts_tracker_average_price_weight).build_transaction(override_tx_parameters)

    def usdg(self) -> str:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.usdg().call()

    def vault(self) -> str:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.vault().call()

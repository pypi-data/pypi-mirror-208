from typing import Optional, Union, List
from eth_typing import Address, ChecksumAddress
from web3 import Web3
from web3.types import TxParams


class ContractAddressNotSet(Exception):
    pass


class IReader:
    def __init__(self, web3: Web3, contract_address: Optional[Union[Address, ChecksumAddress]] = None):
        self.address: Optional[Union[Address, ChecksumAddress]] = contract_address
        self.abi = [{'inputs': [{'internalType': 'contract IVault', 'name': '_vault', 'type': 'address'}, {'internalType': 'address', 'name': '_tokenIn', 'type': 'address'}, {'internalType': 'address', 'name': '_tokenOut', 'type': 'address'}, {'internalType': 'uint256', 'name': '_amountIn', 'type': 'uint256'}], 'name': 'getAmountOut', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'contract IVault', 'name': '_vault', 'type': 'address'}, {'internalType': 'address', 'name': '_tokenIn', 'type': 'address'}, {'internalType': 'address', 'name': '_tokenOut', 'type': 'address'}, {'internalType': 'uint256', 'name': '_amountIn', 'type': 'uint256'}], 'name': 'getFeeBasisPoints', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_vault', 'type': 'address'}, {'internalType': 'address', 'name': '_weth', 'type': 'address'}, {'internalType': 'uint256', 'name': '_usdgAmount', 'type': 'uint256'}, {'internalType': 'address[]', 'name': '_tokens', 'type': 'address[]'}], 'name': 'getFullVaultTokenInfo', 'outputs': [{'internalType': 'uint256[]', 'name': '', 'type': 'uint256[]'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_vault', 'type': 'address'}, {'internalType': 'address', 'name': '_weth', 'type': 'address'}, {'internalType': 'address[]', 'name': '_tokens', 'type': 'address[]'}], 'name': 'getFundingRates', 'outputs': [{'internalType': 'uint256[]', 'name': '', 'type': 'uint256[]'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'contract IVault', 'name': '_vault', 'type': 'address'}, {'internalType': 'address', 'name': '_tokenIn', 'type': 'address'}, {'internalType': 'address', 'name': '_tokenOut', 'type': 'address'}], 'name': 'getMaxAmountIn', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_factory', 'type': 'address'}, {'internalType': 'address[]', 'name': '_tokens', 'type': 'address[]'}], 'name': 'getPairInfo', 'outputs': [{'internalType': 'uint256[]', 'name': '', 'type': 'uint256[]'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_vault', 'type': 'address'}, {'internalType': 'address', 'name': '_account', 'type': 'address'}, {'internalType': 'address[]', 'name': '_collateralTokens', 'type': 'address[]'}, {'internalType': 'address[]', 'name': '_indexTokens', 'type': 'address[]'}, {'internalType': 'bool[]', 'name': '_isLong', 'type': 'bool[]'}], 'name': 'getPositions', 'outputs': [{'internalType': 'uint256[]', 'name': '', 'type': 'uint256[]'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'contract IVaultPriceFeed', 'name': '_priceFeed', 'type': 'address'}, {'internalType': 'address[]', 'name': '_tokens', 'type': 'address[]'}], 'name': 'getPrices', 'outputs': [{'internalType': 'uint256[]', 'name': '', 'type': 'uint256[]'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_account', 'type': 'address'}, {'internalType': 'address[]', 'name': '_yieldTrackers', 'type': 'address[]'}], 'name': 'getStakingInfo', 'outputs': [{'internalType': 'uint256[]', 'name': '', 'type': 'uint256[]'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_account', 'type': 'address'}, {'internalType': 'address[]', 'name': '_tokens', 'type': 'address[]'}], 'name': 'getTokenBalances', 'outputs': [{'internalType': 'uint256[]', 'name': '', 'type': 'uint256[]'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_account', 'type': 'address'}, {'internalType': 'address[]', 'name': '_tokens', 'type': 'address[]'}], 'name': 'getTokenBalancesWithSupplies', 'outputs': [{'internalType': 'uint256[]', 'name': '', 'type': 'uint256[]'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}, {'internalType': 'address[]', 'name': '_excludedAccounts', 'type': 'address[]'}], 'name': 'getTokenSupply', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}, {'internalType': 'address[]', 'name': '_accounts', 'type': 'address[]'}], 'name': 'getTotalBalance', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address[]', 'name': '_yieldTokens', 'type': 'address[]'}], 'name': 'getTotalStaked', 'outputs': [{'internalType': 'uint256[]', 'name': '', 'type': 'uint256[]'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_vault', 'type': 'address'}, {'internalType': 'address', 'name': '_weth', 'type': 'address'}, {'internalType': 'uint256', 'name': '_usdgAmount', 'type': 'uint256'}, {'internalType': 'address[]', 'name': '_tokens', 'type': 'address[]'}], 'name': 'getVaultTokenInfo', 'outputs': [{'internalType': 'uint256[]', 'name': '', 'type': 'uint256[]'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_vault', 'type': 'address'}, {'internalType': 'address', 'name': '_weth', 'type': 'address'}, {'internalType': 'uint256', 'name': '_usdgAmount', 'type': 'uint256'}, {'internalType': 'address[]', 'name': '_tokens', 'type': 'address[]'}], 'name': 'getVaultTokenInfoV2', 'outputs': [{'internalType': 'uint256[]', 'name': '', 'type': 'uint256[]'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_account', 'type': 'address'}, {'internalType': 'address[]', 'name': '_vesters', 'type': 'address[]'}], 'name': 'getVestingInfo', 'outputs': [{'internalType': 'uint256[]', 'name': '', 'type': 'uint256[]'}], 'stateMutability': 'view', 'type': 'function'}]
        self.bytecode = ''
        self.w3 = web3
            
    def deploy(self):
        contract = self.w3.eth.contract(abi=self.abi, bytecode=self.bytecode)
        tx_hash = contract.constructor().transact()
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        self.address = tx_receipt.contractAddress
        
    def get_amount_out(self, _vault: str, _token_in: str, _token_out: str, _amount_in: int) -> (int, int):
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getAmountOut(_vault, _token_in, _token_out, _amount_in).call()

    def get_fee_basis_points(self, _vault: str, _token_in: str, _token_out: str, _amount_in: int) -> (int, int, int):
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getFeeBasisPoints(_vault, _token_in, _token_out, _amount_in).call()

    def get_full_vault_token_info(self, _vault: str, _weth: str, _usdg_amount: int, _tokens: List[str]) -> List[int]:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getFullVaultTokenInfo(_vault, _weth, _usdg_amount, _tokens).call()

    def get_funding_rates(self, _vault: str, _weth: str, _tokens: List[str]) -> List[int]:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getFundingRates(_vault, _weth, _tokens).call()

    def get_max_amount_in(self, _vault: str, _token_in: str, _token_out: str) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getMaxAmountIn(_vault, _token_in, _token_out).call()

    def get_pair_info(self, _factory: str, _tokens: List[str]) -> List[int]:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getPairInfo(_factory, _tokens).call()

    def get_positions(self, _vault: str, _account: str, _collateral_tokens: List[str], _index_tokens: List[str], _is_long: List[bool]) -> List[int]:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getPositions(_vault, _account, _collateral_tokens, _index_tokens, _is_long).call()

    def get_prices(self, _price_feed: str, _tokens: List[str]) -> List[int]:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getPrices(_price_feed, _tokens).call()

    def get_staking_info(self, _account: str, _yield_trackers: List[str]) -> List[int]:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getStakingInfo(_account, _yield_trackers).call()

    def get_token_balances(self, _account: str, _tokens: List[str]) -> List[int]:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getTokenBalances(_account, _tokens).call()

    def get_token_balances_with_supplies(self, _account: str, _tokens: List[str]) -> List[int]:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getTokenBalancesWithSupplies(_account, _tokens).call()

    def get_token_supply(self, _token: str, _excluded_accounts: List[str]) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getTokenSupply(_token, _excluded_accounts).call()

    def get_total_balance(self, _token: str, _accounts: List[str]) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getTotalBalance(_token, _accounts).call()

    def get_total_staked(self, _yield_tokens: List[str]) -> List[int]:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getTotalStaked(_yield_tokens).call()

    def get_vault_token_info(self, _vault: str, _weth: str, _usdg_amount: int, _tokens: List[str]) -> List[int]:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getVaultTokenInfo(_vault, _weth, _usdg_amount, _tokens).call()

    def get_vault_token_info_v2(self, _vault: str, _weth: str, _usdg_amount: int, _tokens: List[str]) -> List[int]:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getVaultTokenInfoV2(_vault, _weth, _usdg_amount, _tokens).call()

    def get_vesting_info(self, _account: str, _vesters: List[str]) -> List[int]:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getVestingInfo(_account, _vesters).call()

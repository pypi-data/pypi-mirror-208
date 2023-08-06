from typing import Optional, Union, List
from eth_typing import Address, ChecksumAddress
from web3 import Web3
from web3.types import TxParams


class ContractAddressNotSet(Exception):
    pass


class IRewardTracker:
    def __init__(self, web3: Web3, contract_address: Optional[Union[Address, ChecksumAddress]] = None):
        self.address: Optional[Union[Address, ChecksumAddress]] = contract_address
        self.abi = [{'inputs': [{'internalType': 'address', 'name': '_account', 'type': 'address'}], 'name': 'averageStakedAmounts', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_account', 'type': 'address'}], 'name': 'balanceOf', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_receiver', 'type': 'address'}], 'name': 'claim', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_account', 'type': 'address'}, {'internalType': 'address', 'name': '_receiver', 'type': 'address'}], 'name': 'claimForAccount', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_account', 'type': 'address'}], 'name': 'claimable', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_account', 'type': 'address'}], 'name': 'cumulativeRewards', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_account', 'type': 'address'}, {'internalType': 'address', 'name': '_depositToken', 'type': 'address'}], 'name': 'depositBalances', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_depositToken', 'type': 'address'}, {'internalType': 'uint256', 'name': '_amount', 'type': 'uint256'}], 'name': 'stake', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_fundingAccount', 'type': 'address'}, {'internalType': 'address', 'name': '_account', 'type': 'address'}, {'internalType': 'address', 'name': '_depositToken', 'type': 'address'}, {'internalType': 'uint256', 'name': '_amount', 'type': 'uint256'}], 'name': 'stakeForAccount', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_account', 'type': 'address'}], 'name': 'stakedAmounts', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'tokensPerInterval', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'totalSupply', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_depositToken', 'type': 'address'}, {'internalType': 'uint256', 'name': '_amount', 'type': 'uint256'}], 'name': 'unstake', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_account', 'type': 'address'}, {'internalType': 'address', 'name': '_depositToken', 'type': 'address'}, {'internalType': 'uint256', 'name': '_amount', 'type': 'uint256'}, {'internalType': 'address', 'name': '_receiver', 'type': 'address'}], 'name': 'unstakeForAccount', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [], 'name': 'updateRewards', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}]
        self.bytecode = ''
        self.w3 = web3
            
    def deploy(self):
        contract = self.w3.eth.contract(abi=self.abi, bytecode=self.bytecode)
        tx_hash = contract.constructor().transact()
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        self.address = tx_receipt.contractAddress
        
    def average_staked_amounts(self, _account: str) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.averageStakedAmounts(_account).call()

    def balance_of(self, _account: str) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.balanceOf(_account).call()

    def claim(self, _receiver: str, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.claim(_receiver).build_transaction(override_tx_parameters)

    def claim_for_account(self, _account: str, _receiver: str, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.claimForAccount(_account, _receiver).build_transaction(override_tx_parameters)

    def claimable(self, _account: str) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.claimable(_account).call()

    def cumulative_rewards(self, _account: str) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.cumulativeRewards(_account).call()

    def deposit_balances(self, _account: str, _deposit_token: str) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.depositBalances(_account, _deposit_token).call()

    def stake(self, _deposit_token: str, _amount: int, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.stake(_deposit_token, _amount).build_transaction(override_tx_parameters)

    def stake_for_account(self, _funding_account: str, _account: str, _deposit_token: str, _amount: int, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.stakeForAccount(_funding_account, _account, _deposit_token, _amount).build_transaction(override_tx_parameters)

    def staked_amounts(self, _account: str) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.stakedAmounts(_account).call()

    def tokens_per_interval(self) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.tokensPerInterval().call()

    def total_supply(self) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.totalSupply().call()

    def unstake(self, _deposit_token: str, _amount: int, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.unstake(_deposit_token, _amount).build_transaction(override_tx_parameters)

    def unstake_for_account(self, _account: str, _deposit_token: str, _amount: int, _receiver: str, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.unstakeForAccount(_account, _deposit_token, _amount, _receiver).build_transaction(override_tx_parameters)

    def update_rewards(self, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.updateRewards().build_transaction(override_tx_parameters)

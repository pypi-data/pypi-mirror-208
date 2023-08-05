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


class IStandardizedYield:
    def __init__(self, web3: Web3, contract_address: Optional[Union[Address, ChecksumAddress]] = None):
        self.address: Optional[Union[Address, ChecksumAddress]] = contract_address
        self.abi = [{'anonymous': False, 'inputs': [{'indexed': True, 'internalType': 'address', 'name': 'owner', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'spender', 'type': 'address'}, {'indexed': False, 'internalType': 'uint256', 'name': 'value', 'type': 'uint256'}], 'name': 'Approval', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': True, 'internalType': 'address', 'name': 'user', 'type': 'address'}, {'indexed': False, 'internalType': 'address[]', 'name': 'rewardTokens', 'type': 'address[]'}, {'indexed': False, 'internalType': 'uint256[]', 'name': 'rewardAmounts', 'type': 'uint256[]'}], 'name': 'ClaimRewards', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': True, 'internalType': 'address', 'name': 'caller', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'receiver', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'tokenIn', 'type': 'address'}, {'indexed': False, 'internalType': 'uint256', 'name': 'amountDeposited', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'amountSyOut', 'type': 'uint256'}], 'name': 'Deposit', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': True, 'internalType': 'address', 'name': 'caller', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'receiver', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'tokenOut', 'type': 'address'}, {'indexed': False, 'internalType': 'uint256', 'name': 'amountSyToRedeem', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'amountTokenOut', 'type': 'uint256'}], 'name': 'Redeem', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': True, 'internalType': 'address', 'name': 'from', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'to', 'type': 'address'}, {'indexed': False, 'internalType': 'uint256', 'name': 'value', 'type': 'uint256'}], 'name': 'Transfer', 'type': 'event'}, {'inputs': [{'internalType': 'address', 'name': 'user', 'type': 'address'}], 'name': 'accruedRewards', 'outputs': [{'internalType': 'uint256[]', 'name': 'rewardAmounts', 'type': 'uint256[]'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'owner', 'type': 'address'}, {'internalType': 'address', 'name': 'spender', 'type': 'address'}], 'name': 'allowance', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'spender', 'type': 'address'}, {'internalType': 'uint256', 'name': 'amount', 'type': 'uint256'}], 'name': 'approve', 'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [], 'name': 'assetInfo', 'outputs': [{'internalType': 'enum IStandardizedYield.AssetType', 'name': 'assetType', 'type': 'uint8'}, {'internalType': 'address', 'name': 'assetAddress', 'type': 'address'}, {'internalType': 'uint8', 'name': 'assetDecimals', 'type': 'uint8'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'account', 'type': 'address'}], 'name': 'balanceOf', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'user', 'type': 'address'}], 'name': 'claimRewards', 'outputs': [{'internalType': 'uint256[]', 'name': 'rewardAmounts', 'type': 'uint256[]'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [], 'name': 'decimals', 'outputs': [{'internalType': 'uint8', 'name': '', 'type': 'uint8'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'receiver', 'type': 'address'}, {'internalType': 'address', 'name': 'tokenIn', 'type': 'address'}, {'internalType': 'uint256', 'name': 'amountTokenToDeposit', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'minSharesOut', 'type': 'uint256'}], 'name': 'deposit', 'outputs': [{'internalType': 'uint256', 'name': 'amountSharesOut', 'type': 'uint256'}], 'stateMutability': 'payable', 'type': 'function'}, {'inputs': [], 'name': 'exchangeRate', 'outputs': [{'internalType': 'uint256', 'name': 'res', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'getRewardTokens', 'outputs': [{'internalType': 'address[]', 'name': '', 'type': 'address[]'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'getTokensIn', 'outputs': [{'internalType': 'address[]', 'name': 'res', 'type': 'address[]'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'getTokensOut', 'outputs': [{'internalType': 'address[]', 'name': 'res', 'type': 'address[]'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'token', 'type': 'address'}], 'name': 'isValidTokenIn', 'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'token', 'type': 'address'}], 'name': 'isValidTokenOut', 'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'name', 'outputs': [{'internalType': 'string', 'name': '', 'type': 'string'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'tokenIn', 'type': 'address'}, {'internalType': 'uint256', 'name': 'amountTokenToDeposit', 'type': 'uint256'}], 'name': 'previewDeposit', 'outputs': [{'internalType': 'uint256', 'name': 'amountSharesOut', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'tokenOut', 'type': 'address'}, {'internalType': 'uint256', 'name': 'amountSharesToRedeem', 'type': 'uint256'}], 'name': 'previewRedeem', 'outputs': [{'internalType': 'uint256', 'name': 'amountTokenOut', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'receiver', 'type': 'address'}, {'internalType': 'uint256', 'name': 'amountSharesToRedeem', 'type': 'uint256'}, {'internalType': 'address', 'name': 'tokenOut', 'type': 'address'}, {'internalType': 'uint256', 'name': 'minTokenOut', 'type': 'uint256'}, {'internalType': 'bool', 'name': 'burnFromInternalBalance', 'type': 'bool'}], 'name': 'redeem', 'outputs': [{'internalType': 'uint256', 'name': 'amountTokenOut', 'type': 'uint256'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [], 'name': 'rewardIndexesCurrent', 'outputs': [{'internalType': 'uint256[]', 'name': 'indexes', 'type': 'uint256[]'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [], 'name': 'rewardIndexesStored', 'outputs': [{'internalType': 'uint256[]', 'name': 'indexes', 'type': 'uint256[]'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'symbol', 'outputs': [{'internalType': 'string', 'name': '', 'type': 'string'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'totalSupply', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'to', 'type': 'address'}, {'internalType': 'uint256', 'name': 'amount', 'type': 'uint256'}], 'name': 'transfer', 'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'from', 'type': 'address'}, {'internalType': 'address', 'name': 'to', 'type': 'address'}, {'internalType': 'uint256', 'name': 'amount', 'type': 'uint256'}], 'name': 'transferFrom', 'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [], 'name': 'yieldToken', 'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}], 'stateMutability': 'view', 'type': 'function'}]
        self.bytecode = ''
        self.w3 = web3
            
    def deploy(self):
        contract = self.w3.eth.contract(abi=self.abi, bytecode=self.bytecode)
        tx_hash = contract.constructor().transact()
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        self.address = tx_receipt.contractAddress
        
    def accrued_rewards(self, user: str) -> List[int]:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.accruedRewards(user).call()

    def allowance(self, owner: str, spender: str) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.allowance(owner, spender).call()

    def approve(self, spender: str, amount: int, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.approve(spender, amount).build_transaction(override_tx_parameters)

    def asset_info(self) -> (int, str, int):
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.assetInfo().call()

    def balance_of(self, account: str) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.balanceOf(account).call()

    def claim_rewards(self, user: str, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.claimRewards(user).build_transaction(override_tx_parameters)

    def decimals(self) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.decimals().call()

    def deposit(self, receiver: str, token_in: str, amount_token_to_deposit: int, min_shares_out: int, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.deposit(receiver, token_in, amount_token_to_deposit, min_shares_out).build_transaction(override_tx_parameters)

    def exchange_rate(self) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.exchangeRate().call()

    def get_reward_tokens(self) -> List[str]:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getRewardTokens().call()

    def get_tokens_in(self) -> List[str]:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getTokensIn().call()

    def get_tokens_out(self) -> List[str]:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getTokensOut().call()

    def is_valid_token_in(self, token: str) -> bool:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.isValidTokenIn(token).call()

    def is_valid_token_out(self, token: str) -> bool:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.isValidTokenOut(token).call()

    def name(self) -> str:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.name().call()

    def preview_deposit(self, token_in: str, amount_token_to_deposit: int) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.previewDeposit(token_in, amount_token_to_deposit).call()

    def preview_redeem(self, token_out: str, amount_shares_to_redeem: int) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.previewRedeem(token_out, amount_shares_to_redeem).call()

    def redeem(self, receiver: str, amount_shares_to_redeem: int, token_out: str, min_token_out: int, burn_from_internal_balance: bool, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.redeem(receiver, amount_shares_to_redeem, token_out, min_token_out, burn_from_internal_balance).build_transaction(override_tx_parameters)

    def reward_indexes_current(self, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.rewardIndexesCurrent().build_transaction(override_tx_parameters)

    def reward_indexes_stored(self) -> List[int]:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.rewardIndexesStored().call()

    def symbol(self) -> str:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.symbol().call()

    def total_supply(self) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.totalSupply().call()

    def transfer(self, to: str, amount: int, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.transfer(to, amount).build_transaction(override_tx_parameters)

    def transfer_from(self, _from: str, to: str, amount: int, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.transferFrom(_from, to, amount).build_transaction(override_tx_parameters)

    def yield_token(self) -> str:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.yieldToken().call()

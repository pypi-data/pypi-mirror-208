from typing import Optional, Union, List
from eth_typing import Address, ChecksumAddress
from web3 import Web3
from web3.types import TxParams


class ContractAddressNotSet(Exception):
    pass


class IRewardRouter:
    def __init__(self, web3: Web3, contract_address: Optional[Union[Address, ChecksumAddress]] = None):
        self.address: Optional[Union[Address, ChecksumAddress]] = contract_address
        self.abi = [{'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}, {'internalType': 'uint256', 'name': '_amount', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '_minUsdg', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '_minGlp', 'type': 'uint256'}], 'name': 'mintAndStakeGlp', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'uint256', 'name': '_minUsdg', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '_minGlp', 'type': 'uint256'}], 'name': 'mintAndStakeGlpETH', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'payable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_tokenOut', 'type': 'address'}, {'internalType': 'uint256', 'name': '_glpAmount', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '_minOut', 'type': 'uint256'}, {'internalType': 'address', 'name': '_receiver', 'type': 'address'}], 'name': 'unstakeAndRedeemGlp', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'uint256', 'name': '_glpAmount', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '_minOut', 'type': 'uint256'}, {'internalType': 'address payable', 'name': '_receiver', 'type': 'address'}], 'name': 'unstakeAndRedeemGlpETH', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'nonpayable', 'type': 'function'}]
        self.bytecode = ''
        self.w3 = web3
            
    def deploy(self):
        contract = self.w3.eth.contract(abi=self.abi, bytecode=self.bytecode)
        tx_hash = contract.constructor().transact()
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        self.address = tx_receipt.contractAddress
        
    def mint_and_stake_glp(self, _token: str, _amount: int, _min_usdg: int, _min_glp: int, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.mintAndStakeGlp(_token, _amount, _min_usdg, _min_glp).build_transaction(override_tx_parameters)

    def mint_and_stake_glp_e_t_h(self, _min_usdg: int, _min_glp: int, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.mintAndStakeGlpETH(_min_usdg, _min_glp).build_transaction(override_tx_parameters)

    def unstake_and_redeem_glp(self, _token_out: str, _glp_amount: int, _min_out: int, _receiver: str, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.unstakeAndRedeemGlp(_token_out, _glp_amount, _min_out, _receiver).build_transaction(override_tx_parameters)

    def unstake_and_redeem_glp_e_t_h(self, _glp_amount: int, _min_out: int, _receiver: str, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.unstakeAndRedeemGlpETH(_glp_amount, _min_out, _receiver).build_transaction(override_tx_parameters)

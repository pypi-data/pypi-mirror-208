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


class IPActionSwapYT:
    def __init__(self, web3: Web3, contract_address: Optional[Union[Address, ChecksumAddress]] = None):
        self.address: Optional[Union[Address, ChecksumAddress]] = contract_address
        self.abi = [{'anonymous': False, 'inputs': [{'indexed': True, 'internalType': 'address', 'name': 'caller', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'market', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'receiver', 'type': 'address'}, {'indexed': False, 'internalType': 'int256', 'name': 'netPtToAccount', 'type': 'int256'}, {'indexed': False, 'internalType': 'int256', 'name': 'netYtToAccount', 'type': 'int256'}], 'name': 'SwapPtAndYt', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': True, 'internalType': 'address', 'name': 'caller', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'market', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'receiver', 'type': 'address'}, {'indexed': False, 'internalType': 'int256', 'name': 'netYtToAccount', 'type': 'int256'}, {'indexed': False, 'internalType': 'int256', 'name': 'netSyToAccount', 'type': 'int256'}], 'name': 'SwapYtAndSy', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': True, 'internalType': 'address', 'name': 'caller', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'market', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'token', 'type': 'address'}, {'indexed': False, 'internalType': 'address', 'name': 'receiver', 'type': 'address'}, {'indexed': False, 'internalType': 'int256', 'name': 'netYtToAccount', 'type': 'int256'}, {'indexed': False, 'internalType': 'int256', 'name': 'netTokenToAccount', 'type': 'int256'}], 'name': 'SwapYtAndToken', 'type': 'event'}, {'inputs': [{'internalType': 'address', 'name': 'receiver', 'type': 'address'}, {'internalType': 'address', 'name': 'market', 'type': 'address'}, {'internalType': 'uint256', 'name': 'exactPtIn', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'minYtOut', 'type': 'uint256'}, {'components': [{'internalType': 'uint256', 'name': 'guessMin', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'guessMax', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'guessOffchain', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'maxIteration', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'eps', 'type': 'uint256'}], 'internalType': 'struct ApproxParams', 'name': 'guessTotalPtToSwap', 'type': 'tuple'}], 'name': 'swapExactPtForYt', 'outputs': [{'internalType': 'uint256', 'name': 'netYtOut', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'netSyFee', 'type': 'uint256'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'receiver', 'type': 'address'}, {'internalType': 'address', 'name': 'market', 'type': 'address'}, {'internalType': 'uint256', 'name': 'exactSyIn', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'minYtOut', 'type': 'uint256'}, {'components': [{'internalType': 'uint256', 'name': 'guessMin', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'guessMax', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'guessOffchain', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'maxIteration', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'eps', 'type': 'uint256'}], 'internalType': 'struct ApproxParams', 'name': 'guessYtOut', 'type': 'tuple'}], 'name': 'swapExactSyForYt', 'outputs': [{'internalType': 'uint256', 'name': 'netYtOut', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'netSyFee', 'type': 'uint256'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'receiver', 'type': 'address'}, {'internalType': 'address', 'name': 'market', 'type': 'address'}, {'internalType': 'uint256', 'name': 'minYtOut', 'type': 'uint256'}, {'components': [{'internalType': 'uint256', 'name': 'guessMin', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'guessMax', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'guessOffchain', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'maxIteration', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'eps', 'type': 'uint256'}], 'internalType': 'struct ApproxParams', 'name': 'guessYtOut', 'type': 'tuple'}, {'components': [{'internalType': 'address', 'name': 'tokenIn', 'type': 'address'}, {'internalType': 'uint256', 'name': 'netTokenIn', 'type': 'uint256'}, {'internalType': 'address', 'name': 'tokenMintSy', 'type': 'address'}, {'internalType': 'address', 'name': 'bulk', 'type': 'address'}, {'internalType': 'address', 'name': 'pendleSwap', 'type': 'address'}, {'components': [{'internalType': 'enum SwapType', 'name': 'swapType', 'type': 'uint8'}, {'internalType': 'address', 'name': 'extRouter', 'type': 'address'}, {'internalType': 'bytes', 'name': 'extCalldata', 'type': 'bytes'}, {'internalType': 'bool', 'name': 'needScale', 'type': 'bool'}], 'internalType': 'struct SwapData', 'name': 'swapData', 'type': 'tuple'}], 'internalType': 'struct TokenInput', 'name': 'input', 'type': 'tuple'}], 'name': 'swapExactTokenForYt', 'outputs': [{'internalType': 'uint256', 'name': 'netYtOut', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'netSyFee', 'type': 'uint256'}], 'stateMutability': 'payable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'receiver', 'type': 'address'}, {'internalType': 'address', 'name': 'market', 'type': 'address'}, {'internalType': 'uint256', 'name': 'exactYtIn', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'minPtOut', 'type': 'uint256'}, {'components': [{'internalType': 'uint256', 'name': 'guessMin', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'guessMax', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'guessOffchain', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'maxIteration', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'eps', 'type': 'uint256'}], 'internalType': 'struct ApproxParams', 'name': 'guessTotalPtSwapped', 'type': 'tuple'}], 'name': 'swapExactYtForPt', 'outputs': [{'internalType': 'uint256', 'name': 'netPtOut', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'netSyFee', 'type': 'uint256'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'receiver', 'type': 'address'}, {'internalType': 'address', 'name': 'market', 'type': 'address'}, {'internalType': 'uint256', 'name': 'exactYtIn', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'minSyOut', 'type': 'uint256'}], 'name': 'swapExactYtForSy', 'outputs': [{'internalType': 'uint256', 'name': 'netSyOut', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'netSyFee', 'type': 'uint256'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'receiver', 'type': 'address'}, {'internalType': 'address', 'name': 'market', 'type': 'address'}, {'internalType': 'uint256', 'name': 'netYtIn', 'type': 'uint256'}, {'components': [{'internalType': 'address', 'name': 'tokenOut', 'type': 'address'}, {'internalType': 'uint256', 'name': 'minTokenOut', 'type': 'uint256'}, {'internalType': 'address', 'name': 'tokenRedeemSy', 'type': 'address'}, {'internalType': 'address', 'name': 'bulk', 'type': 'address'}, {'internalType': 'address', 'name': 'pendleSwap', 'type': 'address'}, {'components': [{'internalType': 'enum SwapType', 'name': 'swapType', 'type': 'uint8'}, {'internalType': 'address', 'name': 'extRouter', 'type': 'address'}, {'internalType': 'bytes', 'name': 'extCalldata', 'type': 'bytes'}, {'internalType': 'bool', 'name': 'needScale', 'type': 'bool'}], 'internalType': 'struct SwapData', 'name': 'swapData', 'type': 'tuple'}], 'internalType': 'struct TokenOutput', 'name': 'output', 'type': 'tuple'}], 'name': 'swapExactYtForToken', 'outputs': [{'internalType': 'uint256', 'name': 'netTokenOut', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'netSyFee', 'type': 'uint256'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'receiver', 'type': 'address'}, {'internalType': 'address', 'name': 'market', 'type': 'address'}, {'internalType': 'uint256', 'name': 'exactYtOut', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'maxSyIn', 'type': 'uint256'}], 'name': 'swapSyForExactYt', 'outputs': [{'internalType': 'uint256', 'name': 'netSyIn', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'netSyFee', 'type': 'uint256'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'receiver', 'type': 'address'}, {'internalType': 'address', 'name': 'market', 'type': 'address'}, {'internalType': 'uint256', 'name': 'exactSyOut', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'maxYtIn', 'type': 'uint256'}, {'components': [{'internalType': 'uint256', 'name': 'guessMin', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'guessMax', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'guessOffchain', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'maxIteration', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'eps', 'type': 'uint256'}], 'internalType': 'struct ApproxParams', 'name': 'guessYtIn', 'type': 'tuple'}], 'name': 'swapYtForExactSy', 'outputs': [{'internalType': 'uint256', 'name': 'netYtIn', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'netSyFee', 'type': 'uint256'}], 'stateMutability': 'nonpayable', 'type': 'function'}]
        self.bytecode = ''
        self.w3 = web3
            
    def deploy(self):
        contract = self.w3.eth.contract(abi=self.abi, bytecode=self.bytecode)
        tx_hash = contract.constructor().transact()
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        self.address = tx_receipt.contractAddress
        
    def swap_exact_pt_for_yt(self, receiver: str, market: str, exact_pt_in: int, min_yt_out: int, guess_total_pt_to_swap: ApproxParams, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.swapExactPtForYt(receiver, market, exact_pt_in, min_yt_out, serialize_struct(guess_total_pt_to_swap)).build_transaction(override_tx_parameters)

    def swap_exact_sy_for_yt(self, receiver: str, market: str, exact_sy_in: int, min_yt_out: int, guess_yt_out: ApproxParams, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.swapExactSyForYt(receiver, market, exact_sy_in, min_yt_out, serialize_struct(guess_yt_out)).build_transaction(override_tx_parameters)

    def swap_exact_token_for_yt(self, receiver: str, market: str, min_yt_out: int, guess_yt_out: ApproxParams, input: TokenInput, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.swapExactTokenForYt(receiver, market, min_yt_out, serialize_struct(guess_yt_out), serialize_struct(input)).build_transaction(override_tx_parameters)

    def swap_exact_yt_for_pt(self, receiver: str, market: str, exact_yt_in: int, min_pt_out: int, guess_total_pt_swapped: ApproxParams, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.swapExactYtForPt(receiver, market, exact_yt_in, min_pt_out, serialize_struct(guess_total_pt_swapped)).build_transaction(override_tx_parameters)

    def swap_exact_yt_for_sy(self, receiver: str, market: str, exact_yt_in: int, min_sy_out: int, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.swapExactYtForSy(receiver, market, exact_yt_in, min_sy_out).build_transaction(override_tx_parameters)

    def swap_exact_yt_for_token(self, receiver: str, market: str, net_yt_in: int, output: TokenOutput, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.swapExactYtForToken(receiver, market, net_yt_in, serialize_struct(output)).build_transaction(override_tx_parameters)

    def swap_sy_for_exact_yt(self, receiver: str, market: str, exact_yt_out: int, max_sy_in: int, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.swapSyForExactYt(receiver, market, exact_yt_out, max_sy_in).build_transaction(override_tx_parameters)

    def swap_yt_for_exact_sy(self, receiver: str, market: str, exact_sy_out: int, max_yt_in: int, guess_yt_in: ApproxParams, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.swapYtForExactSy(receiver, market, exact_sy_out, max_yt_in, serialize_struct(guess_yt_in)).build_transaction(override_tx_parameters)

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


class IPActionSwapPT:
    def __init__(self, web3: Web3, contract_address: Optional[Union[Address, ChecksumAddress]] = None):
        self.address: Optional[Union[Address, ChecksumAddress]] = contract_address
        self.abi = [{'anonymous': False, 'inputs': [{'indexed': True, 'internalType': 'address', 'name': 'caller', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'market', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'receiver', 'type': 'address'}, {'indexed': False, 'internalType': 'int256', 'name': 'netPtToAccount', 'type': 'int256'}, {'indexed': False, 'internalType': 'int256', 'name': 'netSyToAccount', 'type': 'int256'}], 'name': 'SwapPtAndSy', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': True, 'internalType': 'address', 'name': 'caller', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'market', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'token', 'type': 'address'}, {'indexed': False, 'internalType': 'address', 'name': 'receiver', 'type': 'address'}, {'indexed': False, 'internalType': 'int256', 'name': 'netPtToAccount', 'type': 'int256'}, {'indexed': False, 'internalType': 'int256', 'name': 'netTokenToAccount', 'type': 'int256'}], 'name': 'SwapPtAndToken', 'type': 'event'}, {'inputs': [{'internalType': 'address', 'name': 'receiver', 'type': 'address'}, {'internalType': 'address', 'name': 'market', 'type': 'address'}, {'internalType': 'uint256', 'name': 'exactPtIn', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'minSyOut', 'type': 'uint256'}], 'name': 'swapExactPtForSy', 'outputs': [{'internalType': 'uint256', 'name': 'netSyOut', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'netSyFee', 'type': 'uint256'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'receiver', 'type': 'address'}, {'internalType': 'address', 'name': 'market', 'type': 'address'}, {'internalType': 'uint256', 'name': 'exactPtIn', 'type': 'uint256'}, {'components': [{'internalType': 'address', 'name': 'tokenOut', 'type': 'address'}, {'internalType': 'uint256', 'name': 'minTokenOut', 'type': 'uint256'}, {'internalType': 'address', 'name': 'tokenRedeemSy', 'type': 'address'}, {'internalType': 'address', 'name': 'bulk', 'type': 'address'}, {'internalType': 'address', 'name': 'pendleSwap', 'type': 'address'}, {'components': [{'internalType': 'enum SwapType', 'name': 'swapType', 'type': 'uint8'}, {'internalType': 'address', 'name': 'extRouter', 'type': 'address'}, {'internalType': 'bytes', 'name': 'extCalldata', 'type': 'bytes'}, {'internalType': 'bool', 'name': 'needScale', 'type': 'bool'}], 'internalType': 'struct SwapData', 'name': 'swapData', 'type': 'tuple'}], 'internalType': 'struct TokenOutput', 'name': 'output', 'type': 'tuple'}], 'name': 'swapExactPtForToken', 'outputs': [{'internalType': 'uint256', 'name': 'netTokenOut', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'netSyFee', 'type': 'uint256'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'receiver', 'type': 'address'}, {'internalType': 'address', 'name': 'market', 'type': 'address'}, {'internalType': 'uint256', 'name': 'exactSyIn', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'minPtOut', 'type': 'uint256'}, {'components': [{'internalType': 'uint256', 'name': 'guessMin', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'guessMax', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'guessOffchain', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'maxIteration', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'eps', 'type': 'uint256'}], 'internalType': 'struct ApproxParams', 'name': 'guessPtOut', 'type': 'tuple'}], 'name': 'swapExactSyForPt', 'outputs': [{'internalType': 'uint256', 'name': 'netPtOut', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'netSyFee', 'type': 'uint256'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'receiver', 'type': 'address'}, {'internalType': 'address', 'name': 'market', 'type': 'address'}, {'internalType': 'uint256', 'name': 'minPtOut', 'type': 'uint256'}, {'components': [{'internalType': 'uint256', 'name': 'guessMin', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'guessMax', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'guessOffchain', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'maxIteration', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'eps', 'type': 'uint256'}], 'internalType': 'struct ApproxParams', 'name': 'guessPtOut', 'type': 'tuple'}, {'components': [{'internalType': 'address', 'name': 'tokenIn', 'type': 'address'}, {'internalType': 'uint256', 'name': 'netTokenIn', 'type': 'uint256'}, {'internalType': 'address', 'name': 'tokenMintSy', 'type': 'address'}, {'internalType': 'address', 'name': 'bulk', 'type': 'address'}, {'internalType': 'address', 'name': 'pendleSwap', 'type': 'address'}, {'components': [{'internalType': 'enum SwapType', 'name': 'swapType', 'type': 'uint8'}, {'internalType': 'address', 'name': 'extRouter', 'type': 'address'}, {'internalType': 'bytes', 'name': 'extCalldata', 'type': 'bytes'}, {'internalType': 'bool', 'name': 'needScale', 'type': 'bool'}], 'internalType': 'struct SwapData', 'name': 'swapData', 'type': 'tuple'}], 'internalType': 'struct TokenInput', 'name': 'input', 'type': 'tuple'}], 'name': 'swapExactTokenForPt', 'outputs': [{'internalType': 'uint256', 'name': 'netPtOut', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'netSyFee', 'type': 'uint256'}], 'stateMutability': 'payable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'receiver', 'type': 'address'}, {'internalType': 'address', 'name': 'market', 'type': 'address'}, {'internalType': 'uint256', 'name': 'exactSyOut', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'maxPtIn', 'type': 'uint256'}, {'components': [{'internalType': 'uint256', 'name': 'guessMin', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'guessMax', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'guessOffchain', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'maxIteration', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'eps', 'type': 'uint256'}], 'internalType': 'struct ApproxParams', 'name': 'guessPtIn', 'type': 'tuple'}], 'name': 'swapPtForExactSy', 'outputs': [{'internalType': 'uint256', 'name': 'netPtIn', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'netSyFee', 'type': 'uint256'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'receiver', 'type': 'address'}, {'internalType': 'address', 'name': 'market', 'type': 'address'}, {'internalType': 'uint256', 'name': 'exactPtOut', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'maxSyIn', 'type': 'uint256'}], 'name': 'swapSyForExactPt', 'outputs': [{'internalType': 'uint256', 'name': 'netSyIn', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'netSyFee', 'type': 'uint256'}], 'stateMutability': 'nonpayable', 'type': 'function'}]
        self.bytecode = ''
        self.w3 = web3
            
    def deploy(self):
        contract = self.w3.eth.contract(abi=self.abi, bytecode=self.bytecode)
        tx_hash = contract.constructor().transact()
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        self.address = tx_receipt.contractAddress
        
    def swap_exact_pt_for_sy(self, receiver: str, market: str, exact_pt_in: int, min_sy_out: int, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.swapExactPtForSy(receiver, market, exact_pt_in, min_sy_out).build_transaction(override_tx_parameters)

    def swap_exact_pt_for_token(self, receiver: str, market: str, exact_pt_in: int, output: TokenOutput, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.swapExactPtForToken(receiver, market, exact_pt_in, serialize_struct(output)).build_transaction(override_tx_parameters)

    def swap_exact_sy_for_pt(self, receiver: str, market: str, exact_sy_in: int, min_pt_out: int, guess_pt_out: ApproxParams, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.swapExactSyForPt(receiver, market, exact_sy_in, min_pt_out, serialize_struct(guess_pt_out)).build_transaction(override_tx_parameters)

    def swap_exact_token_for_pt(self, receiver: str, market: str, min_pt_out: int, guess_pt_out: ApproxParams, input: TokenInput, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.swapExactTokenForPt(receiver, market, min_pt_out, serialize_struct(guess_pt_out), serialize_struct(input)).build_transaction(override_tx_parameters)

    def swap_pt_for_exact_sy(self, receiver: str, market: str, exact_sy_out: int, max_pt_in: int, guess_pt_in: ApproxParams, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.swapPtForExactSy(receiver, market, exact_sy_out, max_pt_in, serialize_struct(guess_pt_in)).build_transaction(override_tx_parameters)

    def swap_sy_for_exact_pt(self, receiver: str, market: str, exact_pt_out: int, max_sy_in: int, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.swapSyForExactPt(receiver, market, exact_pt_out, max_sy_in).build_transaction(override_tx_parameters)

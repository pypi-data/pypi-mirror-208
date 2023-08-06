from typing import Optional, Union, List, TypedDict
from eth_typing import Address, ChecksumAddress
from web3 import Web3
from web3.types import TxParams


class ContractAddressNotSet(Exception):
    pass


class IPMarket:
    def __init__(self, web3: Web3, contract_address: Optional[Union[Address, ChecksumAddress]] = None):
        self.address: Optional[Union[Address, ChecksumAddress]] = contract_address
        self.abi = [{'anonymous': False, 'inputs': [{'indexed': True, 'internalType': 'address', 'name': 'owner', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'spender', 'type': 'address'}, {'indexed': False, 'internalType': 'uint256', 'name': 'value', 'type': 'uint256'}], 'name': 'Approval', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': True, 'internalType': 'address', 'name': 'receiverSy', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'receiverPt', 'type': 'address'}, {'indexed': False, 'internalType': 'uint256', 'name': 'netLpBurned', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'netSyOut', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'netPtOut', 'type': 'uint256'}], 'name': 'Burn', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': False, 'internalType': 'uint16', 'name': 'observationCardinalityNextOld', 'type': 'uint16'}, {'indexed': False, 'internalType': 'uint16', 'name': 'observationCardinalityNextNew', 'type': 'uint16'}], 'name': 'IncreaseObservationCardinalityNext', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': True, 'internalType': 'address', 'name': 'receiver', 'type': 'address'}, {'indexed': False, 'internalType': 'uint256', 'name': 'netLpMinted', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'netSyUsed', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'netPtUsed', 'type': 'uint256'}], 'name': 'Mint', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': True, 'internalType': 'address', 'name': 'caller', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'receiver', 'type': 'address'}, {'indexed': False, 'internalType': 'int256', 'name': 'netPtOut', 'type': 'int256'}, {'indexed': False, 'internalType': 'int256', 'name': 'netSyOut', 'type': 'int256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'netSyFee', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'netSyToReserve', 'type': 'uint256'}], 'name': 'Swap', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': True, 'internalType': 'address', 'name': 'from', 'type': 'address'}, {'indexed': True, 'internalType': 'address', 'name': 'to', 'type': 'address'}, {'indexed': False, 'internalType': 'uint256', 'name': 'value', 'type': 'uint256'}], 'name': 'Transfer', 'type': 'event'}, {'anonymous': False, 'inputs': [{'indexed': True, 'internalType': 'uint256', 'name': 'timestamp', 'type': 'uint256'}, {'indexed': False, 'internalType': 'uint256', 'name': 'lnLastImpliedRate', 'type': 'uint256'}], 'name': 'UpdateImpliedRate', 'type': 'event'}, {'inputs': [{'internalType': 'address', 'name': 'user', 'type': 'address'}], 'name': 'activeBalance', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'owner', 'type': 'address'}, {'internalType': 'address', 'name': 'spender', 'type': 'address'}], 'name': 'allowance', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'spender', 'type': 'address'}, {'internalType': 'uint256', 'name': 'amount', 'type': 'uint256'}], 'name': 'approve', 'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'account', 'type': 'address'}], 'name': 'balanceOf', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'receiverSy', 'type': 'address'}, {'internalType': 'address', 'name': 'receiverPt', 'type': 'address'}, {'internalType': 'uint256', 'name': 'netLpToBurn', 'type': 'uint256'}], 'name': 'burn', 'outputs': [{'internalType': 'uint256', 'name': 'netSyOut', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'netPtOut', 'type': 'uint256'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [], 'name': 'decimals', 'outputs': [{'internalType': 'uint8', 'name': '', 'type': 'uint8'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'expiry', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'getRewardTokens', 'outputs': [{'internalType': 'address[]', 'name': '', 'type': 'address[]'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'uint16', 'name': 'cardinalityNext', 'type': 'uint16'}], 'name': 'increaseObservationsCardinalityNext', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [], 'name': 'isExpired', 'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'receiver', 'type': 'address'}, {'internalType': 'uint256', 'name': 'netSyDesired', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'netPtDesired', 'type': 'uint256'}], 'name': 'mint', 'outputs': [{'internalType': 'uint256', 'name': 'netLpOut', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'netSyUsed', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'netPtUsed', 'type': 'uint256'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [], 'name': 'name', 'outputs': [{'internalType': 'string', 'name': '', 'type': 'string'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'uint32[]', 'name': 'secondsAgos', 'type': 'uint32[]'}], 'name': 'observe', 'outputs': [{'internalType': 'uint216[]', 'name': 'lnImpliedRateCumulative', 'type': 'uint216[]'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'router', 'type': 'address'}], 'name': 'readState', 'outputs': [{'components': [{'internalType': 'int256', 'name': 'totalPt', 'type': 'int256'}, {'internalType': 'int256', 'name': 'totalSy', 'type': 'int256'}, {'internalType': 'int256', 'name': 'totalLp', 'type': 'int256'}, {'internalType': 'address', 'name': 'treasury', 'type': 'address'}, {'internalType': 'int256', 'name': 'scalarRoot', 'type': 'int256'}, {'internalType': 'uint256', 'name': 'expiry', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'lnFeeRateRoot', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'reserveFeePercent', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'lastLnImpliedRate', 'type': 'uint256'}], 'internalType': 'struct MarketState', 'name': 'market', 'type': 'tuple'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'readTokens', 'outputs': [{'internalType': 'contract IStandardizedYield', 'name': '_SY', 'type': 'address'}, {'internalType': 'contract IPPrincipalToken', 'name': '_PT', 'type': 'address'}, {'internalType': 'contract IPYieldToken', 'name': '_YT', 'type': 'address'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'user', 'type': 'address'}], 'name': 'redeemRewards', 'outputs': [{'internalType': 'uint256[]', 'name': '', 'type': 'uint256[]'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'receiver', 'type': 'address'}, {'internalType': 'uint256', 'name': 'exactPtIn', 'type': 'uint256'}, {'internalType': 'bytes', 'name': 'data', 'type': 'bytes'}], 'name': 'swapExactPtForSy', 'outputs': [{'internalType': 'uint256', 'name': 'netSyOut', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'netSyFee', 'type': 'uint256'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'receiver', 'type': 'address'}, {'internalType': 'uint256', 'name': 'exactPtOut', 'type': 'uint256'}, {'internalType': 'bytes', 'name': 'data', 'type': 'bytes'}], 'name': 'swapSyForExactPt', 'outputs': [{'internalType': 'uint256', 'name': 'netSyIn', 'type': 'uint256'}, {'internalType': 'uint256', 'name': 'netSyFee', 'type': 'uint256'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [], 'name': 'symbol', 'outputs': [{'internalType': 'string', 'name': '', 'type': 'string'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'totalActiveSupply', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'totalSupply', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'to', 'type': 'address'}, {'internalType': 'uint256', 'name': 'amount', 'type': 'uint256'}], 'name': 'transfer', 'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': 'from', 'type': 'address'}, {'internalType': 'address', 'name': 'to', 'type': 'address'}, {'internalType': 'uint256', 'name': 'amount', 'type': 'uint256'}], 'name': 'transferFrom', 'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}], 'stateMutability': 'nonpayable', 'type': 'function'}]
        self.bytecode = ''
        self.w3 = web3
            
    def deploy(self):
        contract = self.w3.eth.contract(abi=self.abi, bytecode=self.bytecode)
        tx_hash = contract.constructor().transact()
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        self.address = tx_receipt.contractAddress
        
    def active_balance(self, user: str) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.activeBalance(user).call()

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

    def balance_of(self, account: str) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.balanceOf(account).call()

    def burn(self, receiver_sy: str, receiver_pt: str, net_lp_to_burn: int, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.burn(receiver_sy, receiver_pt, net_lp_to_burn).build_transaction(override_tx_parameters)

    def decimals(self) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.decimals().call()

    def expiry(self) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.expiry().call()

    def get_reward_tokens(self) -> List[str]:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getRewardTokens().call()

    def increase_observations_cardinality_next(self, cardinality_next: int, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.increaseObservationsCardinalityNext(cardinality_next).build_transaction(override_tx_parameters)

    def is_expired(self) -> bool:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.isExpired().call()

    def mint(self, receiver: str, net_sy_desired: int, net_pt_desired: int, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.mint(receiver, net_sy_desired, net_pt_desired).build_transaction(override_tx_parameters)

    def name(self) -> str:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.name().call()

    def observe(self, seconds_agos: List[int]) -> List[None]:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.observe(seconds_agos).call()

    def read_state(self, router: str) -> tuple:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.readState(router).call()

    def read_tokens(self) -> (str, str, str):
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.readTokens().call()

    def redeem_rewards(self, user: str, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.redeemRewards(user).build_transaction(override_tx_parameters)

    def swap_exact_pt_for_sy(self, receiver: str, exact_pt_in: int, data: bytes, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.swapExactPtForSy(receiver, exact_pt_in, data).build_transaction(override_tx_parameters)

    def swap_sy_for_exact_pt(self, receiver: str, exact_pt_out: int, data: bytes, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.swapSyForExactPt(receiver, exact_pt_out, data).build_transaction(override_tx_parameters)

    def symbol(self) -> str:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.symbol().call()

    def total_active_supply(self) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.totalActiveSupply().call()

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

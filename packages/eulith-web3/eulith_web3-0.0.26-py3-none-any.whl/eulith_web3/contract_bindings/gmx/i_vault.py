from typing import Optional, Union, List
from eth_typing import Address, ChecksumAddress
from web3 import Web3
from web3.types import TxParams


class ContractAddressNotSet(Exception):
    pass


class IVault:
    def __init__(self, web3: Web3, contract_address: Optional[Union[Address, ChecksumAddress]] = None):
        self.address: Optional[Union[Address, ChecksumAddress]] = contract_address
        self.abi = [{'inputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'name': 'allWhitelistedTokens', 'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'allWhitelistedTokensLength', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_account', 'type': 'address'}, {'internalType': 'address', 'name': '_router', 'type': 'address'}], 'name': 'approvedRouters', 'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}], 'name': 'bufferAmounts', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}, {'internalType': 'address', 'name': '_receiver', 'type': 'address'}], 'name': 'buyUSDG', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}], 'name': 'cumulativeFundingRates', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_account', 'type': 'address'}, {'internalType': 'address', 'name': '_collateralToken', 'type': 'address'}, {'internalType': 'address', 'name': '_indexToken', 'type': 'address'}, {'internalType': 'uint256', 'name': '_collateralDelta', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '_sizeDelta', 'type': 'uint256'}, {'internalType': 'bool', 'name': '_isLong', 'type': 'bool'}, {'internalType': 'address', 'name': '_receiver', 'type': 'address'}], 'name': 'decreasePosition', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}], 'name': 'directPoolDeposit', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}], 'name': 'feeReserves', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'fundingInterval', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'fundingRateFactor', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_indexToken', 'type': 'address'}, {'internalType': 'uint256', 'name': '_size', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '_averagePrice', 'type': 'uint256'}, {'internalType': 'bool', 'name': '_isLong', 'type': 'bool'}, {'internalType': 'uint256', 'name': '_lastIncreasedTime', 'type': 'uint256'}], 'name': 'getDelta', 'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}, {'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}, {'internalType': 'uint256', 'name': '_usdgDelta', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '_feeBasisPoints', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '_taxBasisPoints', 'type': 'uint256'}, {'internalType': 'bool', 'name': '_increment', 'type': 'bool'}], 'name': 'getFeeBasisPoints', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}], 'name': 'getMaxPrice', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}], 'name': 'getMinPrice', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}], 'name': 'getNextFundingRate', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_account', 'type': 'address'}, {'internalType': 'address', 'name': '_collateralToken', 'type': 'address'}, {'internalType': 'address', 'name': '_indexToken', 'type': 'address'}, {'internalType': 'bool', 'name': '_isLong', 'type': 'bool'}], 'name': 'getPosition', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '', 'type': 'uint256'}, {'internalType': 'bool', 'name': '', 'type': 'bool'}, {'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}, {'internalType': 'uint256', 'name': '_usdgAmount', 'type': 'uint256'}], 'name': 'getRedemptionAmount', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}], 'name': 'getTargetUsdgAmount', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}], 'name': 'globalShortAveragePrices', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}], 'name': 'globalShortSizes', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'gov', 'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}], 'name': 'guaranteedUsd', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'hasDynamicFees', 'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'inManagerMode', 'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'inPrivateLiquidationMode', 'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_account', 'type': 'address'}, {'internalType': 'address', 'name': '_collateralToken', 'type': 'address'}, {'internalType': 'address', 'name': '_indexToken', 'type': 'address'}, {'internalType': 'uint256', 'name': '_sizeDelta', 'type': 'uint256'}, {'internalType': 'bool', 'name': '_isLong', 'type': 'bool'}], 'name': 'increasePosition', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [], 'name': 'isInitialized', 'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'isLeverageEnabled', 'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_account', 'type': 'address'}], 'name': 'isLiquidator', 'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_account', 'type': 'address'}], 'name': 'isManager', 'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'isSwapEnabled', 'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}], 'name': 'lastFundingTimes', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_account', 'type': 'address'}, {'internalType': 'address', 'name': '_collateralToken', 'type': 'address'}, {'internalType': 'address', 'name': '_indexToken', 'type': 'address'}, {'internalType': 'bool', 'name': '_isLong', 'type': 'bool'}, {'internalType': 'address', 'name': '_feeReceiver', 'type': 'address'}], 'name': 'liquidatePosition', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [], 'name': 'liquidationFeeUsd', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'marginFeeBasisPoints', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'maxGasPrice', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}], 'name': 'maxGlobalShortSizes', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'maxLeverage', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}], 'name': 'maxUsdgAmounts', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}], 'name': 'minProfitBasisPoints', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'minProfitTime', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'mintBurnFeeBasisPoints', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}], 'name': 'poolAmounts', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'priceFeed', 'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}], 'name': 'reservedAmounts', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'router', 'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}, {'internalType': 'address', 'name': '_receiver', 'type': 'address'}], 'name': 'sellUSDG', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}, {'internalType': 'uint256', 'name': '_amount', 'type': 'uint256'}], 'name': 'setBufferAmount', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'uint256', 'name': '_errorCode', 'type': 'uint256'}, {'internalType': 'string', 'name': '_error', 'type': 'string'}], 'name': 'setError', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'uint256', 'name': '_taxBasisPoints', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '_stableTaxBasisPoints', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '_mintBurnFeeBasisPoints', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '_swapFeeBasisPoints', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '_stableSwapFeeBasisPoints', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '_marginFeeBasisPoints', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '_liquidationFeeUsd', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '_minProfitTime', 'type': 'uint256'}, {'internalType': 'bool', 'name': '_hasDynamicFees', 'type': 'bool'}], 'name': 'setFees', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'uint256', 'name': '_fundingInterval', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '_fundingRateFactor', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '_stableFundingRateFactor', 'type': 'uint256'}], 'name': 'setFundingRate', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'bool', 'name': '_inManagerMode', 'type': 'bool'}], 'name': 'setInManagerMode', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'bool', 'name': '_inPrivateLiquidationMode', 'type': 'bool'}], 'name': 'setInPrivateLiquidationMode', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'bool', 'name': '_isLeverageEnabled', 'type': 'bool'}], 'name': 'setIsLeverageEnabled', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'bool', 'name': '_isSwapEnabled', 'type': 'bool'}], 'name': 'setIsSwapEnabled', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_liquidator', 'type': 'address'}, {'internalType': 'bool', 'name': '_isActive', 'type': 'bool'}], 'name': 'setLiquidator', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_manager', 'type': 'address'}, {'internalType': 'bool', 'name': '_isManager', 'type': 'bool'}], 'name': 'setManager', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'uint256', 'name': '_maxGasPrice', 'type': 'uint256'}], 'name': 'setMaxGasPrice', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}, {'internalType': 'uint256', 'name': '_amount', 'type': 'uint256'}], 'name': 'setMaxGlobalShortSize', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'uint256', 'name': '_maxLeverage', 'type': 'uint256'}], 'name': 'setMaxLeverage', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_priceFeed', 'type': 'address'}], 'name': 'setPriceFeed', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}, {'internalType': 'uint256', 'name': '_tokenDecimals', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '_redemptionBps', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '_minProfitBps', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '_maxUsdgAmount', 'type': 'uint256'}, {'internalType': 'bool', 'name': '_isStable', 'type': 'bool'}, {'internalType': 'bool', 'name': '_isShortable', 'type': 'bool'}], 'name': 'setTokenConfig', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}, {'internalType': 'uint256', 'name': '_amount', 'type': 'uint256'}], 'name': 'setUsdgAmount', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'contract IVaultUtils', 'name': '_vaultUtils', 'type': 'address'}], 'name': 'setVaultUtils', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}], 'name': 'shortableTokens', 'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'stableFundingRateFactor', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'stableSwapFeeBasisPoints', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'stableTaxBasisPoints', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}], 'name': 'stableTokens', 'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_tokenIn', 'type': 'address'}, {'internalType': 'address', 'name': '_tokenOut', 'type': 'address'}, {'internalType': 'address', 'name': '_receiver', 'type': 'address'}], 'name': 'swap', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [], 'name': 'swapFeeBasisPoints', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'taxBasisPoints', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}], 'name': 'tokenBalances', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}], 'name': 'tokenDecimals', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}, {'internalType': 'uint256', 'name': '_tokenAmount', 'type': 'uint256'}], 'name': 'tokenToUsdMin', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}], 'name': 'tokenWeights', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'totalTokenWeights', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'usdg', 'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}], 'name': 'usdgAmounts', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_account', 'type': 'address'}, {'internalType': 'address', 'name': '_collateralToken', 'type': 'address'}, {'internalType': 'address', 'name': '_indexToken', 'type': 'address'}, {'internalType': 'bool', 'name': '_isLong', 'type': 'bool'}, {'internalType': 'bool', 'name': '_raise', 'type': 'bool'}], 'name': 'validateLiquidation', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}, {'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [], 'name': 'vaultUtils', 'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}], 'stateMutability': 'nonpayable', 'type': 'function'}, {'inputs': [], 'name': 'whitelistedTokenCount', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}], 'name': 'whitelistedTokens', 'outputs': [{'internalType': 'bool', 'name': '', 'type': 'bool'}], 'stateMutability': 'view', 'type': 'function'}, {'inputs': [{'internalType': 'address', 'name': '_token', 'type': 'address'}, {'internalType': 'address', 'name': '_receiver', 'type': 'address'}], 'name': 'withdrawFees', 'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}], 'stateMutability': 'nonpayable', 'type': 'function'}]
        self.bytecode = ''
        self.w3 = web3
            
    def deploy(self):
        contract = self.w3.eth.contract(abi=self.abi, bytecode=self.bytecode)
        tx_hash = contract.constructor().transact()
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        self.address = tx_receipt.contractAddress
        
    def all_whitelisted_tokens(self, a0: int) -> str:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.allWhitelistedTokens(a0).call()

    def all_whitelisted_tokens_length(self) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.allWhitelistedTokensLength().call()

    def approved_routers(self, _account: str, _router: str) -> bool:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.approvedRouters(_account, _router).call()

    def buffer_amounts(self, _token: str) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.bufferAmounts(_token).call()

    def buy_u_s_d_g(self, _token: str, _receiver: str, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.buyUSDG(_token, _receiver).build_transaction(override_tx_parameters)

    def cumulative_funding_rates(self, _token: str) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.cumulativeFundingRates(_token).call()

    def decrease_position(self, _account: str, _collateral_token: str, _index_token: str, _collateral_delta: int, _size_delta: int, _is_long: bool, _receiver: str, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.decreasePosition(_account, _collateral_token, _index_token, _collateral_delta, _size_delta, _is_long, _receiver).build_transaction(override_tx_parameters)

    def direct_pool_deposit(self, _token: str, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.directPoolDeposit(_token).build_transaction(override_tx_parameters)

    def fee_reserves(self, _token: str) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.feeReserves(_token).call()

    def funding_interval(self) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.fundingInterval().call()

    def funding_rate_factor(self) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.fundingRateFactor().call()

    def get_delta(self, _index_token: str, _size: int, _average_price: int, _is_long: bool, _last_increased_time: int) -> (bool, int):
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getDelta(_index_token, _size, _average_price, _is_long, _last_increased_time).call()

    def get_fee_basis_points(self, _token: str, _usdg_delta: int, _fee_basis_points: int, _tax_basis_points: int, _increment: bool) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getFeeBasisPoints(_token, _usdg_delta, _fee_basis_points, _tax_basis_points, _increment).call()

    def get_max_price(self, _token: str) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getMaxPrice(_token).call()

    def get_min_price(self, _token: str) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getMinPrice(_token).call()

    def get_next_funding_rate(self, _token: str) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getNextFundingRate(_token).call()

    def get_position(self, _account: str, _collateral_token: str, _index_token: str, _is_long: bool) -> (int, int, int, int, int, int, bool, int):
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getPosition(_account, _collateral_token, _index_token, _is_long).call()

    def get_redemption_amount(self, _token: str, _usdg_amount: int) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getRedemptionAmount(_token, _usdg_amount).call()

    def get_target_usdg_amount(self, _token: str) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.getTargetUsdgAmount(_token).call()

    def global_short_average_prices(self, _token: str) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.globalShortAveragePrices(_token).call()

    def global_short_sizes(self, _token: str) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.globalShortSizes(_token).call()

    def gov(self) -> str:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.gov().call()

    def guaranteed_usd(self, _token: str) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.guaranteedUsd(_token).call()

    def has_dynamic_fees(self) -> bool:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.hasDynamicFees().call()

    def in_manager_mode(self) -> bool:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.inManagerMode().call()

    def in_private_liquidation_mode(self) -> bool:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.inPrivateLiquidationMode().call()

    def increase_position(self, _account: str, _collateral_token: str, _index_token: str, _size_delta: int, _is_long: bool, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.increasePosition(_account, _collateral_token, _index_token, _size_delta, _is_long).build_transaction(override_tx_parameters)

    def is_initialized(self) -> bool:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.isInitialized().call()

    def is_leverage_enabled(self) -> bool:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.isLeverageEnabled().call()

    def is_liquidator(self, _account: str) -> bool:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.isLiquidator(_account).call()

    def is_manager(self, _account: str) -> bool:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.isManager(_account).call()

    def is_swap_enabled(self) -> bool:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.isSwapEnabled().call()

    def last_funding_times(self, _token: str) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.lastFundingTimes(_token).call()

    def liquidate_position(self, _account: str, _collateral_token: str, _index_token: str, _is_long: bool, _fee_receiver: str, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.liquidatePosition(_account, _collateral_token, _index_token, _is_long, _fee_receiver).build_transaction(override_tx_parameters)

    def liquidation_fee_usd(self) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.liquidationFeeUsd().call()

    def margin_fee_basis_points(self) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.marginFeeBasisPoints().call()

    def max_gas_price(self) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.maxGasPrice().call()

    def max_global_short_sizes(self, _token: str) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.maxGlobalShortSizes(_token).call()

    def max_leverage(self) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.maxLeverage().call()

    def max_usdg_amounts(self, _token: str) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.maxUsdgAmounts(_token).call()

    def min_profit_basis_points(self, _token: str) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.minProfitBasisPoints(_token).call()

    def min_profit_time(self) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.minProfitTime().call()

    def mint_burn_fee_basis_points(self) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.mintBurnFeeBasisPoints().call()

    def pool_amounts(self, _token: str) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.poolAmounts(_token).call()

    def price_feed(self) -> str:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.priceFeed().call()

    def reserved_amounts(self, _token: str) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.reservedAmounts(_token).call()

    def router(self) -> str:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.router().call()

    def sell_u_s_d_g(self, _token: str, _receiver: str, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.sellUSDG(_token, _receiver).build_transaction(override_tx_parameters)

    def set_buffer_amount(self, _token: str, _amount: int, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.setBufferAmount(_token, _amount).build_transaction(override_tx_parameters)

    def set_error(self, _error_code: int, _error: str, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.setError(_error_code, _error).build_transaction(override_tx_parameters)

    def set_fees(self, _tax_basis_points: int, _stable_tax_basis_points: int, _mint_burn_fee_basis_points: int, _swap_fee_basis_points: int, _stable_swap_fee_basis_points: int, _margin_fee_basis_points: int, _liquidation_fee_usd: int, _min_profit_time: int, _has_dynamic_fees: bool, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.setFees(_tax_basis_points, _stable_tax_basis_points, _mint_burn_fee_basis_points, _swap_fee_basis_points, _stable_swap_fee_basis_points, _margin_fee_basis_points, _liquidation_fee_usd, _min_profit_time, _has_dynamic_fees).build_transaction(override_tx_parameters)

    def set_funding_rate(self, _funding_interval: int, _funding_rate_factor: int, _stable_funding_rate_factor: int, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.setFundingRate(_funding_interval, _funding_rate_factor, _stable_funding_rate_factor).build_transaction(override_tx_parameters)

    def set_in_manager_mode(self, _in_manager_mode: bool, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.setInManagerMode(_in_manager_mode).build_transaction(override_tx_parameters)

    def set_in_private_liquidation_mode(self, _in_private_liquidation_mode: bool, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.setInPrivateLiquidationMode(_in_private_liquidation_mode).build_transaction(override_tx_parameters)

    def set_is_leverage_enabled(self, _is_leverage_enabled: bool, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.setIsLeverageEnabled(_is_leverage_enabled).build_transaction(override_tx_parameters)

    def set_is_swap_enabled(self, _is_swap_enabled: bool, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.setIsSwapEnabled(_is_swap_enabled).build_transaction(override_tx_parameters)

    def set_liquidator(self, _liquidator: str, _is_active: bool, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.setLiquidator(_liquidator, _is_active).build_transaction(override_tx_parameters)

    def set_manager(self, _manager: str, _is_manager: bool, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.setManager(_manager, _is_manager).build_transaction(override_tx_parameters)

    def set_max_gas_price(self, _max_gas_price: int, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.setMaxGasPrice(_max_gas_price).build_transaction(override_tx_parameters)

    def set_max_global_short_size(self, _token: str, _amount: int, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.setMaxGlobalShortSize(_token, _amount).build_transaction(override_tx_parameters)

    def set_max_leverage(self, _max_leverage: int, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.setMaxLeverage(_max_leverage).build_transaction(override_tx_parameters)

    def set_price_feed(self, _price_feed: str, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.setPriceFeed(_price_feed).build_transaction(override_tx_parameters)

    def set_token_config(self, _token: str, _token_decimals: int, _redemption_bps: int, _min_profit_bps: int, _max_usdg_amount: int, _is_stable: bool, _is_shortable: bool, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.setTokenConfig(_token, _token_decimals, _redemption_bps, _min_profit_bps, _max_usdg_amount, _is_stable, _is_shortable).build_transaction(override_tx_parameters)

    def set_usdg_amount(self, _token: str, _amount: int, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.setUsdgAmount(_token, _amount).build_transaction(override_tx_parameters)

    def set_vault_utils(self, _vault_utils: str, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.setVaultUtils(_vault_utils).build_transaction(override_tx_parameters)

    def shortable_tokens(self, _token: str) -> bool:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.shortableTokens(_token).call()

    def stable_funding_rate_factor(self) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.stableFundingRateFactor().call()

    def stable_swap_fee_basis_points(self) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.stableSwapFeeBasisPoints().call()

    def stable_tax_basis_points(self) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.stableTaxBasisPoints().call()

    def stable_tokens(self, _token: str) -> bool:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.stableTokens(_token).call()

    def swap(self, _token_in: str, _token_out: str, _receiver: str, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.swap(_token_in, _token_out, _receiver).build_transaction(override_tx_parameters)

    def swap_fee_basis_points(self) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.swapFeeBasisPoints().call()

    def tax_basis_points(self) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.taxBasisPoints().call()

    def token_balances(self, _token: str) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.tokenBalances(_token).call()

    def token_decimals(self, _token: str) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.tokenDecimals(_token).call()

    def token_to_usd_min(self, _token: str, _token_amount: int) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.tokenToUsdMin(_token, _token_amount).call()

    def token_weights(self, _token: str) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.tokenWeights(_token).call()

    def total_token_weights(self) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.totalTokenWeights().call()

    def usdg(self) -> str:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.usdg().call()

    def usdg_amounts(self, _token: str) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.usdgAmounts(_token).call()

    def validate_liquidation(self, _account: str, _collateral_token: str, _index_token: str, _is_long: bool, _raise: bool) -> (int, int):
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.validateLiquidation(_account, _collateral_token, _index_token, _is_long, _raise).call()

    def vault_utils(self, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.vaultUtils().build_transaction(override_tx_parameters)

    def whitelisted_token_count(self) -> int:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.whitelistedTokenCount().call()

    def whitelisted_tokens(self, _token: str) -> bool:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.whitelistedTokens(_token).call()

    def withdraw_fees(self, _token: str, _receiver: str, override_tx_parameters: Optional[TxParams] = None) -> TxParams:
        if not self.address:
            raise ContractAddressNotSet("you must either deploy or initialize the contract with an address")
        c = self.w3.eth.contract(address=self.address, abi=self.abi)
                    
        return c.functions.withdrawFees(_token, _receiver).build_transaction(override_tx_parameters)

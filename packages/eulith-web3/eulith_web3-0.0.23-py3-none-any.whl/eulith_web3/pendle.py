from enum import Enum
from typing import Optional

from eth_typing import ChecksumAddress

from eulith_web3.eulith_web3 import EulithWeb3
from eulith_web3.exceptions import EulithRpcException


class PendleClientException(Exception):
    pass


class PendlePtQuote:
    """
    Represents a quote for buying Pendle Token (PT) in exchange for underlying assets.

    :ivar price_denom_underlying: The PT price in terms of the underlying asset.
    :vartype price_denom_underlying: Optional[float]

    :ivar implied_yield: The current implied yield (as of the last trade).
    :vartype implied_yield: Optional[float]

    :ivar sy_underlying_exchange_rage: The exchange rate of the underlying asset to the SY asset.
    :vartype sy_underlying_exchange_rage: Optional[float]
    """
    def __init__(self, from_dict: dict):
        self.price_denom_underlying: Optional[float] = None
        self.implied_yield: Optional[float] = None
        self.sy_underlying_exchange_rage: Optional[float] = None

        for key, val in from_dict.items():
            setattr(self, key, val)


class PendleMarketSymbol(Enum):
    PrincipleToken = 0
    YieldToken = 1
    StandardYield = 2


class PendleClient:
    def __init__(self, ew3: EulithWeb3, router_override: Optional[ChecksumAddress] = None):
        self.ew3 = ew3

        # Default address from https://docs.pendle.finance/Developers/DeployedContracts/Ethereum
        # Default address is true for both Ethereum and Arbitrum
        self.router = router_override if router_override else self.ew3.to_checksum_address('0x0000000001e4ef00d069e71d6ba041b0a16f7ea0')

    def quote_pt(self, buy_pt_amount: float, market_address: ChecksumAddress) -> PendlePtQuote:
        """
        Get a quote for buying a certain amount of Pendle Token (PT) in exchange for underlying assets.

        :param buy_pt_amount: The amount of PT to buy.
        :type buy_pt_amount: float

        :param market_address: The address of the Pendle market to buy PT from.
        :type market_address: ChecksumAddress

        :return: A PendlePtQuote object containing the PT purchase quote.
        :rtype: PendlePtQuote

        :raises EulithRpcException: If there is an error while getting the PT quote.
        """
        status, result = self.ew3.eulith_data.get_pt_quote(buy_pt_amount, market_address)
        if status:
            return PendlePtQuote(result)
        else:
            raise EulithRpcException(result)

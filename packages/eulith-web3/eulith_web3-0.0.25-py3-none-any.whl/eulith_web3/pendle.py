from enum import Enum
from typing import Optional, Union

import requests
from eth_typing import ChecksumAddress
from web3.types import TxParams, RPCEndpoint

from eulith_web3.erc20 import EulithERC20
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


class PendleSwap:
    """
    The PendleSwap class encapsulates response data from the Eulith server in convenient typed fields

    :param ew3: The Eulith web3 instance.
    :type ew3: EulithWeb3
    :param from_dict: Response body from the Eulith Pendle Swap request
    :type from_dict: dict

    :ivar sell_token: The token to be sold.
    :vartype sell_token: Optional[EulithERC20]
    :ivar buy_token: The token to be bought.
    :vartype buy_token: Optional[EulithERC20]
    :ivar sell_amount: The amount of sell token to be sold.
    :vartype sell_amount: Optional[float]
    :ivar buy_amount: The amount of buy token to be bought.
    :vartype buy_amount: Optional[float]
    :ivar approve_address: The ERC20 address you need to approve(sell_amount) for the swap to work
    :vartype approve_address: Optional[ChecksumAddress]
    :ivar tx: The transaction parameters.
    :vartype tx: Optional[TxParams]
    """
    def __init__(self, ew3, from_dict: dict):
        self.sell_token: Optional[EulithERC20] = None
        self.buy_token: Optional[EulithERC20] = None
        self.sell_amount: Optional[float] = None
        self.buy_amount: Optional[float] = None
        self.approve_address: Optional[ChecksumAddress] = None
        self.tx: Optional[TxParams] = None

        for key, val in from_dict.items():
            if key == 'sell_token' or key == 'buy_token':
                setattr(self, key, EulithERC20(ew3, ew3.to_checksum_address(val)))
            elif key == 'approve_address':
                setattr(self, key, ew3.to_checksum_address(val))
            else:
                setattr(self, key, val)


class PendleMarketSymbol(str, Enum):
    PT = 'pt'
    YT = 'yt'


class PendleClient:
    def __init__(self, ew3, router_override: Optional[ChecksumAddress] = None):
        self.ew3 = ew3

        # Default address from https://docs.pendle.finance/Developers/DeployedContracts/Ethereum
        # Default address is true for both Ethereum and Arbitrum
        self.router = router_override if router_override \
            else self.ew3.to_checksum_address('0x0000000001e4ef00d069e71d6ba041b0a16f7ea0')

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

    def swap(self, sell_token: Union[EulithERC20, PendleMarketSymbol],
             buy_token: Union[EulithERC20, PendleMarketSymbol], sell_amount: float, slippage: float,
             pendle_market: ChecksumAddress, recipient: Optional[ChecksumAddress] = None) -> PendleSwap:
        """
        Retrieves pricing and transaction data needed to swap between two tokens in a given Pendle market.

        :param sell_token: The token to be sold.
        :type sell_token: Union[EulithERC20, PendleMarketSymbol]
        :param buy_token: The token to be bought.
        :type buy_token: Union[EulithERC20, PendleMarketSymbol]
        :param sell_amount: The amount of sell token to be sold.
        :type sell_amount: float
        :param slippage: The acceptable slippage percentage for the swap, represented in float terms like 0.01 == 1%
        :type slippage: float
        :param pendle_market: The Pendle market address where the swap will occur.
        :type pendle_market: ChecksumAddress
        :param recipient: The address that will receive the bought tokens. If not provided, the wallet attached to EulithWeb3 will be used.
        :type recipient: Optional[ChecksumAddress]

        :return: A PendleSwap object representing the executed swap.
        :rtype: PendleSwap

        :raises EulithRpcException: If no recipient is provided and no wallet is attached to EulithWeb3, or if the request fails.
        """

        try:
            sell_token = sell_token.address if isinstance(sell_token, EulithERC20) else sell_token.value
            buy_token = buy_token.address if isinstance(buy_token, EulithERC20) else buy_token.value

            params = {
                'sell_token': sell_token,
                'buy_token': buy_token,
                'sell_amount': sell_amount,
                'slippage_tolerance': slippage,
                'market': pendle_market
            }

            if recipient:
                params['recipient'] = recipient

            res = self.ew3.eulith_data.http.make_request(RPCEndpoint("eulith_pendle_swap"), [params])
            result = res.get('result', {})

            if self.ew3.wallet_address:
                result['tx']['from'] = self.ew3.wallet_address
            else:
                # The server returns None in the 'from' field.
                # If we can't set it, we pop it out to avoid serialization issues with a None value
                result['tx'].pop('from')

            return PendleSwap(self.ew3, result)
        except requests.exceptions.HTTPError as e:
            message = e.response.json().get('error', 'request failed for unknown reason')
            raise EulithRpcException(message)
        except KeyError as e:
            raise EulithRpcException(f'the server responded with a payload that didnt have the expected keys (tx), err {e}')

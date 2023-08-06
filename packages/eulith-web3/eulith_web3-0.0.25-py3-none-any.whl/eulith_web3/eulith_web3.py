import time
import urllib.parse
import uuid
from typing import Union, Any, cast, Callable, Dict, Optional, List
from urllib.parse import urljoin

import requests
import web3.middleware
from eth_typing import URI, ChecksumAddress
from eth_utils import is_hex_address
from hexbytes import HexBytes
from requests import Response
from web3 import Web3, HTTPProvider
from web3.types import RPCEndpoint, RPCResponse, TxParams, TxReceipt

from eulith_web3.common import INT_FEE_TO_FLOAT_DIVISOR, ETHEREUM_STATUS_SUCCESS
from eulith_web3.contract_bindings.safe.i_safe import ISafe
from eulith_web3.erc20 import TokenSymbol, EulithWETH, EulithERC20
from eulith_web3.exceptions import EulithAuthException, EulithRpcException
from eulith_web3.requests import EulithShortOnRequest, EulithShortOffRequest, EulithAaveV2StartLoanRequest, FlashRequest
from eulith_web3.safe_utils.transaction_data import get_enable_module_typed_data
from eulith_web3.signer import Signer
from eulith_web3.signing import normalize_signature
from eulith_web3.swap import EulithSwapProvider, EulithSwapRequest, EulithLiquiditySource
from eulith_web3.uniswap import EulithUniswapV3Pool, EulithUniV3StartLoanRequest, EulithUniV3StartSwapRequest, \
    EulithUniV3SwapQuoteRequest, EulithUniswapPoolLookupRequest, UniswapPoolFee
from eulith_web3.websocket import EulithWebsocketConnection
from eulith_web3.whitelists import ClientWhitelist, ClientWhitelistHash, get_client_whitelist_typed_data


class ApiToken:
    """
    The Eulith API relies on 3 types of tokens for access to service:
        - user token (authenticates users on the frontend and for api refresh tokens)
        - api refresh token (exchanged for an api access token) -- expires after 1 year
        - api access token (authenticates all api services) -- expires after 24 hours

    :ivar token: the stored API token
    :type token: str
    :ivar expire: the unix timestamp of expiration for the token
    :type expire: int
    """

    def __init__(self, token: str, expire: int) -> None:
        """
        :param token: the string representation of the api token
        :type token: str
        :param expire: Unix timestamp indicating the expiration time of the token
        :type expire: int
        """

        self.token = token
        self.expire = expire

    def expires_in_hours(self) -> float:
        """
        The self.expire attribute represents the Unix timestamp (the number of seconds since the epoch), and difference
        between self.expire and now is when it will expire, this is divided by 3600 seconds in an hour to give expiry
        time in hours

        :return: The number of hours until the token expires
        :rtype: float
        """

        now = int(time.time())
        return (self.expire - now) / 3600


def get_api_access_token(eulith_url: URI, eulith_refresh_token: str) -> ApiToken:
    """
    Getting a new API access token using an API refresh token

    :param eulith_url: The base URL of the eulith API
    :type eulith_url: URI
    :param eulith_refresh_token: The refresh token used to request a new access token
    :type eulith_refresh_token: str

    :return: Newly obtained API access token
    :rtype: ApiToken

    :raises EulithAuthException: If the API returns a 400 status code
    :raises EulithRpcException: If the API returns a non-200 status code
    """

    headers = {"Authorization": "Bearer " + eulith_refresh_token, "Content-Type": "application/json"}
    url = urljoin(eulith_url, URI("v0/api/access"))
    response = requests.get(url, headers=headers)
    handle_http_response(response)
    json = response.json()
    token = ApiToken(json['token'], json['exp'])
    return token


def handle_http_response(resp: Response):
    """
    Handle HTTP responses from the API and raise exceptions when needed.
    HTTP status code 400 indicates a Bad Request error, when the request is in wrong format, has wrong or missing parameters, or is incorrect
    HTTP status code 200 indicates a successful HTTP request

    :param resp: The HTTP response from the API
    :type resp: Response

    :raises EulithAuthException: If the API returns a 400 status code
    :raises EulithRpcException: If the API returns a non-200 status code
    """

    if resp.status_code == 400:
        raise EulithAuthException(f"status: {str(resp.status_code)}, message: {resp.text}")
    if resp.status_code != 200:
        raise EulithRpcException(f"status: {str(resp.status_code)}, message: {resp.text}")


def handle_rpc_response(resp: RPCResponse):
    """
    Checks if the resp object passed as an argument to the handle_rpc_response function contains a key 'error'.
    If the key 'error' exists in the dictionary 'resp' and if its value is not an empty string, we handle RPC response
    from the API and raise EulithRpcException

    :param resp: RPC response from the API
    :type resp: RPCResponse

    :raises EulithRpcException: If the 'error' field in the RPC response is not empty
    """

    if 'error' in resp and resp['error'] != "":
        raise EulithRpcException("RPC Error: " + str(resp['error']))


def add_params_to_url(url: str, params) -> str:
    """
    This function takes in a URL and a dictionary of parameters and adds the parameters to the URL as query parameters.
    Eulith relies on query params to specify your atomic tx id or gnosis safe address, for example.

    :param url: The URL to which the parameters will be added.
    :type url: str
    :param params: The dictionary of parameters that will be added to the URL.
    :type params: Dict

    :return: The URL with the added parameters as query parameters.
    :rtype: str

    Example:
        add_params_to_url("https://www.example.com", {"param1": "value1", "param2": "value2"})
        Returns: "https://www.example.com?param1=value1&param2=value2"
    """

    url_parts = urllib.parse.urlparse(url)
    query = dict(urllib.parse.parse_qsl(url_parts.query))
    query.update(params)

    return url_parts._replace(query=urllib.parse.urlencode(query)).geturl()


def get_headers(url: str, token: str) -> Dict:
    """
    Function returns a dictionary of headers to be used in an HTTP request.

    :param url: The URL for which the headers will be returned.
    :type url: str
    :param token: The bearer token to be included in the Authorization header.
    :type token: str

    :return: A dictionary of headers to be used in an HTTP request.
    :rtype: Dict

    Example:
        get_headers("https://www.exampletokenwebsite.com", "token123")
    Returns: {
        'Authorization': 'Bearer token123',
        'Content-Type': 'application/json'
    }
    """

    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }

    # If the URL contains "localhost", an additional header is added to the headers dictionary.
    if 'localhost' in url:
        headers['X-Test'] = 'true'

    return headers


class EulithData:
    """
    Embedded class to represent data of the Eulith API and provides methods to interact with the API.

    :ivar eulith_url: URL of the Eulith API
    :type eulith_url: URI
    :ivar eulith_refresh_token: Refresh token for the Eulith API
    :type eulith_refresh_token: str
    :ivar private: bool switches on whether transactions are routed through a private mempool or not
    :type private: bool
    :ivar atomic: Boolean indicating if the current transaction is atomic
    :type atomic: bool
    :ivar tx_id: ID of the current transaction
    :type tx_id: str
    :ivar api_access_token: Access token for the Eulith API
    :type api_access_token: ApiToken
    :ivar http: HTTP provider instance to make requests to the Eulith API
    :type http: HTTPProvider
    """

    def __init__(self, eulith_url: Union[URI, str],
                 eulith_refresh_token: str, private: bool) -> None:
        """
        :param eulith_url: URL of the Eulith API
        :type eulith_url: Union[URI, str]
        :param eulith_refresh_token: Refresh token for the Eulith API
        :type eulith_refresh_token: str
        :param private: This bool switches on whether transactions are routed through a private mempool or not
        :type private: bool
        """

        self.eulith_url: URI = URI(eulith_url)
        self.private = private
        self.eulith_refresh_token: str = eulith_refresh_token
        self.atomic: bool = False
        self.tx_id: str = ""
        self.api_access_token: ApiToken = get_api_access_token(self.eulith_url, self.eulith_refresh_token)
        headers = get_headers(eulith_url, self.api_access_token.token)
        self.http = HTTPProvider(endpoint_uri=eulith_url, request_kwargs={
            'headers': headers,
            'timeout': 60
        })

    def send_transaction(self, params) -> RPCResponse:
        """
        Sends a transaction to the blockchain via the Eulith RPC provider, handling exceptions that may occur
        when making a request with the make_request method from the HTTPProvider class.

        :param params: Dictionary containing the parameters for the transaction
        :type params: dict

        :returns: The response from the Eulith API
        :rtype: RPCResponse

        :raises EulithRpcException: If there was an error with the RPC request
        """

        try:
            return self.http.make_request(RPCEndpoint("eth_sendTransaction"), params)
        except requests.exceptions.HTTPError as e:
            message = e.response.json().get('error', 'request failed for unknown reason')
            raise EulithRpcException(message)

    def start_transaction(self, account: str, gnosis: str):
        """
        Starts a Eulith atomic transaction. Anything transaction you send within an atomic transaction
        will get confirmed as a single unit. Everything operation in the unit will succeeds,
        or the whole transactions fails. The state of the blockchain is frozen while your atomic transaction
        is processing; there can't be any sandwiches, state changes, etc, in between your atomic operations.

        :param account: Account address
        :type account: str
        :param gnosis: Gnosis Safe address
        :type gnosis: str
        """

        self.atomic = True
        self.tx_id = str(uuid.uuid4())
        params = {'auth_address': account, 'atomic_tx_id': self.tx_id}
        if len(gnosis) > 0:
            params['gnosis_address'] = gnosis
        new_url = add_params_to_url(self.eulith_url, params)
        self.http.endpoint_uri = new_url

    def commit(self) -> TxParams:
        """
        Serializes the current pending atomic tx into a single transactional unit, and returns
        the unsigned params. To get the atomic transaction on-chain, you need to sign these params
        and submit the transaction as a signed payload. The Eulith API handles this automatically for you.

        :returns: A dictionary containing the transaction parameters.
        :rtype: TxParams

        :raises EulithRpcException: If the request fails or the response from the server contains an error.
        """

        self.atomic = False
        params = {}

        try:
            response = self.http.make_request(RPCEndpoint("eulith_commit"), params)
            handle_rpc_response(response)
            self.tx_id = ""
            return cast(TxParams, response['result'])

        except requests.exceptions.HTTPError as e:
            message = e.response.json().get('error', 'request failed for unknown reason')

            raise EulithRpcException(message)

    def rollback(self):
        """
        Rollback here refers to discarding txs added to the atomic tx bundle during the call.
        """

        self.commit()

    def refresh_api_token(self):
        """
        By periodically refreshing, we ensure that the API access token remains valid, as API access tokens have a
        24 hour lifespan and must be periodically refreshed
        """

        self.api_access_token: ApiToken = get_api_access_token(self.eulith_url, self.eulith_refresh_token)
        headers = get_headers(self.eulith_url, self.api_access_token.token)
        self.http = HTTPProvider(endpoint_uri=self.eulith_url, request_kwargs={
            'headers': headers
        })

    def is_close_to_expiry(self) -> bool:
        """
        Checks if the API access token is close to expiring. API access tokens expire 24 hours after origination.

        :returns: A boolean indicating if the API access token is close to expiring.
        :rtype: bool
        """

        return self.api_access_token.expires_in_hours() < 6

    def swap_quote(self, params: EulithSwapRequest) -> (bool, RPCResponse):
        """
        Makes a request to the Eulith API to obtain a quote for a token swap. The returned quote is by default
        the best price across multiple DEX aggregators.

        :param params: Request parameters
        :type params: EulithSwapRequest

        :returns: A tuple of a boolean indicating success and a `RPCResponse` object.
        :rtype: (bool, RPCResponse)

        :raises: requests.exceptions.HTTPError if there was an error making the request.
        """

        try:
            sell_token: EulithERC20
            buy_token: EulithERC20
            sell_amount: float
            recipient: Optional[ChecksumAddress]
            route_through: Optional[EulithSwapProvider]
            slippage_tolerance: Optional[float]
            liquidity_source: Optional[EulithLiquiditySource]

            sell_address = params.get('sell_token').address
            buy_address = params.get('buy_token').address
            parsed_params = {
                'sell_token': sell_address,
                'buy_token': buy_address,
                'sell_amount': params.get('sell_amount')
            }
            recipient = params.get('recipient', None)
            route_through = params.get('route_through', None)
            liquidity_source = params.get('liquidity_source', None)
            slippage_tolerance = params.get('slippage_tolerance', None)

            if recipient:
                parsed_params['recipient'] = recipient
            if route_through:
                parsed_params['route_through'] = route_through
            if liquidity_source:
                parsed_params['liquidity_source'] = liquidity_source
            if slippage_tolerance:
                parsed_params['slippage_tolerance'] = slippage_tolerance

            return True, self.http.make_request(RPCEndpoint("eulith_swap"), [parsed_params])
        except requests.exceptions.HTTPError as e:
            # If there was an error making the request, extract the error message and return it in the response.
            message = e.response.json().get('error', 'request failed for unknown reason')
            return False, RPCResponse(error=message)

    def short_on(self, params: EulithShortOnRequest) -> (bool, RPCResponse):
        """
        Request the Eulith API to open a levered short position on a token.

        :param params: Request params
        :type params: EulithShortOnRequest
            collateral_token (EulithERC20) -- ERC20 token to be used as collateral.
            short_token (EulithERC20) -- ERC20 token to be shorted.
            collateral_amount (float) -- A float representing the amount of the `collateral_token` to be used.

        :returns: A tuple of a boolean indicating success and a `RPCResponse` object.
        :rtype: (bool, RPCResponse)

        :raises: requests.exceptions.HTTPError if there was an error making the request.
        """

        try:
            # Extract the addresses of the collateral and short tokens from the `params` argument.
            collateral_address = params.get('collateral_token').address
            short_address = params.get('short_token').address

            # Create a dictionary of parameters for the request with the token addresses and collateral amount.
            parsed_params = {
                'collateral_token': collateral_address,
                'short_token': short_address,
                'collateral_amount': params.get('collateral_amount')
            }

            return True, self.http.make_request(RPCEndpoint("eulith_short_on"), [parsed_params])
        except requests.exceptions.HTTPError as e:
            # If there was an error making the request, extract the error message and return it in the response.
            message = e.response.json().get('error', 'request failed for unknown reason')
            return False, RPCResponse(error=message)

    def short_off(self, params: EulithShortOffRequest) -> (bool, RPCResponse):
        """
        Makes a request to the Eulith API to unwind an existing short.

        :param params: Request params
        :type params: EulithShortOffRequest

        :returns: A tuple of a boolean indicating success and a `RPCResponse` object.
        :rtype: (bool, RPCResponse)

        :raises: requests.exceptions.HTTPError if there was an error making the request.
        """

        try:

            collateral_address = params.get('collateral_token').address
            short_address = params.get('short_token').address

            parsed_params = {
                'collateral_token': collateral_address,
                'short_token': short_address,
                'repay_short_amount': params.get('repay_short_amount'),
                'true_for_unwind_a': params.get('true_for_unwind_a', True)
            }

            return True, self.http.make_request(RPCEndpoint("eulith_short_off"), [parsed_params])
        except requests.exceptions.HTTPError as e:
            # If there was an error making the request, extract the error message and return it in the response.
            message = e.response.json().get('error', 'request failed for unknown reason')
            return False, RPCResponse(error=message)

    def start_uniswap_v3_loan(self, params: EulithUniV3StartLoanRequest) -> (bool, RPCResponse):
        """
        Makes a request to start a loan in Uniswap V3. This loan is its own atomic structure, meaning
        after you start a loan you have immediate access to the borrow tokens. Transactions you send
        after starting the loan are included in the loan until you call finish_inner to close the loan and
        return one layer up in the nested atomic structure.

        Note that loans have to execute in an atomic transaction. You can't execute a loan on its own.

        :param params: Request params
        :type params: EulithUniV3StartLoanRequest

        :returns: A tuple of a boolean indicating success and an `RPCResponse` object.
        :rtype: (bool, RPCResponse)

        :raises: requests.exceptions.HTTPError if there was an error making the request.
        """

        try:
            borrow_token_a = params.get('borrow_token_a').address
            borrow_amount_a = params.get('borrow_amount_a')
            borrow_token_b = params.get('borrow_token_b', None)
            borrow_amount_b = params.get('borrow_amount_b', None)
            pay_transfer_from = params.get('pay_transfer_from', None)
            recipient = params.get('recipient', None)

            parsed_params = {
                'borrow_token_a': borrow_token_a,
                'borrow_amount_a': borrow_amount_a
            }

            if borrow_token_b:
                parsed_params['borrow_token_b'] = borrow_token_b.address
            if borrow_amount_b:
                parsed_params['borrow_amount_b'] = borrow_amount_b
            if pay_transfer_from:
                parsed_params['pay_transfer_from'] = pay_transfer_from
            if recipient:
                parsed_params['recipient'] = recipient

            return True, self.http.make_request(RPCEndpoint('eulith_start_uniswapv3_loan'), [parsed_params])
        except requests.exceptions.HTTPError as e:
            message = e.response.json().get('error', 'request failed for unknown reason')
            return False, RPCResponse(error=message)

    def start_uniswap_v3_swap(self, params: EulithUniV3StartSwapRequest) -> (bool, RPCResponse):
        """
        Starting a uniswap V3 swap, a trade of one token for another on the Uniswap v3 protocol.

        This swap is its own atomic structure, meaning after you start a swap you have immediate access to the
        buy_tokens tokens. Transactions you send after starting the swap are included in the loan until you call
        finish_inner to close the swap and return one layer up in the nested atomic structure.

        :param params: Request params
        :type params: EulithUniV3StartSwapRequest

        :returns: A tuple of a boolean indicating success and a `RPCResponse` object.
        :rtype: (bool, RPCResponse)

        :raises: requests.exceptions.HTTPError if there was an error making the request.
        """

        try:
            sell_token = params.get('sell_token').address
            amount = params.get('amount')
            pool_address = params.get('pool_address')
            fill_or_kill = params.get('fill_or_kill')
            sqrt_limit_price = params.get('sqrt_limit_price')
            recipient = params.get('recipient', None)
            pay_transfer_from = params.get('pay_transfer_from', None)

            parsed_params = {
                'sell_token': sell_token,
                'amount': amount,
                'pool_address': pool_address,
                'fill_or_kill': fill_or_kill,
                'sqrt_limit_price': sqrt_limit_price
            }

            if recipient:
                parsed_params['recipient'] = recipient

            if pay_transfer_from:
                parsed_params['pay_transfer_from'] = pay_transfer_from

            return True, self.http.make_request(RPCEndpoint('eulith_start_uniswapv3_swap'), [parsed_params])
        except requests.exceptions.HTTPError as e:

            message = e.response.json().get('error', 'request failed for unknown reason')
            return False, RPCResponse(error=message)

    def start_aave_v2_loan(self, params: EulithAaveV2StartLoanRequest) -> (bool, RPCResponse):
        """
        Start a loan using the Aave V2 protocol

        :param params: Request params
        :type params: EulithAaveV2StartLoanRequest

        :returns: A tuple of a boolean indicating success and a `RPCResponse` object.
        :rtype: (bool, RPCResponse)

        :raises: requests.exceptions.HTTPError if there was an error making the request.
        """

        try:
            tokens = params.get('tokens')
            token_params = []
            for t in tokens:
                token_params.append({
                    'token_address': t.get('token_address').address,
                    'amount': t.get('amount')
                })

            parsed_params = {
                'tokens': token_params,
            }

            return True, self.http.make_request(RPCEndpoint('eulith_start_aavev2_loan'), [parsed_params])
        except requests.exceptions.HTTPError as e:

            message = e.response.json().get('error', 'request failed for unknown reason')
            return False, RPCResponse(error=message)

    def finish_inner(self) -> (bool, RPCResponse):
        """
        Uniswap & Aave flash loans and swaps are their own "sub atomic" structures. So when you start
        one of those actions, you have to finish it by calling this method. "Finishing" here means you close the
        transaction and append it to the outer atomic structure.

        :return: A tuple that contains a boolean indicating if the request was successful, and a `RPCResponse`
        :rtype: (bool, RPCResponse)

        :raises HTTPError: In case of an error in the HTTP request.
        """

        try:
            return True, self.http.make_request(RPCEndpoint('eulith_finish_inner'), None)
        except requests.exceptions.HTTPError as e:

            message = e.response.json().get('error', 'request failed for unknown reason')
            return False, RPCResponse(error=message)

    def uniswap_v3_quote(self, params: EulithUniV3SwapQuoteRequest) -> (bool, RPCResponse):
        """
        Request a quote from Uniswap V3 for a swap between two tokens.

        :param params: Request params
        :type params: EulithUniV3SwapQuoteRequest

        :returns: A tuple of a boolean indicating success and a `RPCResponse` object.
        :rtype: (bool, RPCResponse)

        :raises: requests.exceptions.HTTPError if there was an error making the request.
        """

        try:
            parsed_params = {
                'sell_token': params.get('sell_token').address,
                'buy_token': params.get('buy_token').address,
                'amount': params.get('amount'),
                'true_for_amount_in': params.get('true_for_amount_in', True)
            }

            fee = params.get('fee', None)
            if fee:
                parsed_params['fee'] = fee.value

            return True, self.http.make_request(RPCEndpoint('eulith_uniswapv3_quote'), [parsed_params])
        except requests.exceptions.HTTPError as e:
            message = e.response.json().get('error', 'request failed for unknown reason')
            return False, RPCResponse(error=message)

    def lookup_univ3_pool(self, params: EulithUniswapPoolLookupRequest) -> (bool, RPCResponse):
        """
        Looking up information about UniSwap V3 pools.

        :param params: Request params
        :type params: EulithUniswapPoolLookupRequest

        :returns: A tuple of a boolean indicating success and a `RPCResponse` object.
        :rtype: (bool, RPCResponse)

        :raises: requests.exceptions.HTTPError if there was an error making the request.
        """

        try:
            parsed_params = {
                'token_a': params.get('token_a').address,
                'token_b': params.get('token_b').address,
                'fee': params.get('fee').value
            }
            return True, self.http.make_request(RPCEndpoint('eulith_uniswapv3_pool_lookup'), [parsed_params])
        except requests.exceptions.HTTPError as e:
            message = e.response.json().get('error', 'request failed for unknown reason')
            return False, RPCResponse(error=message)

    def lookup_token_symbol(self, symbol: TokenSymbol) -> (bool, ChecksumAddress, int):
        """
        Look up token information by ERC20 symbol.

        :param symbol: Token symbol to look up.
        :type symbol: TokenSymbol

        :return: A tuple containing a boolean indicating the success of the request,
                 the contract address of the token, and the number of decimals of the token.
        :rtype: tuple(bool, ChecksumAddress, int)
        """

        try:
            res = self.http.make_request(RPCEndpoint("eulith_erc_lookup"), [{'symbol': symbol}])
            parsed_res = res.get('result', [])
            if len(parsed_res) != 1:
                return False, RPCResponse(error=f"unexpected response for {symbol} lookup, token isn't recognized"), -1
            return True, parsed_res[0].get('contract_address'), parsed_res[0].get('decimals')
        except requests.exceptions.HTTPError as e:
            message = e.response.json().get('error', 'request failed for unknown reason')
            return False, RPCResponse(error=message), -1

    def get_gmx_addresses(self) -> (bool, dict):
        """
        Returns a dictionary of GMX contract addresses.

        :return: A tuple containing a boolean indicating success or failure, and a dictionary of GMX contract addresses.
        :rtype: tuple
        """
        try:
            res = self.http.make_request(RPCEndpoint("eulith_gmx_address_lookup"), None)
            result = res.get('result', {})
            return True, result
        except requests.exceptions.HTTPError as e:
            message = e.response.json().get('error', 'request failed for unknown reason')
            return False, RPCResponse(error=message)

    def get_gmx_positions(self, wallet_address: ChecksumAddress, collateral_tokens: List[EulithERC20],
                          index_tokens: List[EulithERC20], is_long: List[bool]) -> (bool, dict):
        """
        Get positions of the given wallet for a given set of collateral and index tokens and directions

        :param wallet_address: The address to get the positions of
        :type wallet_address: ChecksumAddress
        :param collateral_tokens: List of the collateral tokens the positions belong to
        :type collateral_tokens: List[EulithERC20]
        :param index_tokens: List of the index tokens the positions belong to
        :type index_tokens: List[EulithERC20]
        :param is_long: List of the direction of each position True is long False is short
        :type is_long: List[bool]
        :return: A tuple with the status and result
        :rtype: (bool, dict)
        """
        try:
            collateral_addresses = []
            index_addresses = []

            for t in collateral_tokens:
                collateral_addresses.append(t.address)

            for t in index_tokens:
                index_addresses.append(t.address)

            params = {
                'wallet_address': wallet_address,
                'collateral_addresses': collateral_addresses,
                'index_addresses': index_addresses,
                'is_long': is_long
            }

            res = self.http.make_request(RPCEndpoint("eulith_gmx_position_lookup"), [params])
            result = res.get('result', {})
            return True, result
        except requests.exceptions.HTTPError as e:
            message = e.response.json().get('error', 'request failed for unknown reason')
            return False, RPCResponse(error=message)

    def request_gmx_mint_glp(self, pay_token: EulithERC20, pay_amount: float, slippage: Optional[float]) -> (bool, dict):
        """
        Requests to mint GLP tokens by providing pay_token and pay_amount.
        Returns minimum GLP tokens to be minted, minimum USD value and transactions to be executed to take the position.
        We handle some of this logic server-side to keep the client light and simple.

        :param pay_token: The token to pay with
        :type pay_token: EulithERC20
        :param pay_amount: The amount of pay_token to use
        :type pay_amount: float
        :param slippage: The slippage tolerance as a percentage, defaults to None, in percentage units i.e. 0.01
        :type slippage: Optional[float]
        :return: A tuple containing whether the request was successful and the resulting dictionary
        :rtype: Tuple[bool, dict]
        """
        try:
            params = {
                'pay_token_address': pay_token.address,
                'pay_amount': pay_amount,
            }

            if slippage:
                params['slippage'] = slippage

            res = self.http.make_request(RPCEndpoint("eulith_mint_and_stake_glp"), [params])
            result = res.get('result', {})
            return True, result
        except requests.exceptions.HTTPError as e:
            message = e.response.json().get('error', 'request failed for unknown reason')
            return False, RPCResponse(error=message)

    def get_pt_quote(self, buy_pt_amount: float, market_address: ChecksumAddress) -> (bool, dict):
        try:
            params = {
                'market_address': market_address,
                'exact_pt_out': buy_pt_amount,
            }

            res = self.http.make_request(RPCEndpoint("eulith_pendle_pt_quote"), [params])
            result = res.get('result', {})
            return True, result
        except requests.exceptions.HTTPError as e:
            message = e.response.json().get('error', 'request failed for unknown reason')
            return False, RPCResponse(error=message)

    def submit_new_armor_hash(self, tx_hash: str) -> bool:
        try:
            params = {
                'tx_hash': tx_hash
            }

            res = self.http.make_request(RPCEndpoint("eulith_submit_armor_hash"), [params])
            result = res.get('result', False)
            return result
        except requests.exceptions.HTTPError as e:
            return False

    def get_deployed_execution_contracts(self) -> (bool, dict):
        try:
            response = self.http.make_request(RPCEndpoint("eulith_get_contracts"), {})
            contracts = response['result']['contracts']
            return True, contracts
        except requests.exceptions.HTTPError as e:
            message = e.response.json().get('error', 'request failed for unknown reason')
            return False, RPCResponse(error=message)

    def submit_safe_signature(self, module_address: str, owner_address: str,
                              signature: str, signed_hash: str, signature_type: str) -> (bool, dict):
        try:
            params = {
                'module_address': module_address,
                'owner_address': owner_address,
                'signature': str(signature),
                'signed_hash': signed_hash,
                'signature_type': signature_type
            }

            res = self.http.make_request(RPCEndpoint("eulith_submit_enable_safe_signature"), [params])
            result = res.get('result', False)
            return True, result
        except requests.exceptions.HTTPError as e:
            message = e.response.json().get('error', 'request failed for unknown reason')
            return False, RPCResponse(error=message)

    def get_enable_safe_tx(self, auth_address: str, owner_threshold: int, owners: List[str]) -> (bool, TxParams):
        try:
            params = {
                'auth_address': auth_address,
                'owner_threshold': owner_threshold,
                'owners': owners
            }

            res = self.http.make_request(RPCEndpoint("eulith_enable_safe_tx"), [params])
            result = res.get('result', {})
            return True, result
        except requests.exceptions.HTTPError as e:
            message = e.response.json().get('error', 'request failed for unknown reason')
            return False, RPCResponse(error=message)

    def submit_enable_safe_tx_hash(self, tx_hash: str) -> (bool, dict):
        try:
            params = {
                'tx_hash': tx_hash
            }

            res = self.http.make_request(RPCEndpoint("eulith_submit_enable_safe_hash"), [params])
            result = res.get('result', False)
            return result, {}
        except requests.exceptions.HTTPError as e:
            message = e.response.json().get('error', 'request failed for unknown reason')
            return False, RPCResponse(error=message)

    def create_draft_client_whitelist(self, owner_address: str, addresses: List[str]) -> (int, dict):
        try:
            params = {
                "owner_address": owner_address,
                "addresses": addresses
            }

            response = self.http.make_request(RPCEndpoint("eulith_create_draft_client_whitelist"), [params])
            return response["result"]["list_id"], {}
        except requests.exceptions.HTTPError as e:
            message = e.response.json().get('error', 'request failed for unknown reason')
            return -1, RPCResponse(error=message)

    def get_draft_client_whitelist_hash(self, list_id: int) -> (Optional[ClientWhitelistHash], dict):
        try:
            params = {
                "list_id": list_id
            }

            response = self.http.make_request(RPCEndpoint("eulith_get_draft_client_whitelist_hash"), [params])
            return response["result"], {}
        except requests.exceptions.HTTPError as e:
            message = e.response.json().get('error', 'request failed for unknown reason')
            return None, RPCResponse(error=message)

    def submit_draft_client_whitelist_signature(self, list_id: int, owner_address: str, signature: str, signed_hash: str) -> (bool, dict):
        try:
            params = {
                "list_id": list_id,
                "owner_address": owner_address,
                "signature": signature,
                "signed_hash": signed_hash,
            }

            response = self.http.make_request(RPCEndpoint("eulith_submit_draft_client_whitelist_signature"), [params])
            return response["result"], {}
        except requests.exceptions.HTTPError as e:
            message = e.response.json().get('error', 'request failed for unknown reason')
            return False, RPCResponse(error=message)

    def get_current_client_whitelist(self, owner_address: str, *, is_draft: bool) -> (Optional[ClientWhitelist], dict):
        try:
            params = {
                "owner_address": owner_address,
                "is_draft": is_draft,
            }

            response = self.http.make_request(RPCEndpoint("eulith_get_current_client_whitelist"), [params])
            return response["result"], {}
        except requests.exceptions.HTTPError as e:
            message = e.response.json().get('error', 'request failed for unknown reason')
            return None, RPCResponse(error=message)


class EulithWeb3(Web3):
    """
    The main drop-in replacement for Web3.py for users of Eulith

    :ivar eulith_data: internal methods to help with Eulith functionality
    :type eulith_data: EulithData
    :ivar middleware_onion: web3py middleware
    :type middleware_onion: MiddlewareOnion
    :ivar v0: versioned namespace for Eulith interactions
    :type v0: v0
    """

    def __init__(self,
                 eulith_url: Union[URI, str],
                 eulith_refresh_token: str,
                 signing_middle_ware: Any = None,
                 private: bool = False,
                 **kwargs
                 ) -> None:
        """
        :param eulith_url: The Eulith endpoint; different endpoints will point this library to different chains.
        :type eulith_url: Union[URI, str]
        :param eulith_refresh_token: The refresh token used to authenticate the Eulith API
        :type eulith_refresh_token: str
        :param signing_middle_ware: The signing middleware used to sign transactions.
        :type signing_middle_ware: Any
        :param private: Flag that indicates whether transactions are routed through a private mempool
        :type private: bool
        :param kwargs: Varying number of keyword or named arguments that should be passed to the `Web3` class.
        :type kwargs: dict
        """

        if signing_middle_ware:
            eulith_url = add_params_to_url(eulith_url, {'auth_address': signing_middle_ware.address})

        self.eulith_data = EulithData(eulith_url, eulith_refresh_token, private)
        http = self._make_http()
        kwargs.update(provider=http)
        super().__init__(**kwargs)

        self.wallet_address = None

        if signing_middle_ware:
            self.wallet_address = signing_middle_ware.address
            self.signer = signing_middle_ware.signer
            self.middleware_onion.add(signing_middle_ware)

        self.middleware_onion.add(eulith_atomic_middleware)
        self.middleware_onion.add(web3.middleware.request_parameter_normalizer)
        self.middleware_onion.add(web3.middleware.pythonic_middleware, "eulith_pythonic")
        self.middleware_onion.add(eulith_api_token_middleware)
        self.v0 = v0(self)
        self.websocket_conn = EulithWebsocketConnection(self)

        # Config for `wait_for_transaction_receipt_with_confirmations`
        self.default_confirmations = 3
        self._cached_confirmations_timeout_secs = None

    def _eulith_send_atomic(self, params) -> RPCResponse:
        """
        This function is used to send an atomic transaction.

        :param params: A dictionary that contains the parameters required for the transaction.
        :type params: dict

        :return: A `RPCResponse` object that holds the response from the server.
        :rtype: RPCResponse
        """

        return self.eulith_data.send_transaction(params)

    def eulith_start_transaction(self, account: str, gnosis: str = "") -> None:
        """
        Begins an atomic transaction with your wallet as the authorized address,
        or optionally with your gnosis safe as msg.sender

        :param account: Your ETH wallet address
        :type account: str
        :param gnosis: Optional. Gnosis Safe address.
        :type gnosis: str, optional

        :raises TypeError: If the `account` is not a hex-formatted address or the `gnosis` is not a hex-formatted address.
        """

        if not is_hex_address(account):
            raise TypeError("account must be a hex-formatted address")
        if len(gnosis) > 0 and not is_hex_address(gnosis):
            raise TypeError("gnosis must either be blank or a hex-formatted address")
        self.eulith_data.start_transaction(account, gnosis)

    def eulith_commit_transaction(self) -> TxParams:
        """
        Serializes your pending atomic unit into a single transaction and returns the params to be signed

        :returns: The parameters of the committed transaction.
        :rtype: TxParams
        """

        return self.eulith_data.commit()

    def eulith_rollback_transaction(self):
        """
        Rollback a transaction, discard the current atomic transaction
        """

        self.eulith_data.rollback()

    def eulith_contract_address(self, account: str) -> str:
        """
        Retrieve the toolkit contract address bearing a one-to-one relationship to the `account` address.
        One toolkit contract is generated per wallet address.

        :param account: The hex formatted address of the account.
        :type account: str

        :returns: The hex formatted address of the contract. If no contract is found, an empty string is returned.
        :rtype: str

        :raises: TypeError: If `account` is not a hex formatted address.
        :raises: EulithRpcException: If an error occurs while making the request.
        """

        if not is_hex_address(account):
            raise TypeError("`account` must be a hex formatted address")

        status, contracts = self.eulith_data.get_deployed_execution_contracts()

        if not status:
            raise EulithRpcException(contracts)

        for c in contracts:
            if c['authorized_address'].lower() == account.lower():
                return c['contract_address']
        return ""

    def eulith_create_contract_if_not_exist(self, account: str) -> str:
        """
        Check if a toolkit contract exists for an account, and creates a new unique contract for the account
        if it doesn't already exist.

        :param account: The hex formatted address of the account.
        :type account: str

        :return: The hex formatted address of the contract.
        :rtype: str
        """

        c = self.eulith_contract_address(account)
        if c == "":
            c = self.eulith_create_contract(account)

        return c

    def eulith_create_contract(self, account: str, contract_type: Optional[str] = None) -> Union[str, TxParams]:
        """
        Creates a new toolkit or armor contract for the specified authorized wallet address (account).
        Toolkit contracts are deployed by us, we require the client to deploy their own armor contract.
        Hence, you might either get a contract address back as a string or a ready-to-sign TxParams
        object that you will need to sign and send yourself.

        :param account: The hex formatted address of the account.
        :type account: str
        :param contract_type: Optional contract type, defaults to toolkit contract.
                              Can also pass `armor` to generate new DeFi armor deployment transaction
        :type contract_type: Optional[str]

        :return: The hex formatted address of the newly created contract.
        :rtype: str
        """

        if not is_hex_address(account):
            raise TypeError("account must be a hex formatted address")

        if contract_type and contract_type != 'armor':
            raise TypeError(f"we currently only support toolkit and armor contracts. "
                            f"If you're trying to deploy a toolkit contract, leave contract_type blank. "
                            f"Unrecognized type: {contract_type}")

        params = {
            'authorized_address': account
        }

        if contract_type:
            params['contract_type'] = contract_type

        try:
            response = self.manager.provider.make_request("eulith_new_contract", [params])
            handle_rpc_response(response)
            result = response['result']
            if not contract_type:
                tx_receipt = self.wait_for_transaction_receipt_with_confirmations(result['new_contract_tx_hash'])
                check_tx_receipt(tx_receipt)
                return result['contract_address']
            elif contract_type == 'armor':
                return result
        except requests.exceptions.HTTPError as e:
            message = e.response.json().get('error', 'request failed for unknown reason')
            raise EulithRpcException(message)

    def eulith_refresh_api_token(self):
        """
        API tokens have a 24hr lifespan, so this function refreshes upon calling.
        """

        self.eulith_data.refresh_api_token()
        http = self._make_http()
        self.provider = http

    def eulith_refresh_api_token_if_necessary(self):
        """
        Ensures that the API token is always valid and can be used to make requests to the blockchain without interruption
        """

        if self.eulith_data.is_close_to_expiry():
            self.eulith_refresh_api_token()

    def eulith_swap_quote(self, params: EulithSwapRequest) -> [float, List[TxParams]]:
        """
        Gets a swap quote which contains information about the price and liquidity of assets. Returns the price of the
        quote and the transactions needed to execute the trade

        :param params: The parameters for the swap.
        :type params: EulithSwapRequest

        :returns: A tuple containing the price of the swap and a list of `TxParams` objects that represent
                  the transactions required for the swap.
        :rtype: Tuple[float, List[TxParams]]

        :raises: EulithRpcException: If there is an error in the response from the Ethereum node.
        """

        status, result = self.eulith_data.swap_quote(params)
        if status:
            price = result.get('result', {}).get('price', 0.0)
            txs = result.get('result', {}).get('txs', [])
            return price, txs
        else:
            raise EulithRpcException(result)

    def _make_http(self):
        """
        Creates an HTTP provider that can be used to make requests to the specified blockchain node

        :returns: An instance of the `HTTPProvider` class.
        :rtype: HTTPProvider
        """

        url = self.eulith_data.eulith_url
        if self.eulith_data.private:
            url = add_params_to_url(url, {'private': 'true'})

        headers = get_headers(url, self.eulith_data.api_access_token.token)

        http = HTTPProvider(endpoint_uri=url, request_kwargs={
            'headers': headers
        })

        return http

    # If the eulith_data.atomic flag is not set, the function will wait for each transaction receipt using the
    # wait_for_transaction_receipt_with_confirmations method
    def eulith_send_multi_transaction(self, txs: [TxParams]) -> Optional[TxReceipt]:
        """
        Sends multiple transactions to the blockchain (or appends to the current atomic context) in a single batch,
        with each transaction executed one after the other (order is preserved).

        :param txs: List of `TxParams` objects, each representing a single transaction to be executed.
        :type txs: List[TxParams]
        """

        r = None

        for tx in txs:
            tx_hash = self.eth.send_transaction(tx)
            if not self.eulith_data.atomic:
                r = self.wait_for_transaction_receipt_with_confirmations(tx_hash)
                check_tx_receipt(r)

        return r

    def eulith_get_erc_token(self, symbol: TokenSymbol) -> Union[EulithERC20, EulithWETH]:
        """
        Obtains an instance of either the `EulithERC20` or `EulithWETH` class based on the provided token symbol.

        :param symbol: Symbol of the token to look up.
        :type symbol: TokenSymbol

        :returns: An instance of either the `EulithERC20` or `EulithWETH` class.
        :rtype: Union[EulithERC20, EulithWETH]

        :raises: EulithRpcException if there was an error with the RPC request
        """

        status, contract_address_or_error, decimals = self.eulith_data.lookup_token_symbol(symbol)
        if status:
            if symbol == TokenSymbol.WETH:
                return EulithWETH(self, contract_address_or_error)
            else:
                return EulithERC20(self, contract_address_or_error, decimals)
        else:
            raise EulithRpcException(contract_address_or_error)

    def parse_uni_quote_to_swap_request(self, res, fill_or_kill: bool, recipient: Optional[ChecksumAddress],
                                        pay_transfer_from: Optional[ChecksumAddress]) -> (
    float, UniswapPoolFee, EulithUniV3StartSwapRequest):
        """
        This function takes in the result of Uniswap swap quote and converts it into a swap request that can be passed
        to the `start_swap` function. Rather than manually extracting and formatting the necessary data,
        this function does the work for you. The parse_uni_quote_to_swap_request function returns an instance of the
        EulithUniV3StartSwapRequest class, which is the expected input type for the start_uniswap_v3_swap function.
        This makes it easy to pass the swap request directly to the start_uniswap_v3_swap function after it has been
        generated by the parse_uni_quote_to_swap_request function.

        :param res: The result of a Uniswap swap quote, which is a dictionary containing information about the swap.
        :type res: dict
        :param fill_or_kill: Default True doesn't allow any partial fills. If the order can't be filled
                             fully at the specified price, we revert.
        :type fill_or_kill: bool
        :param recipient: The Ethereum address of the recipient of the swap. This is an optional parameter.
        :type recipient: Optional[ChecksumAddress]
        :param pay_transfer_from: The Ethereum address of the account that will pay the sell_token to cover the swap.
        :type pay_transfer_from: Optional[ChecksumAddress]

        :returns: A tuple containing the price of the swap, the pool fee, and the swap request.
        :rtype: Tuple(float, UniswapPoolFee, EulithUniV3StartSwapRequest)
        """

        # Get the result of the Uniswap swap quote from the 'result' key of the res dictionary.
        result = res.get('result')

        price = result.get('price')
        sell_token_address = result.get('sell_token')
        sell_token = EulithERC20(self, sell_token_address)
        amount = result.get('amount')
        pool_address = result.get('pool_address')
        limit_price = result.get('sqrt_limit_price')
        fee = result.get('fee')
        true_for_amount_in = result.get('true_for_amount_in')

        if not true_for_amount_in:
            amount *= -1.0  # make negative if we want exact amount out

        swap_request = EulithUniV3StartSwapRequest(sell_token=sell_token,
                                                   amount=amount,
                                                   pool_address=self.to_checksum_address(pool_address),
                                                   fill_or_kill=fill_or_kill,
                                                   sqrt_limit_price=limit_price,
                                                   recipient=recipient,
                                                   pay_transfer_from=pay_transfer_from)

        return price, UniswapPoolFee(fee), swap_request

    def wait_for_transaction_receipt_with_confirmations(self, tx_hash: HexBytes, *, confirmations=0) -> TxReceipt:
        """
        Wait for a receipt for the transaction hash, optionally waiting for a number of confirmed blocks before
        returning.

        If calling this function from within `EulithWeb3` with `confirmations` greater than zero, prefer setting it to
        `confirmations=self.default_confirmations`. This is so that test code running against Anvil can set
        `self.default_confirmations` to 0 and avoid timing out waiting for blocks that will never come.

        :param tx_hash: The hash of the transaction to wait for.
        :type tx_hash: HexBytes
        :param confirmations: If greater than zero, this function will wait until
                              current_block_number == tx_block_number + confirmations
        :type confirmations: int

        :return: The receipt of the transaction.
        :rtype: TxReceipt
        """
        tx_receipt = self.eth.wait_for_transaction_receipt(tx_hash)

        if confirmations == 0:
            return tx_receipt

        attempts = 0
        max_attempts = 3
        timeout_secs = self._get_confirmation_timeout_secs()
        last_block_number_seen = None

        while True:
            attempts += 1

            current_block_number = self.eth.get_block_number()
            if current_block_number >= tx_receipt["blockNumber"] + confirmations:
                return tx_receipt

            if last_block_number_seen is not None and current_block_number > last_block_number_seen:
                # We have made progress, so we can reset the number of attempts.
                attempts = 0

            last_block_number_seen = current_block_number

            if attempts == max_attempts:
                raise EulithRpcException(f"failed to confirm transaction {tx_receipt['transactionHash']}")

            # We do not do exponential backoff here as we expect blocks to be created at a regular rate.
            time.sleep(timeout_secs)

    def _get_confirmation_timeout_secs(self) -> float:
        if self._cached_confirmations_timeout_secs is not None:
            return self._cached_confirmations_timeout_secs

        # The duration of time to wait for confirmation is strongly dependent on how quickly the chain creates new
        # blocks, which varies from chain to chain (e.g., Arbitrum is much faster than Ethereum mainnet). We take the
        # average time of the last 3 blocks, add half a second as a hedge, and cap the timeout at 30 seconds.
        current_block = self.eth.get_block("latest")
        current_block_minus_3 = self.eth.get_block(current_block["number"] - 3)
        timeout_secs = (current_block["timestamp"] - current_block_minus_3["timestamp"]) / 3.0
        timeout_secs += 0.5
        timeout_secs = min(timeout_secs, 30.0)

        self._cached_confirmations_timeout_secs = timeout_secs
        return self._cached_confirmations_timeout_secs


# Namespace
class v0:
    """
    Simplified and versioned access to the methods and functionality of `EulithWeb3`.
    """

    def __init__(self, ew3: EulithWeb3):
        """
        Initialize the `v0` class by taking an instance of `EulithWeb3` as an argument.

        :param ew3: An instance of the `EulithWeb3` class.
        :type ew3: EulithWeb3
        """

        self.ew3 = ew3

    def send_multi_transaction(self, txs: List[TxParams]) -> TxReceipt:
        """
        Sends multiple transactions to the blockchain (or appends to the current atomic context) in a single batch,
        with each transaction executed one after the other (order is preserved).

        :param txs: List of `TxParams` objects, each representing a single transaction to be executed.
        :type txs: List[TxParams]
        """

        return self.ew3.eulith_send_multi_transaction(txs)

    def start_atomic_transaction(self, account: str, gnosis: str = ""):
        """
        Begins an atomic transaction with your wallet as the authorized address,
        or optionally with your gnosis safe as msg.sender

        :param account: Your ETH wallet address
        :type account: str
        :param gnosis: Optional. Gnosis Safe address.
        :type gnosis: str, optional

        :raises TypeError: If the `account` is not a hex-formatted address or the `gnosis` is not a hex-formatted address.
        """

        return self.ew3.eulith_start_transaction(account, gnosis)

    def commit_atomic_transaction(self) -> TxParams:
        """
        Serializes your pending atomic unit into a single transaction and returns the params to be signed

        :returns: The parameters of the committed transaction.
        :rtype: TxParams
        """

        return self.ew3.eulith_commit_transaction()

    def rollback_atomic_transaction(self):
        """
        Rollback a transaction, discard the current atomic transaction
        """

        return self.ew3.eulith_rollback_transaction()

    def get_toolkit_contract_address(self, account: str) -> str:
        """
        Retrieve the toolkit contract address bearing a one-to-one relationship to the `account` address.
        One toolkit contract is generated per wallet address.

        :param account: The hex formatted address of the account.
        :type account: str

        :returns: The hex formatted address of the contract. If no contract is found, an empty string is returned.
        :rtype: str

        :raises: TypeError: If `account` is not a hex formatted address.
        :raises: EulithRpcException: If an error occurs while making the request.
        """

        return self.ew3.eulith_contract_address(account)

    def get_armor_and_safe_addresses(self, authorized_trading_address: str) -> (str, str):
        """
        Get the armor and safe addresses for a specific authorized_trading_address.

        This method retrieves the armor and safe addresses associated with the provided authorized_trading_address.

        :param authorized_trading_address: The Ethereum address (str) to search for.
        :return: A tuple (str, str) containing the contract address and safe address, respectively.
                 If no match is found, an empty tuple ('', '') is returned.

        :raises EulithRpcException: If there is an issue fetching the deployed execution contracts.
        """
        status, contracts = self.ew3.eulith_data.get_deployed_execution_contracts()

        if not status:
            raise EulithRpcException(contracts)

        for c in contracts:
            if c['authorized_address'].lower() == authorized_trading_address.lower():
                return c['contract_address'], c['safe_address']

        return '', ''

    def ensure_toolkit_contract(self, account: str) -> str:
        """
        Check if a toolkit contract exists for an account, and creates a new unique contract for the account
        if it doesn't already exist.

        :param account: The hex formatted address of the account.
        :type account: str

        :return: The hex formatted address of the contract.
        :rtype: str
        """

        return self.ew3.eulith_create_contract_if_not_exist(account)

    def create_toolkit_contract(self, account: str) -> str:
        """
        Creates a new toolkit contract for the specified authorized wallet address (account).

        :param account: The hex formatted address of the account.
        :type account: str

        :return: The hex formatted address of the newly created contract.
        :rtype: str
        """

        return self.ew3.eulith_create_contract(account)

    def get_armor_deploy_tx(self, account: str) -> TxParams:
        """
        Generates transaction to create a new armor and safe contract for the specified authorized wallet address (account).

        :param account: The hex formatted address of the account.
        :type account: str

        :return: The TxParams to sign and send in order to deploy your new armor and safe contracts.
        :rtype: TxParams
        """
        return self.ew3.eulith_create_contract(account, 'armor')

    def refresh_api_token(self):
        """
        API tokens have a 24hr lifespan, so this function refreshes it upon calling.
        """

        self.ew3.eulith_refresh_api_token()

    def ensure_valid_api_token(self):
        """
        API tokens expire 24 hours after they are created. Refresh the token if necessary
        """

        self.ew3.eulith_refresh_api_token_if_necessary()

    def get_erc_token(self, symbol: TokenSymbol) -> Union[EulithERC20, EulithWETH]:
        """
        Obtains an instance of either the `EulithERC20` or `EulithWETH` class based on the provided token symbol.

        :param symbol: Symbol of the token to look up.
        :type symbol: TokenSymbol

        :returns: An instance of either the `EulithERC20` or `EulithWETH` class.
        :rtype: Union[EulithERC20, EulithWETH]

        :raises: EulithRpcException if there was an error with the RPC request
        """

        return self.ew3.eulith_get_erc_token(symbol)

    def get_swap_quote(self, params: EulithSwapRequest) -> (float, List[TxParams]):
        """
        Gets a swap quote which contains information about the price and liquidity of assets. Returns the price of the
        quote and the transactions needed to execute the trade

        :param params: The parameters for the swap.
        :type params: EulithSwapRequest

        :returns: A tuple containing the price of the swap and a list of `TxParams` objects that represent
                  the transactions required for the swap.
        :rtype: Tuple(float, List[TxParams])

        :raises: EulithRpcException: If there is an error in the response from the Ethereum node.
        """

        return self.ew3.eulith_swap_quote(params)

    def short_on(self, params: EulithShortOnRequest) -> float:
        """
        Request the Eulith API to open a levered short position on a token.

        :param params: Request parameters
        :type params: EulithShortOnRequest

        :return: the leverage of the short position
        :rtype: float

        :raises EulithRpcException: if the short position request fails
        """

        status, res = self.ew3.eulith_data.short_on(params)
        if status:
            leverage = res.get('result', {}).get('leverage', 0.0)
            return leverage
        else:
            raise EulithRpcException(res)

    def short_off(self, params: EulithShortOffRequest) -> float:
        """
        Makes a request to the Eulith API to unwind an existing short.

        :param params: Request parameters
        :type params: EulithShortOffRequest

        :return: The amount of released collateral.
        :rtype: float

        :raises EulithRpcException: If the short off request fails.
        """

        status, res = self.ew3.eulith_data.short_off(params)
        if status:
            released_collateral = res.get('result', {}).get('released_collateral', 0.0)
            return released_collateral
        else:
            raise EulithRpcException(res)

    def get_univ3_pool(self, params: EulithUniswapPoolLookupRequest) -> EulithUniswapV3Pool:
        """
        Looking up information about UniSwap V3 pools.

        :param params: Request parameters
        :type params: EulithUniswapPoolLookupRequest

        :return: An instance of `EulithUniswapV3Pool` class representing the Uniswap pool information.
        :rtype: EulithUniswapV3Pool

        :raises EulithRpcException: If the Uniswap V3 pool lookup fails or if the response from the server is unexpected.
        """

        status, res = self.ew3.eulith_data.lookup_univ3_pool(params)
        if status:
            result = res.get('result')
            if len(result) != 1:
                raise EulithRpcException(f"uniswap v3 pool lookup came back with an unexpected response: {result}")
            inner_result = result[0]

            token_zero = inner_result.get('token_zero')
            token_one = inner_result.get('token_one')
            fee = inner_result.get('fee')
            pool_address = inner_result.get('pool_address')
            return EulithUniswapV3Pool(self.ew3, self.ew3.to_checksum_address(pool_address), UniswapPoolFee(fee),
                                       self.ew3.to_checksum_address(token_zero), self.ew3.to_checksum_address(token_one))
        else:
            raise EulithRpcException(res)

    # returns fee (float) as percent: i.e. 0.001 = 0.1%
    def start_flash_loan(self, params: Union[EulithUniV3StartLoanRequest, EulithAaveV2StartLoanRequest]) -> float:
        """
        Initiates a flash loan. A flash loan is a type of loan that can be taken and repaid within a single transaction.
        This is a generic wrapper around Uniswap flash loans and Aave flash loans. You can pass either as the params
        and it will handle the request appropriately.

        :param params: The parameters required to initiate the flash loan.
        :type params: Union[EulithUniV3StartLoanRequest, EulithAaveV2StartLoanRequest]

        :return: The fee of the flash loan.
        :rtype: float

        :raises EulithRpcException: If there was an error with the request to the Ethereum node.
        """

        param_keys = params.keys()
        if 'borrow_token_a' in param_keys:
            status, res = self.ew3.eulith_data.start_uniswap_v3_loan(params)
        else:
            status, res = self.ew3.eulith_data.start_aave_v2_loan(params)

        if status:
            fee = int(res.get('result'), 16)
            return fee / INT_FEE_TO_FLOAT_DIVISOR
        else:
            raise EulithRpcException(res)

    def start_uni_swap(self, params: EulithUniV3StartSwapRequest) -> float:
        """
        Starting a uniswap V3 swap, a trade of one token for another on the Uniswap v3 protocol.

        This swap is its own atomic structure, meaning after you start a swap you have immediate access to the
        buy_tokens tokens. Transactions you send after starting the swap are included in the loan until you call
        finish_inner to close the swap and return one layer up in the nested atomic structure.

        :param params: Request parameters
        :type params: EulithUniV3StartSwapRequest

        :return: The fee of the Uniswap V3 swap, represented as a percentage.
        :rtype: float

        :raises EulithRpcException: If there was an error with the request to the Eulith server
        """

        status, res = self.ew3.eulith_data.start_uniswap_v3_swap(params)
        if status:
            fee = int(res.get('result'), 16)
            return fee / INT_FEE_TO_FLOAT_DIVISOR
        else:
            raise EulithRpcException(res)

    def get_univ3_best_price_quote(self, sell_token: EulithERC20, buy_token: EulithERC20, amount: float,
                                   true_for_amount_in: Optional[bool] = True, fill_or_kill: Optional[bool] = True,
                                   recipient: Optional[ChecksumAddress] = None,
                                   pay_transfer_from: Optional[ChecksumAddress] = None) -> (float, float, EulithUniV3StartSwapRequest):
        """
        Get the best price quote for a given token exchange on Uniswap V3.

        :param sell_token: The token that is to be sold.
        :type sell_token: EulithERC20
        :param buy_token: The token that is to be bought.
        :type buy_token: EulithERC20
        :param amount: The amount of the trade. If true_for_amount_in, this is the exact sell_amount in. Otherwise, the exact buy_amount out.
        :type amount: float
        :param true_for_amount_in: Whether the `amount` is in `sell_token` IN or `buy_token` OUT. Defaults to True.
        :type true_for_amount_in: Optional[bool]
        :param fill_or_kill: Default True doesn't allow any partial fills. If the order can't be filled fully at the specified price, revert.
        :type fill_or_kill: Optional[bool]
        :param recipient: The address of the recipient of the `buy_token`. Defaults to msg.sender
        :type recipient: Optional[ChecksumAddress]
        :param pay_transfer_from: The address to pay the sell side of the transaction. Defaults to msg.sender
        :type pay_transfer_from: Optional[ChecksumAddress]

        :return: A tuple containing three values:
            - price (float): The price of the `buy_token` in terms of `sell_token`.
            - fee (float): The fee for the transaction.
            - swap_request (EulithUniV3StartSwapRequest): The swap request details. These can be immediately used to execute the swap
        :rtype: Tuple(float, float, EulithUniV3StartSwapRequest)

        :raises EulithRpcException: If the status of the response from the `uniswap_v3_quote` method is False.
        """

        parsed_params = EulithUniV3SwapQuoteRequest(
            sell_token=sell_token,
            buy_token=buy_token,
            amount=amount,
            true_for_amount_in=true_for_amount_in,
            fee=None)
        status, res = self.ew3.eulith_data.uniswap_v3_quote(parsed_params)
        if status:
            price, fee, swap_request = self.ew3.parse_uni_quote_to_swap_request(res, fill_or_kill, recipient,
                                                                                pay_transfer_from)
            return price, fee / INT_FEE_TO_FLOAT_DIVISOR, swap_request
        else:
            raise EulithRpcException(res)

    def finish_inner(self) -> int:
        """
        Finishes the actual exchange of tokens in the swap or loan
        and returns the scope back to the outer atomic context. Remember, uniswap swaps and loans are SUB ATOMIC,
        meaning they have their own atomic structure that you can add to. When you're done with those transactions
        you need to close them with this method

        :returns: The number of transactions appended to the root atomic transaction
        :rtype: int

        :raises EulithRpcException: If there was an error with the RPC request.
        """

        status, res = self.ew3.eulith_data.finish_inner()
        if status:
            return int(res.get('result'), 16)
        else:
            raise EulithRpcException(res)

    # returns price (float), fee (float) as percent: i.e. 0.001 = 0.1%
    def start_flash(self, params: FlashRequest) -> (float, float):
        """
        A generic wrapper for any kind of flash transaction between any two tokens.


        :param params: The FlashRequest object containing information about the flash
        :type params: FlashRequest

        :returns: A tuple of two floats representing (price, fee) of the flash.
                  If take and pay are the same token, the price is 1.0
        :rtype: Tuple(float, float)
        """

        amount = params.get('take_amount')
        pay_transfer_from = params.get('pay_transfer_from', None)
        recipient = params.get('recipient', None)

        if params.get('take').address.lower() == params.get('pay').address.lower():
            fee = self.start_flash_loan(EulithUniV3StartLoanRequest(
                borrow_token_a=params.get('take'),
                borrow_amount_a=amount,
                borrow_token_b=None,
                borrow_amount_b=None,
                pay_transfer_from=pay_transfer_from,
                recipient=recipient
            ))

            return 1.0, fee
        else:
            price, fee, swap_request = self.get_univ3_best_price_quote(params.get('pay'),
                                                                       params.get('take'),
                                                                       amount,
                                                                       False, True, recipient, pay_transfer_from)
            fee = self.start_uni_swap(swap_request)
            return price, fee

    def pay_flash(self) -> int:
        """
        Pays and closes an open flash transaction.

        :returns: The number of transactions in the current atomic unit.
        :rtype: int
        """

        return self.finish_inner()

    def get_gmx_addresses(self) -> dict:
        """
        Returns the addresses of various contracts used by GMX protocol.

        :return: A dictionary with the contract addresses as values and their names as keys.
        :rtype: dict
        """
        status, result = self.ew3.eulith_data.get_gmx_addresses()
        if status:
            return result
        else:
            raise EulithRpcException(result)

    def deploy_new_armor(self, authorized_trading_address: ChecksumAddress, override_tx_params: TxParams = None) -> (str, str):
        """
        Deploys new armor contract using the current wallet configured in EulithWeb3. Note that the
        deploying wallet is NOT the same thing as the authorized_address on the armor contract. The user
        must choose the authorized trading address and pass it into this method.

        :param authorized_trading_address: (str) The address authorized to execute trades through the new armor contract
        :type authorized_trading_address: ChecksumAddress
        :param override_tx_params: (TxParams, optional) The optional transaction parameters
                                   to override default values (like gas, gas_price, etc). Defaults to None.
        :type override_tx_params: TxParams
        :return: (tuple) A tuple of armor and safe addresses.
        :rtype: tuple

        :raises EulithRpcException: If submitting new armor tx hash to the server fails.
        :type: EulithRpcException
        """
        deploy_armor_tx = self.get_armor_deploy_tx(authorized_trading_address)

        if override_tx_params:
            deploy_armor_tx.update(override_tx_params)

        h = self.ew3.eth.send_transaction(deploy_armor_tx)
        tx_receipt = self.ew3.wait_for_transaction_receipt_with_confirmations(h, confirmations=self.ew3.default_confirmations)
        check_tx_receipt(tx_receipt)

        accepted = self.ew3.eulith_data.submit_new_armor_hash(h.hex())

        if not accepted:
            raise EulithRpcException("failed to submit new armor tx hash to the server")

        return self.get_armor_and_safe_addresses(authorized_trading_address)

    def submit_enable_module_signature(self, authorized_trading_address: str, signer: Signer) -> bool:
        """
        Submits a signature to enable a module for a safe. Note that the signature must come from a safe owner,
        but submitting a signature here DOES NOT add the signing address as an owner of the safe. The owners are
        specified in a later initialization step.

        :param authorized_trading_address: (str) The address authorized to execute trades through the new armor contract
        :type authorized_trading_address: ChecksumAddress
        :param signer: The signer to apply the signature to enable the armor module
        :type signer: Signer

        :return: Status true or false
        :rtype: bool
        """
        aa, sa = self.get_armor_and_safe_addresses(authorized_trading_address)
        safe = ISafe(self.ew3, self.ew3.to_checksum_address(sa))

        enable_module_tx = safe.enable_module(self.ew3.to_checksum_address(aa), override_tx_parameters={
            'gas': 0,
            'nonce': 0,
        })

        checksum_sa = self.ew3.to_checksum_address(sa)

        enable_data = enable_module_tx.get('data')
        tx_hash = safe.get_transaction_hash(checksum_sa, 0, enable_data,
                                            0, 0, 0, 0, '0x0000000000000000000000000000000000000000',
                                            '0x0000000000000000000000000000000000000000', 0)

        typed_data_payload = get_enable_module_typed_data(checksum_sa, self.ew3.eth.chain_id, enable_data)
        signature = signer.sign_typed_data(typed_data_payload, tx_hash)

        serialized_signature = normalize_signature(signature)

        status, result = self.ew3.eulith_data.submit_safe_signature(aa, str(signer.address),
                                                                    serialized_signature,
                                                                    f'0x{tx_hash.hex()}', 'enable_module')

        if not status:
            raise EulithRpcException(result)

        return True

    def enable_armor(self, auth_address: str, owner_threshold: int, owners: List[str], override_tx_params: TxParams = None) -> bool:
        """
        Enable the armor for the contract by creating and submitting an initialization transaction. Note that
        the owners passed here MUST include the addresses of the signatures you submitted in the enable
        module step AND you must have submitted at least `owner_threshold` signatures in that step.

        :param auth_address: The authorized address of the Armor contract.
        :type auth_address: str
        :param owner_threshold: The minimum number of owner signatures required to authorize a transaction on the safe
        :type owner_threshold: int
        :param owners: A list of owner addresses that are allowed to manage the contract.
        :type owners: List[str]
        :param override_tx_params: Optional dictionary to override transaction parameters.
        :type override_tx_params: TxParams, optional

        :return: True if the transaction is successfully submitted, False otherwise.
        :rtype: bool

        :raises EulithRpcException: If there is an issue with the Eulith RPC request.
        """
        status, result = self.ew3.eulith_data.get_enable_safe_tx(auth_address, owner_threshold, owners)
        if not status:
            raise EulithRpcException(result)

        if override_tx_params:
            result.update(override_tx_params)
        else:
            result.update({'from': self.ew3.wallet_address})

        h = self.ew3.eth.send_transaction(result)
        tx_receipt = self.ew3.wait_for_transaction_receipt_with_confirmations(h, confirmations=self.ew3.default_confirmations)
        check_tx_receipt(tx_receipt)

        status, error = self.ew3.eulith_data.submit_enable_safe_tx_hash(h.hex())
        if error:
            raise EulithRpcException(error)
        return status

    def create_draft_client_whitelist(self, owner_address: str, addresses: List[str]) -> int:
        """
        Create a draft of the client whitelist for an Armor contract. This method only creates a draft; to enable the
        whitelist, use `submit_draft_client_whitelist_signature` to submit signatures from the threshold of owners of
        the Armor's safe.

        :param owner_address: The owner address for the whitelist.
        :type owner_address: str
        :param addresses: The list of addresses to include on the whitelist.
        :type addresses: List[str]

        :return: An opaque identifier for the whitelist, to be passed to `submit_draft_client_whitelist_signature`.
        :rtype: int

        :raises EulithRpcException: If there is an issue with the Eulith RPC request.
        """
        list_id, error = self.ew3.eulith_data.create_draft_client_whitelist(owner_address, addresses)
        if error:
            raise EulithRpcException(error)

        return list_id

    def submit_draft_client_whitelist_signature(self, list_id: int, signer: Signer) -> bool:
        """
        Submit a signature for a draft client whitelist in order to enable it once signatures have been received from
        the threshold of owners.

        :param list_id: The ID of the whitelist, as returned by `create_draft_client_whitelist`.
        :type list_id: int
        :param signer: The signer to sign the whitelist hash with. Must be an owner of the safe.
        :type signer: Signer

        :return: True if the whitelist was enabled, False otherwise.
        :rtype: bool

        :raises EulithRpcException: If there is an issue with the Eulith RPC request.
        """
        hsh, error = self.ew3.eulith_data.get_draft_client_whitelist_hash(list_id)
        if error:
            raise EulithRpcException(error)

        typed_data_payload = get_client_whitelist_typed_data(hsh["hash_input"])
        signature = signer.sign_typed_data(typed_data_payload, HexBytes(hsh["hash"]))
        serialized_signature = normalize_signature(signature)

        status, error = self.ew3.eulith_data.submit_draft_client_whitelist_signature(list_id, signer.address, serialized_signature, hsh["hash"])
        if error:
            raise EulithRpcException(error)

        return status

    def get_current_client_whitelist(self, owner_address: str, *, is_draft: bool) -> Optional[ClientWhitelist]:
        """
        Retrieve either the current draft or published version of the user's client whitelist.

        :param owner_address: The owner of the whitelist to retrieve.
        :type owner_address: str
        :param is_draft: Whether to return the draft or the published version.
        :type is_draft: bool

        :return: The client whitelist, or None if it does not exist.
        :rtype: bool

        :raises EulithRpcException: If there is an issue with the Eulith RPC request.
        """
        whitelist, error = self.ew3.eulith_data.get_current_client_whitelist(owner_address, is_draft=is_draft)
        if error:
            raise EulithRpcException(error)

        return whitelist

def eulith_atomic_middleware(
        make_request: Callable[[RPCEndpoint, Any], Any], web3: "Web3") -> Callable[[RPCEndpoint, Any], RPCResponse]:
    def middleware(method: RPCEndpoint, params: Any) -> RPCResponse:
        try:
            if method != "eth_sendTransaction" or not web3.eulith_data.atomic:
                return make_request(method, params)

            return cast(EulithWeb3, web3)._eulith_send_atomic(params)
        except requests.exceptions.HTTPError as e:
            message = e.response.json().get('error', 'request failed for unknown reason')
            raise EulithRpcException(message)

    return middleware


def eulith_api_token_middleware(make_request: Callable[[RPCEndpoint, Any], Any], web3: "Web3") -> Callable[
    [RPCEndpoint, Any], RPCResponse]:
    def middleware(method: RPCEndpoint, params: Any) -> RPCResponse:
        try:
            ew3 = cast(EulithWeb3, web3)
            ew3.eulith_refresh_api_token_if_necessary()

            return make_request(method, params)
        except requests.exceptions.HTTPError as e:
            message = e.response.json().get('error', 'request failed for unknown reason')
            raise EulithRpcException(message)

    return middleware

def check_tx_receipt(tx_receipt: TxReceipt):
    if tx_receipt["status"] != ETHEREUM_STATUS_SUCCESS:
        raise EulithRpcException(f"transaction reverted ({tx_receipt['transactionHash']})")

from typing import List, Optional

from web3.types import TxParams, ChecksumAddress, TxReceipt

from eulith_web3.contract_bindings.gmx.i_position_router import IPositionRouter
from eulith_web3.contract_bindings.gmx.i_reader import IReader
from eulith_web3.contract_bindings.gmx.i_reward_router import IRewardRouter
from eulith_web3.contract_bindings.gmx.i_router import IRouter
from eulith_web3.contract_bindings.gmx.i_vault import IVault
from eulith_web3.contract_bindings.gmx.i_reward_tracker import IRewardTracker
from eulith_web3.contract_bindings.gmx.i_glp_manager import IGlpManager
from eulith_web3.erc20 import EulithERC20
from eulith_web3.eulith_web3 import EulithWeb3
from eulith_web3.exceptions import EulithRpcException


class GMXPosition:
    """
    A class that represents a GMX position.

    :param from_dict: A dictionary that contains position data from the Eulith server.
    :type from_dict: dict

    :ivar collateral_token_address: The address of the collateral token.
    :vartype collateral_token_address: Optional[str]

    :ivar index_token_address: The address of the index token.
    :vartype index_token_address: Optional[str]

    :ivar is_long: True if the position is long, False if it is short.
    :vartype is_long: Optional[bool]

    :ivar position_size_denom_usd: The size of the position in USD.
    :vartype position_size_denom_usd: Optional[float]

    :ivar collateral_size_denom_usd: The size of the collateral in USD.
    :vartype collateral_size_denom_usd: Optional[float]

    :ivar entry_price_denom_usd: The entry price of the position in USD.
    :vartype entry_price_denom_usd: Optional[float]

    :ivar realized_pnl: The realized profit and loss of the position in USD.
    :vartype realized_pnl: Optional[float]

    :ivar has_profit: True if the position has profit, False otherwise.
    :vartype has_profit: Optional[bool]

    :ivar liquidation_price_denom_usd: The liquidation price of the position in USD.
    :vartype liquidation_price_denom_usd: Optional[float]

    :ivar current_delta_denom_usd: The current delta of the position in USD.
    :vartype current_delta_denom_usd: Optional[float]
    """
    def __init__(self, from_dict: dict):
        self.collateral_token_address: Optional[str] = None
        self.index_token_address: Optional[str] = None
        self.is_long: Optional[bool] = None
        self.position_size_denom_usd: Optional[float] = None
        self.collateral_size_denom_usd: Optional[float] = None
        self.entry_price_denom_usd: Optional[float] = None
        self.realized_pnl: Optional[float] = None
        self.has_profit: Optional[bool] = None
        self.liquidation_price_denom_usd: Optional[float] = None
        self.current_delta_denom_usd: Optional[float] = None

        for key, val in from_dict.items():
            setattr(self, key, val)


class GMXClient:
    """
    A class that provides access to the GMX protocol.

    :param ew3: An instance of `EulithWeb3`.
    :type ew3: EulithWeb3

    :ivar addresses: A dictionary of GMX contract addresses.
    :vartype addresses: dict

    :ivar price_precision_decimals: The number of decimals to use for price precision.
    :vartype price_precision_decimals: int

    :ivar ew3: An instance of `EulithWeb3`.
    :vartype ew3: EulithWeb3
    """
    def __init__(self, ew3: EulithWeb3):
        self.addresses = ew3.v0.get_gmx_addresses()
        self.price_precision_decimals = 30
        self.ew3 = ew3

    def get_router(self) -> IRouter:
        """
        Gets an instance of `IRouter` that provides access to the GMX Router Contract.

        :return: An instance of `IRouter`.
        :rtype: IRouter
        """
        router_address = self.ew3.to_checksum_address(self.addresses.get('router'))
        gmx_router = IRouter(self.ew3, router_address)
        return gmx_router

    def get_vault(self) -> IVault:
        """
        Gets an instance of `IVault` that provides access to the GMX Vault Contract.

        :return: An instance of `IVault`.
        :rtype: IVault
        """
        vault_address = self.ew3.to_checksum_address(self.addresses.get('vault'))
        vault = IVault(self.ew3, vault_address)
        return vault

    def get_reader(self) -> IReader:
        """
        Gets an instance of `IReader` that provides access to the GMX Reader Contract.

        :return: An instance of `IReader`.
        :rtype: IReader
        """
        reader_address = self.ew3.to_checksum_address(self.addresses.get('reader'))
        reader = IReader(self.ew3, reader_address)
        return reader

    def get_reward_tracker(self) -> IRewardTracker:
        """
        Gets an instance of `IRewardTracker` that provides access to the GMX RewardTracker contract.

        :return: An instance of IRewardTracker.
        :rtype: IRewardTracker
        """
        reward_tracker_address = self.ew3.to_checksum_address(self.addresses.get('reward_tracker'))
        reward_tracker = IRewardTracker(self.ew3, reward_tracker_address)
        return reward_tracker

    def get_position_router(self) -> IPositionRouter:
        """
        Returns an instance of the `IPositionRouter` that provides access to the GMX PositionRouter contract.

        :return: An instance of `IPositionRouter`.
        :rtype: IPositionRouter
        """
        position_router_address = self.ew3.to_checksum_address(self.addresses.get('position_router'))
        pr = IPositionRouter(self.ew3, position_router_address)
        return pr

    def get_reward_router(self) -> IRewardRouter:
        """
        Returns an instance of the `IRewardRouter` that provides access to the GMX RewardRouter contract.

        :return: An instance of `IRewardRouter`.
        :rtype: IRewardRouter
        """
        rra = self.ew3.to_checksum_address(self.addresses.get('reward_router'))
        rr = IRewardRouter(self.ew3, rra)
        return rr

    def get_glp_manager(self) -> IGlpManager:
        """
        Returns an instance of the `IGlpManager` that provides access to the GMX GLPManager contract.

        :return: An instance of `GlpManager`
        :rtype: IGlpManager
        """
        glp_manager_address = self.ew3.to_checksum_address(self.addresses.get('glp_manager'))
        gm = IGlpManager(self.ew3, glp_manager_address)
        return gm

    def get_dollar_denominated_token_amt(self, token: EulithERC20, amount: float) -> float:
        """
        Get the dollar-denominated amount of a given token amount on GMX.

        :param token: The token to convert.
        :type token: EulithERC20
        :param amount: The amount of the token to convert.
        :type amount: float
        :return: The dollar-denominated value of the token, returned in whole float units.
        :rtype: float
        """
        vault = self.get_vault()
        full_int_amount = int(amount * 10 ** token.decimals)
        token_usd_min = vault.token_to_usd_min(token.address, full_int_amount)
        return token_usd_min / 10 ** self.price_precision_decimals

    def ensure_approved_position_router_plugin(self) -> str:
        """
        Ensures that the PositionRouter contract is an approved plugin on the router for the current wallet address.

        :return: A string representing the transaction hash of the approval transaction, if a new approval was required.
        :rtype: str
        """
        position_router_address = self.ew3.to_checksum_address(self.addresses.get('position_router'))
        gmx_router = self.get_router()

        if not gmx_router.approved_plugins(self.ew3.wallet_address, position_router_address):
            approve_plugin_tx = gmx_router.approve_plugin(
                position_router_address,
                {'from': self.ew3.wallet_address, 'gas': 5000000})
            h = self.ew3.eth.send_transaction(approve_plugin_tx)
            if not self.ew3.eulith_data.atomic:
                self.ew3.eth.wait_for_transaction_receipt(h)

            return h.hex()

    def get_max_ask_price(self, token: EulithERC20) -> float:
        """
        Get the maximum ask price for the given token in USD.

        :param token: An instance of the EulithERC20 class representing the token.
        :type token: EulithERC20
        :return: The maximum ask price in USD.
        :rtype: float
        """
        vault = self.get_vault()
        max_price = vault.get_max_price(token.address)
        return max_price / 10 ** self.price_precision_decimals

    def get_min_bid_price(self, token: EulithERC20) -> float:
        """
        Returns the minimum bid price for a given token.

        :param token: An instance of the EulithERC20 class representing the token.
        :type token: EulithERC20
        :return: The minimum bid price for the given token in USD
        :rtype: float
        """
        vault = self.get_vault()
        min_price = vault.get_min_price(token.address)
        return min_price / 10 ** self.price_precision_decimals

    def get_positions(self, wallet: ChecksumAddress, collateral_tokens: List[EulithERC20],
                      index_tokens: List[EulithERC20], is_long: List[bool]) -> List[GMXPosition]:
        """
        Returns a list of GMXPosition objects representing the positions for the specified wallet.
        The returned list matches the order of the collateral_token, index_token, and is_long tuples
        passed in their respective lists.

        :param wallet: The Ethereum wallet address to get the positions for.
        :type wallet: ChecksumAddress
        :param collateral_tokens: A list of EulithERC20 tokens that the positions are collateralized with.
        :type collateral_tokens: List[EulithERC20]
        :param index_tokens: A list of EulithERC20 tokens that the positions track.
        :type index_tokens: List[EulithERC20]
        :param is_long: A list of boolean values indicating whether the positions are long or short.
        :type is_long: List[bool]
        :return: A list of GMXPosition objects representing the positions for the specified wallet.
        :rtype: List[GMXPosition]
        :raises EulithRpcException: If there was an error fetching the positions.
        """
        status, res = self.ew3.eulith_data.get_gmx_positions(wallet, collateral_tokens, index_tokens, is_long)
        if status:
            positions = res.get('positions', [])
            return_positions = []
            for p in positions:
                return_positions.append(GMXPosition(p))

            return return_positions
        else:
            raise EulithRpcException(res)

    def mint_glp(self, pay_in: EulithERC20, pay_amount: float,
                 slippage: Optional[float] = None) -> (float, float, List[TxParams]):
        """
        Mint and stake GLP tokens for a given token and amount.

        :param pay_in: The token to pay with.
        :type pay_in: EulithERC20
        :param pay_amount: The amount of the token to pay with.
        :type pay_amount: float
        :param slippage: Optional slippage in percentage units i.e. slippage = 0.01 == 1%.
        :type slippage: Optional[float]
        :return: A tuple of minimum GLP, minimum USD value, and a list of transactions to be executed.
        :rtype: Tuple[float, float, List[TxParams]]
        :raises EulithRpcException: If there is an error in the RPC response.
        """
        status, res = self.ew3.eulith_data.request_gmx_mint_glp(pay_in, pay_amount, slippage)
        if status:
            if len(res) > 0:
                r = res[0]
                txs = r.get('txs')
                for t in txs:
                    t['from'] = self.ew3.wallet_address
                min_usd_value = r.get('min_usd_value')
                min_glp = r.get('min_glp')
                return min_glp, min_usd_value, txs
            else:
                raise EulithRpcException('mint and stake glp returned empty list response')
        else:
            raise EulithRpcException(res)

    def redeem_glp(self, receive_token: EulithERC20, glp_amount: float,
                   min_receive_token: Optional[float] = None,
                   receiving_address: Optional[ChecksumAddress] = None) -> TxParams:
        """
        Redeems GLP tokens for an equivalent value of `receive_token`.

        :param receive_token: The token to receive in exchange for GLP.
        :type receive_token: EulithERC20
        :param glp_amount: The amount of GLP tokens to redeem.
        :type glp_amount: float
        :param min_receive_token: The minimum amount of `receive_token` to receive.
        :type min_receive_token: Optional[float]
        :param receiving_address: The address to receive the `receive_token`. Defaults to the current wallet address.
        :type receiving_address: Optional[ChecksumAddress]
        :return: A dictionary containing transaction parameters.
        :rtype: TxParams
        """
        rr = self.get_reward_router()
        glp_amount_int = int(glp_amount * 10 ** 18)
        min_receive_int = int(min_receive_token * 10 ** receive_token.decimals)

        if not receiving_address:
            receiving_address = self.ew3.wallet_address

        tx = rr.unstake_and_redeem_glp(receive_token.address, glp_amount_int,
                                       min_receive_int, receiving_address,
                                       {'from': self.ew3.wallet_address, 'gas': 1500000})

        return tx

    def get_dollar_denom_glp_value(self) -> float:
        """
        Get the dollar-denominated value of one GLP.

        :return: The dollar-denominated value of one GLP.
        :rtype: float
        """
        glp_manager = self.get_glp_manager()
        price = glp_manager.get_price(False)
        return price / 10 ** self.price_precision_decimals

    def get_staked_glp_balance(self, wallet_address: ChecksumAddress) -> float:
        """
        Get the amount of staked GLP for the given wallet address.

        :param wallet_address: The wallet address to check the staked GLP balance for.
        :type wallet_address: ChecksumAddress
        :return: The amount of staked GLP for the given wallet address.
        :rtype: float
        """
        reward_tracker = self.get_reward_tracker()
        balance = reward_tracker.balance_of(wallet_address)
        return balance / 10 ** 18  # 18 magic number here is the token decimal value

    # The fee is whole units denominated in the buy_token. For example on a swap from WETH to USDC, fee = 0.04
    # means 0.04 USDC is being taken as a fee
    # Swap fees are 0.2% - 0.8% https://gmxio.gitbook.io/gmx/trading
    def swap(self, sell_token: EulithERC20, buy_token: EulithERC20, amount_in: float, slippage: float = 0.01,
             recipient: ChecksumAddress = None, approve_erc: bool = False) -> (float, float, TxParams):
        """
        Executes a swap between two tokens using the current router.

        :param sell_token: The token to sell.
        :type sell_token: EulithERC20
        :param buy_token: The token to buy.
        :type buy_token: EulithERC20
        :param amount_in: The amount of sell_token to sell in whole float units.
        :type amount_in: float
        :param slippage: The acceptable slippage for the trade, expressed as decimal percentage defaults to 0.01 == 1%
        :type slippage: float
        :param recipient: The address to send the purchased tokens to. Defaults to the calling wallet address.
        :type recipient: ChecksumAddress
        :param approve_erc: If True, do the necessary pre-requisite ERC20 approvals automatically
        :type approve_erc: bool
        :return: A tuple of the swap price, fee amount and transaction parameters.
                 The fee is whole units denominated in the buy_token
        :rtype: tuple
        """
        router = self.get_router()
        reader = self.get_reader()
        vault = self.get_vault()

        amount_in_int = int(amount_in * 10 ** sell_token.decimals)

        router_allowance = sell_token.allowance_float(self.ew3.wallet_address, router.address)

        if approve_erc and router_allowance < amount_in:
            approve_tx = sell_token.approve_float(router.address, amount_in,
                                                  {'from': self.ew3.wallet_address, 'gas': 1000000})
            h = self.ew3.eth.send_transaction(approve_tx)
            if not self.ew3.eulith_data.atomic:
                self.ew3.eth.wait_for_transaction_receipt(h)

        out_amount, fee = reader.get_amount_out(vault.address, sell_token.address, buy_token.address, amount_in_int)
        out_amount_float = out_amount / 10 ** buy_token.decimals

        min_amount_out = int((1 - slippage) * out_amount)

        if not recipient:
            recipient = self.ew3.wallet_address

        tx_params = router.swap(
            [sell_token.address, buy_token.address], amount_in_int,
            min_amount_out, recipient, {'from': self.ew3.wallet_address, 'gas': 2000000})

        price = amount_in / out_amount_float

        float_fee = fee / 10 ** buy_token.decimals

        return price, float_fee, tx_params

    def increase_position(self, position_token: EulithERC20, collateral_token: EulithERC20, true_for_long: bool,
                          collateral_amount_in: float, leverage: float = 1.0, approve_erc: bool = True) -> Optional[TxReceipt]:
        """
        Increases a GMX position.

        :param position_token: The position token to be manipulated.
        :type position_token: EulithERC20
        :param collateral_token: The token to use for collateral.
        :type collateral_token: EulithERC20
        :param true_for_long: If True, the position is a long position. Otherwise, it is a short position.
        :type true_for_long: bool
        :param collateral_amount_in: The amount of collateral to add to the position.
        :type collateral_amount_in: float
        :param leverage: The leverage to use. Default is 1.0.
        :type leverage: float
        :param approve_erc: If True, do the necessary pre-requisite ERC20 approvals automatically
        :type approve_erc: bool
        :return: If successful, returns a transaction receipt. Otherwise, returns None.
        :rtype: Optional[TxReceipt]
        """
        self.ensure_approved_position_router_plugin()

        token_usd_min = int(
            self.get_dollar_denominated_token_amt(collateral_token, collateral_amount_in)
            * 10 ** self.price_precision_decimals
            * leverage)

        full_int_amount = int(collateral_amount_in * 10 ** collateral_token.decimals)

        pr = self.get_position_router()
        fee = pr.min_execution_fee()

        increase_position_path = [collateral_token.address]
        zero_address = '0x0000000000000000000000000000000000000000'

        if true_for_long:
            acceptable_price = int(self.get_max_ask_price(position_token) * 10 ** self.price_precision_decimals)
        else:
            acceptable_price = int(self.get_min_bid_price(position_token) * 10 ** self.price_precision_decimals)

        if approve_erc:
            router_address = self.ew3.to_checksum_address(self.addresses.get('router'))
            at = collateral_token.approve_float(
                router_address,
                collateral_amount_in, {'from': self.ew3.wallet_address, 'gas': 1000000})
            h = self.ew3.eth.send_transaction(at)
            if not self.ew3.eulith_data.atomic:
                self.ew3.eth.wait_for_transaction_receipt(h)

        increase_position_tx = pr.create_increase_position(
            increase_position_path,
            position_token.address,
            full_int_amount,
            0,
            token_usd_min,
            true_for_long,
            acceptable_price,
            fee,
            b'00000000000000000000000000000000',
            zero_address,
            {'from': self.ew3.wallet_address, 'gas': 5000000, 'value': fee})

        h = self.ew3.eth.send_transaction(increase_position_tx)
        if not self.ew3.eulith_data.atomic:
            r = self.ew3.eth.wait_for_transaction_receipt(h)
            return r
        else:
            return None

    def decrease_position(self, position_token: EulithERC20, collateral_token: EulithERC20, true_for_long: bool,
                          decrease_collateral: float, decrease_exposure: float, recipient: str = None) -> Optional[TxReceipt]:
        """
        Decreases an existing position.

        :param position_token: The position token to decrease.
        :type position_token: EulithERC20
        :param collateral_token: The collateral token.
        :type collateral_token: EulithERC20
        :param true_for_long: True if the position is long, False if short.
        :type true_for_long: bool
        :param decrease_collateral: The amount of collateral to decrease.
        :type decrease_collateral: float
        :param decrease_exposure: The amount of position token to decrease.
        :type decrease_exposure: float
        :param recipient: The address to receive the returned tokens. Defaults to the wallet address.
        :type recipient: str, optional
        :return: The transaction receipt if the transaction was successful, otherwise None.
        :rtype: Optional[TxReceipt]
        """
        self.ensure_approved_position_router_plugin()

        collateral_change = int(
            self.get_dollar_denominated_token_amt(collateral_token, decrease_collateral)
            * 10 ** self.price_precision_decimals)

        size_change = int(
            self.get_dollar_denominated_token_amt(position_token, decrease_exposure)
            * 10 ** self.price_precision_decimals)

        pr = self.get_position_router()
        fee = pr.min_execution_fee()

        decrease_path = [collateral_token.address]
        zero_address = '0x0000000000000000000000000000000000000000'

        if true_for_long:
            acceptable_price = int(self.get_max_ask_price(position_token) * 10 ** self.price_precision_decimals)
        else:
            acceptable_price = int(self.get_min_bid_price(position_token) * 10 ** self.price_precision_decimals)

        if not recipient:
            recipient = self.ew3.wallet_address

        decrease_position_tx = pr.create_decrease_position(
            decrease_path,
            position_token.address,
            collateral_change,
            size_change,
            true_for_long,
            recipient,
            acceptable_price,
            0,
            fee,
            False,
            zero_address,
            {'from': self.ew3.wallet_address, 'gas': 5000000, 'value': fee})

        h = self.ew3.eth.send_transaction(decrease_position_tx)
        if not self.ew3.eulith_data.atomic:
            r = self.ew3.eth.wait_for_transaction_receipt(h)
            return r
        else:
            return None

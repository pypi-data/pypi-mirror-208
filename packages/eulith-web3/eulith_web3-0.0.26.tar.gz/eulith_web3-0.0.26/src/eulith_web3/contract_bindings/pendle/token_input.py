from typing import List, TypedDict
from eulith_web3.contract_bindings.pendle.swap_data import SwapData


class TokenInput(TypedDict):
    token_in: str
    net_token_in: int
    token_mint_sy: str
    bulk: str
    pendle_swap: str
    swap_data: SwapData

from typing import List, TypedDict
from eulith_web3.contract_bindings.pendle.swap_data import SwapData


class TokenOutput(TypedDict):
    token_out: str
    min_token_out: int
    token_redeem_sy: str
    bulk: str
    pendle_swap: str
    swap_data: SwapData

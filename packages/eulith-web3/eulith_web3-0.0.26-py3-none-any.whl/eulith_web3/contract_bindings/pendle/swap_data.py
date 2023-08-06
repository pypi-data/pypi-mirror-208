from typing import List, TypedDict


class SwapData(TypedDict):
    swap_type: int
    ext_router: str
    ext_calldata: bytes
    need_scale: bool

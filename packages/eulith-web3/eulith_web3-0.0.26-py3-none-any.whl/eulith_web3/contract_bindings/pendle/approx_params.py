from typing import List, TypedDict


class ApproxParams(TypedDict):
    guess_min: int
    guess_max: int
    guess_offchain: int
    max_iteration: int
    eps: int

from typing import List, TypedDict


class MultiApproval(TypedDict):
    tokens: List[str]
    spender: str

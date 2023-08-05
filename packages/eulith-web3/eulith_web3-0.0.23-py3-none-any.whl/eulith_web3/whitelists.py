from typing import List, TypedDict


class ClientWhitelist(TypedDict):
    list_id: int
    sorted_addresses: List[str]
    is_draft: bool


class ClientWhitelistHashInput(TypedDict):
    owner_address: str
    safe_address: str
    list_contents: List[str]
    sub: str
    network_id: int


class ClientWhitelistHash(TypedDict):
    hash_input: ClientWhitelistHashInput
    hash: str


def get_client_whitelist_typed_data(message: ClientWhitelistHashInput) -> dict:
    types = {
        "EIP712Domain": [
            {"name": "name", "type": "string"},
            {"name": "version", "type": "string"},
        ],
        "ClientWhitelistHashInput": [
            {"name": "ownerAddress", "type": "string"},
            {"name": "safeAddress", "type": "string"},
            {"name": "listContents", "type": "string[]"},
            {"name": "sub", "type": "string"},
            {"name": "networkId", "type": "int32"},
        ],
    }

    payload = {
        "types": types,
        "primaryType": "ClientWhitelistHashInput",
        "domain": {"name": "Eulith", "version": "1"},
        "message": {
            "ownerAddress": message["owner_address"],
            "safeAddress": message["safe_address"],
            "listContents": message["list_contents"],
            "sub": message["sub"],
            "networkId": message["network_id"],
        },
    }

    return payload

from typing import Optional

from eth_keys.datatypes import Signature
from web3.types import TxParams


class Signer:
    def address(self) -> str:
        pass

    def sign_msg_hash(self, message_hash: bytes) -> Signature:
        pass

    def sign_transaction(self, tx: TxParams, message_hash: bytes) -> Signature:
        return self.sign_msg_hash(message_hash)

    def sign_typed_data(self, eip712_data: dict, message_hash: bytes) -> Signature:
        return self.sign_msg_hash(message_hash)

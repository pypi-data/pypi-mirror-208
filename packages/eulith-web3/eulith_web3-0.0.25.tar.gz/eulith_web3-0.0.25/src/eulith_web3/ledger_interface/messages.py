"""
MIT License

Copyright (c) 2019 Mike Shultz

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import binascii
import struct
from typing import Optional, Union

from eth_account.messages import encode_structured_data

from eulith_web3.ledger_interface.comms import Dongle, dongle_send_data, init_dongle
from eulith_web3.ledger_interface.constants import DATA_CHUNK_SIZE, DEFAULT_PATH_STRING
from eulith_web3.ledger_interface.objects import SignedMessage, SignedTypedMessage
from eulith_web3.ledger_interface.utils import (
    chunks,
    is_bip32_path,
    parse_bip32_path,
)

AnyText = Union[str, bytes]


def sign_message(
    message: AnyText,
    sender_path: str = DEFAULT_PATH_STRING,
    dongle: Optional[Dongle] = None,
) -> SignedMessage:
    """Sign a simple text message.  Message will be prefixed by the Ethereum
    app on the Ledger device according to `EIP-191`_.

    :param message: (:code:`str|bytes`) - A bit of text to sign
    :param sender_path: (:code:`str`) - HID derivation path for the account to
        sign with.
    :param dongle: (:class:`ledgerblue.Dongle.Dongle`) - The Web3 instance to use
    :return: :class:`ledgereth.objects.SignedMessage`

    .. _`EIP-191`: https://eips.ethereum.org/EIPS/eip-191
    """
    given_dongle = dongle is not None
    dongle = init_dongle(dongle)
    retval = None

    if type(message) == str:
        message = message.encode("utf-8")

    # Silence mypy due to type cohersion above
    assert type(message) == bytes

    encoded = struct.pack(">I", len(message))
    encoded += message

    if not is_bip32_path(sender_path):
        raise ValueError("Invalid sender BIP32 path given to sign_transaction")

    path = parse_bip32_path(sender_path)
    payload = (len(path) // 4).to_bytes(1, "big") + path + encoded

    chunk_count = 0
    for chunk in chunks(payload, DATA_CHUNK_SIZE):
        chunk_size = len(chunk)

        if chunk_count == 0:
            retval = dongle_send_data(
                dongle,
                "SIGN_MESSAGE_FIRST_DATA",
                chunk,
                Lc=chunk_size.to_bytes(1, "big"),
            )
        else:
            retval = dongle_send_data(
                dongle,
                "SIGN_MESSAGE_SECONDARY_DATA",
                chunk,
                Lc=chunk_size.to_bytes(1, "big"),
            )
        chunk_count += 1

    if retval is None or len(retval) < 64:
        raise Exception("Invalid response from Ledger")

    v = int(retval[0])
    r = int(binascii.hexlify(retval[1:33]), 16)
    s = int(binascii.hexlify(retval[33:65]), 16)

    signed = SignedMessage(message, v, r, s)

    # If this func inited the dongle, then close it, otherwise core dump
    if not given_dongle:
        dongle.close()

    return signed


def ledger_sign_typed_data(
    eip712_dict: dict,
    sender_path: str = DEFAULT_PATH_STRING,
    dongle: Optional[Dongle] = None,
) -> SignedTypedMessage:
    signable = encode_structured_data(eip712_dict)
    domain_hash = signable.header
    message_hash = signable.body

    given_dongle = dongle is not None
    dongle = init_dongle(dongle)

    if type(domain_hash) == str:
        domain_hash = domain_hash.encode("utf-8")
    if type(message_hash) == str:
        message_hash = message_hash.encode("utf-8")

    # Silence mypy due to type cohersion above
    assert type(domain_hash) == bytes
    assert type(message_hash) == bytes

    encoded = domain_hash + message_hash

    if not is_bip32_path(sender_path):
        raise ValueError("Invalid sender BIP32 path given to sign_transaction")

    path = parse_bip32_path(sender_path)
    payload = (len(path) // 4).to_bytes(1, "big") + path + encoded

    retval = dongle_send_data(
        dongle,
        "SIGN_TYPED_DATA",
        payload,
        Lc=len(payload).to_bytes(1, "big"),
    )

    if retval is None or len(retval) < 64:
        raise Exception("Invalid response from Ledger")

    v = int(retval[0])
    r = int(binascii.hexlify(retval[1:33]), 16)
    s = int(binascii.hexlify(retval[33:65]), 16)

    signed = SignedTypedMessage(domain_hash, message_hash, v, r, s)

    # If this func inited the dongle, then close it, otherwise core dump
    if not given_dongle:
        dongle.close()

    return signed

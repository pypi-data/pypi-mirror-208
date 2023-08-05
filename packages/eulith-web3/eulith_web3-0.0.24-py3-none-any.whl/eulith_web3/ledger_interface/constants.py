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

import os
from typing import Any, Dict, Type

from eth_utils import remove_0x_prefix


def getenvint(key, default=0):
    """Get an int from en env var or use default"""
    try:
        return int(os.environ.get("MAX_ACCOUNTS_FETCH"))
    except TypeError:
        return default


# Chain ID to use if not given by user
DEFAULT_CHAIN_ID = 1

# Default accounts to fetch with get_accounts
DEFAULT_ACCOUNTS_FETCH = 3

# Number of accounts to fetch when looking up an account by address
MAX_ACCOUNTS_FETCH = getenvint("MAX_ACCOUNTS_FETCH", 5)

# Whether to use the legacy bip32 path derivation used by Ledger Chrome app
LEGACY_ACCOUNTS = os.getenv("LEDGER_LEGACY_ACCOUNTS") is not None

DEFAULT_PATH_STRING = "44'/60'/0'/0/0"
DEFAULT_PATH_ENCODED = (
    b"\x80\x00\x00,\x80\x00\x00<\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
)
if LEGACY_ACCOUNTS:
    DEFAULT_PATH_STRING = "44'/60'/0'/0"
    DEFAULT_PATH_ENCODED = b"\x80\x00\x00,\x80\x00\x00<\x80\x00\x00\x00\x00\x00\x00\x00"
DEFAULT_PATH = remove_0x_prefix(DEFAULT_PATH_ENCODED.hex())
VRS_RETURN_LENGTH = int(65).to_bytes(1, "big")

# Data size expected from Ledger
DATA_CHUNK_SIZE = 255

# Default "zero" values in EVM/Solidity
DEFAULTS: Dict[Type, Any] = {
    int: 0,
    bytes: b"",
}

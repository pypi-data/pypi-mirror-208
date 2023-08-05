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

from enum import IntEnum

from ledgerblue.commException import CommException


class LedgerErrorCodes(IntEnum):
    OK = 0x9000

    ##
    # User/input errors
    ##

    TX_TYPE_UNSUPPORTED = 0x6501
    INCORRECT_LENGTH = 0x6700
    # This may happen if first/secondary data is invalid or out of order or
    # unexpected p1/p2 values
    INVALID_TX_CHUNKS = 0x6B00
    # This can also mean ADPU empty, apparently
    CANCELED_BY_USER = 0x6982
    APDU_SIZE_MISMATCH = 0x6983
    # Invalid data, transaction, or HD path, and a bit of a catch-all
    INVALID_DATA = 0x6A80
    APP_SLEEP = 0x6804
    APP_NOT_STARTED = 0x6D00
    DEVICE_LOCKED = 0x6B0C
    # "Plugins" allow resolution of function selectors and args for various
    # smart contracts.  Ref: https://blog.ledger.com/ethereum-plugins/
    PLUGIN_NOT_PRESENT = 0x6984

    ##
    # Internal errors
    ##

    INT_CONVERSION_ERROR = 0x6504
    OUTPUT_BUFFER_TOO_SMALL = 0x6502
    PLUGIN_ERROR = 0x6503
    # "Signsture/parser not initialized" in source
    DECLINED = 0x6985

    ##
    # Inferred errors found through discovery
    ##

    # ledgerblue default code
    UKNOWN = 0x6F00
    APP_NOT_FOUND = 0x6D02

    @classmethod
    def get_by_value(cls, val):
        try:
            return cls(val)
        except ValueError:
            return None


class LedgerError(Exception):
    message = "Unexpected Ledger error"

    def __init__(self, message=None):
        super().__init__(message or self.message)

    @classmethod
    def transalate_comm_exception(cls, exp: CommException):
        return ERROR_CODE_EXCEPTIONS.get(
            exp.sw,
            LedgerError(
                f"Unexpected error: {hex(exp.sw)} {LedgerErrorCodes.get_by_value(exp.sw) or 'UNKNOWN'}"
            ),
        )


class LedgerNotFound(LedgerError):
    message = "Unable to find Ledger device"


class LedgerLocked(LedgerError):
    message = "Ledger appears to be locked"


class LedgerAppNotOpened(LedgerError):
    message = "Expected Ledger Ethereum app not open"


class LedgerCancel(LedgerError):
    message = "Action cancelled by the user"


class LedgerInvalidADPU(LedgerError):
    message = "Internal error.  Invalid data unit sent to ledger_interface."


class LedgerInvalid(LedgerError):
    message = 'Invalid data sent to ledger_interface or "blind signing" is not enabled'


ERROR_CODE_EXCEPTIONS = {
    LedgerErrorCodes.UKNOWN: LedgerNotFound,
    LedgerErrorCodes.DEVICE_LOCKED: LedgerLocked,
    LedgerErrorCodes.APP_SLEEP: LedgerAppNotOpened,
    LedgerErrorCodes.APP_NOT_STARTED: LedgerAppNotOpened,
    LedgerErrorCodes.APP_NOT_FOUND: LedgerAppNotOpened,
    LedgerErrorCodes.CANCELED_BY_USER: LedgerCancel,
    LedgerErrorCodes.APDU_SIZE_MISMATCH: LedgerInvalidADPU,
    LedgerErrorCodes.DECLINED: LedgerCancel,
    LedgerErrorCodes.INVALID_DATA: LedgerInvalid,
}

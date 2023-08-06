from eulith_web3.erc20 import TokenSymbol
from eulith_web3.eulith_web3 import EulithWeb3
from eulith_web3.exceptions import EulithUnsafeRequestException
from eulith_web3.gmx import GMXClient
from eulith_web3.signing import LocalSigner, construct_signing_middleware


def test_unsafe_tx_error_increase_order():
    acct = LocalSigner("0x4d5db4107d237df6a3d58ee5f70ae63d73d7658d4026f2eefd2f204c81682cb7")
    ew3 = EulithWeb3(eulith_url="http://localhost:7777/v0",
                     eulith_refresh_token="eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NksifQ."
                                          "eyJzdWIiOiJsaWJ0ZXN0IiwiZXhwIjoxODQ0Njc"
                                          "0NDA3MzcwOTU1MTYxNSwic291cmNlX2hhc2giOiI"
                                          "qIiwic2NvcGUiOiJBUElSZWZyZXNoIn0.G87Tv9Lw"
                                          "LH8SRgjlVKIAPk1pdavVS0xwz3fuB7lxP0Et-pPM7o"
                                          "jQkjC1zlC7zWYUdh9p3GvwX_ROfgSPJsw-Qhw",
                     signing_middle_ware=construct_signing_middleware(acct))

    gc = GMXClient(ew3)

    weth = ew3.v0.get_erc_token(TokenSymbol.WETH)

    ew3.v0.start_atomic_transaction(acct.address)
    try:
        gc.create_increase_order(weth, weth, True, 10.0, 10.0, 1000)
        assert False
    except EulithUnsafeRequestException as e:
        assert True
    except:
        assert False

    try:
        gc.create_decrease_order(weth, weth, 10.0, 10.0, True, 1000)
        assert False
    except EulithUnsafeRequestException as e:
        assert True
    except:
        assert False

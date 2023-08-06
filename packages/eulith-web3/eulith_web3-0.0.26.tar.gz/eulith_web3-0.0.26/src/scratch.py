from eulith_web3.erc20 import TokenSymbol
from eulith_web3.eulith_web3 import EulithWeb3
from eulith_web3.gmx import GMXClient
from eulith_web3.ledger import LedgerSigner
from eulith_web3.signing import construct_signing_middleware, LocalSigner

DEVRPC = 'http://localhost:7777/v0'
MAIN = 'https://arb-main.eulithrpc.com/v0'
REFRESH_MAIN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NksifQ.eyJzdWIiOiJsdWNhcyIsImV4cCI6MTcxNTYzMjE5OCwic291cmNlX2hhc2giOiIqIiwic2NvcGUiOiJBUElSZWZyZXNoIn0.NZf5MJzTsNvsBjQ4674yzwGwTyttoefOinBfaqxhJKku0s5jFT3dCpozsMGPNwUFWhfx5OiXNLDhrPM640_2Cxs'
REFRESH_DEV = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NksifQ.eyJzdWIiOiJsaWJ0ZXN0IiwiZXhwIjoxODQ0Njc0NDA3MzcwOTU1MTYxNSwic291cmNlX2hhc2giOiIqIiwic2NvcGUiOiJBUElSZWZyZXNoIn0.G87Tv9LwLH8SRgjlVKIAPk1pdavVS0xwz3fuB7lxP0Et-pPM7ojQkjC1zlC7zWYUdh9p3GvwX_ROfgSPJsw-Qhw'

if __name__ == '__main__':
    wallet = LocalSigner('4d5db4107d237df6a3d58ee5f70ae63d73d7658d4026f2eefd2f204c81682cb7')

    ew3 = EulithWeb3(eulith_url=DEVRPC,
                     eulith_refresh_token=REFRESH_DEV,
                     signing_middle_ware=construct_signing_middleware(wallet))

    gc = GMXClient(ew3)

    weth = ew3.v0.get_erc_token(TokenSymbol.WETH)

    # p = gc.get_positions(ew3.to_checksum_address(wallet.address), [weth], [weth], [True])
    # wbtc_exposure = p[0].position_size_denom_usd
    # collateral_amt = p[0].collateral_size_denom_usd
    #
    # print(round(wbtc_exposure, 20))
    # print(collateral_amt)

    ih = gc.create_increase_order(weth, weth, True, 0.02, 30, 1500, True)
    print(ih.get('transactionHash').hex())

    h = gc.create_decrease_order(weth, weth, 50, 35, True, 2000)
    print(h.get('transactionHash').hex())

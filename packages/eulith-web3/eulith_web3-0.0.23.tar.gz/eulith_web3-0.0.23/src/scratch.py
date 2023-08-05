import time

import boto3

from eulith_web3.contract_bindings.pendle.i_p_market import IPMarket
from eulith_web3.contract_bindings.safe.i_safe import ISafe
from eulith_web3.erc20 import TokenSymbol, EulithERC20
from eulith_web3.eulith_web3 import EulithWeb3
from eulith_web3.kms import KmsSigner
from eulith_web3.ledger_interface.account import get_ledger_accounts
from eulith_web3.pendle import PendleClient, PendleMarketSymbol
from eulith_web3.signing import construct_signing_middleware, LocalSigner
from eulith_web3.swap import EulithSwapRequest
from eulith_web3.ledger import LedgerSigner

DEVRPC = 'http://localhost:7777/v0'
MAIN = 'https://arb-main.eulithrpc.com/v0'
REFRESH = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NksifQ.eyJzdWIiOiJldWxpdGhhZG1pbiIsImV4cCI6MTcxNTI5NjYxMCwic291cmNlX2hhc2giOiIqIiwic2NvcGUiOiJBUElSZWZyZXNoIn0.GtOBb96h2CH_Q2vs6it6HbWbmB4QfExoUdVHts8QCMJrthd8a2vkYfjvVNdcksitBAimn1sPJillzvUHt0thKxw'

if __name__ == '__main__':
    # wallet = LedgerSigner()
    # wallet = LocalSigner("0x4d5db4107d237df6a3d58ee5f70ae63d73d7658d4026f2eefd2f204c81682cb7")

    aws_credentials_profile_name = 'default'

    key_name = 'LUCAS_TEST_KEY'
    formatted_key_name = f'alias/{key_name}'

    session = boto3.Session(profile_name=aws_credentials_profile_name)
    client = session.client('kms')

    wallet = KmsSigner(client, formatted_key_name)

    ew3 = EulithWeb3(eulith_url=MAIN,
                     eulith_refresh_token=REFRESH,
                     signing_middle_ware=construct_signing_middleware(wallet))

    weth = ew3.v0.get_erc_token(TokenSymbol.WETH)
    dt = weth.deposit_eth(0.00001, {
        'gas': 2000000,
        'from': wallet.address
    })
    h = ew3.eth.send_transaction(dt)
    ew3.eth.wait_for_transaction_receipt(h)
    print(h.hex())

    # authorized_address = ew3.to_checksum_address(wallet.address)
    #
    # owner_keys = [
    #     '59d060b1d6ae7c494a2c911c200429e02bfb4714d948c684261b696ed7077833',
    #     'a39004547e27a0314969c82662733328fd7ce36b373460687a205a69fbb8b699',
    #     'd81ea7876bd225b70410448225e4121fbeacb2bbc13b49c00396b622e9fb06a1',
    #     'cf9ac1ec7666006d91173960ede131cc01f1a11eccdfa1ab593385da04878721',
    #     '2f2073f613ff2651f2114e26e8cca6e49a73b719dd728c6915eeb0c20534c32e',
    #     '1e780eaf6fed0ce7aca07418d97df74d5a004e394851b127b8c701b725e8400d'
    # ]
    #
    # aa, sa = ew3.v0.deploy_new_armor(authorized_address, {
    #     'from': authorized_address,
    #     'gas': 2500000
    # })
    #
    # time.sleep(3)
    #
    # status = ew3.v0.submit_enable_module_signature(authorized_address, wallet)

    # status = ew3.v0.enable_armor(threshold, owner_addresses, {
    #     'gas': 500000,
    #     'from': wallet.address
    # })
    #
    # assert status
    #
    # safe = ISafe(ew3, ew3.to_checksum_address(sa))
    #
    # is_module_enabled = safe.is_module_enabled(ew3.to_checksum_address(aa))
    # assert is_module_enabled
    #
    # read_owners = safe.get_owners()
    # assert len(read_owners) == len(owner_keys)
    #
    # read_threshold = safe.get_threshold()
    # assert read_threshold == threshold

    # key_name = 'LUCAS_TEST_KEY'
    # formatted_key_name = f'alias/{key_name}'
    #
    # session = boto3.Session(profile_name='default')
    # client = session.client('kms')
    #
    # wallet = KmsSigner(client, formatted_key_name)
    # print(wallet.address)
    #
    # ew3 = EulithWeb3(eulith_url=ARBMAIN,
    #                  eulith_refresh_token="eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NksifQ.eyJzdWIiOiJsdWNhcyIsImV4cCI6MTcxNTAyMTE0Miwic291cmNlX2hhc2giOiIqIiwic2NvcGUiOiJBUElSZWZyZXNoIn0.0JBiTFCz6CAXeGrVQ9SZimLBlLyugbS8I4NdyRiBryp72bGhORGvJ0bMJBKGt3WMtATOhixNeDxCjc6c26llpBw",
    #                  signing_middle_ware=construct_signing_middleware(wallet))
    #
    # weth = ew3.v0.get_erc_token(TokenSymbol.WETH)
    # usdc = ew3.v0.get_erc_token(TokenSymbol.USDC)
    #
    # market = ew3.to_checksum_address('0x9eC4c502D989F04FfA9312C9D6E3F872EC91A0F9')
    #
    # pc = PendleClient(ew3)
    # q = pc.quote_pt(1, market)
    #
    # print(q.price_denom_underlying * q.sy_underlying_exchange_rage)
    # print(q.implied_yield)
    # swap_amt = 1
    #
    # at = usdc.approve_float(pc.router, swap_amt, {
    #     'gas': 10000000,
    #     'from': wallet.address
    # })
    # h = ew3.eth.send_transaction(at)
    # ew3.eth.wait_for_transaction_receipt(h)
    #
    # status, tx_hash = pc.swap(TokenSymbol.USDC, PendleMarketSymbol.PrincipleToken,
    #                           swap_amt, 0.01, market,
    #                           ew3.to_checksum_address(wallet.address),
    #                           {
    #                             'gas': 100000000,
    #                             'from': wallet.address
    #                           })
    #
    # print(status)
    # print(tx_hash)
    #
    # market_contract = IPMarket(ew3, market)
    #
    # # (SY, PT, YT)
    # market_tokens = market_contract.read_tokens()
    #
    # pt_erc = EulithERC20(ew3, market_tokens[1])
    # pt_balance = pt_erc.balance_of_float(wallet.address)
    #
    # print(pt_balance)

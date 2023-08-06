from xrpl import CryptoAlgorithm
from xrpl.account import does_account_exist
from xrpl.clients import JsonRpcClient, WebsocketClient
from xrpl.ledger import get_fee
from xrpl.wallet import Wallet

from features.exceptions.UnconfiguredEnvironmentException import UnconfiguredEnvironmentException
from features.lib.Helpers import read_env_var
from features.steps import constants
from features.steps.common import send_payment


def before_all(context):
    context.connectionType = read_env_var('CONNECTION_TYPE')
    connectionScheme = read_env_var('CONNECTION_SCHEME')
    connectionURL = read_env_var('CONNECTION_URL')
    context.url = "{}://{}".format(connectionScheme, connectionURL)
    context.client = get_client(context)
    context.crypto_algorithm = CryptoAlgorithm.SECP256K1
    context.test_genesis_wallet = get_test_genesis_wallet(context)
    context.default_fee = int(get_fee(context.client))


def get_test_genesis_wallet(context):
    test_genesis_account_id = "rh1HPuRVsYYvThxG2Bs1MfjmrVC73S16Fb"
    test_genesis_account_seed = "snRzwEoNTReyuvz6Fb1CDXcaJUQdp"
    test_genesis_wallet = Wallet(seed=test_genesis_account_seed, sequence=0, algorithm=context.crypto_algorithm)
    if is_network_local(context):
        if not does_account_exist(test_genesis_account_id, context.client):
            master_account_seed = "snoPBrXtMeMyMHUVTgbuqAfg1SUTb"
            master_genesis_wallet = Wallet(seed=master_account_seed, sequence=0, algorithm=context.crypto_algorithm)
            send_payment(context, source_wallet=master_genesis_wallet, destination_wallet=test_genesis_wallet,
                         amount=constants.DEFAULT_TEST_GENESIS_ACCOUNT_FUND)
    else:
        if not does_account_exist(test_genesis_account_id, context.client):
            raise UnconfiguredEnvironmentException(
                "Genesis account is not created. Please create and fund the account first.")

    return test_genesis_wallet


def is_network_local(context):
    return "127.0.0" in context.url or "localhost" in context.url


def before_scenario(context, scenario):
    context.minDrop = context.default_fee
    context.transferAmount = "10000"
    context.exception = None
    context.test_status = None
    context.sourceAccountUsername = ""
    context.sourceWallet = None
    context.sourceAddress = ""
    context.sourceBalance = 0
    context.destinationAccountUsername = ""
    context.destinationWallet = None
    context.destinationAddress = ""
    context.destinationBalance = 0


def after_all(context):
    if context.connectionType == "websocket":
        context.client.close()


def get_client(context):
    if context.connectionType == "jsonrpc":
        client = JsonRpcClient(context.url)
    elif context.connectionType == "websocket":
        client = WebsocketClient(context.url)
        client.open()
    else:
        raise UnconfiguredEnvironmentException("Unsupported CONNECTION_TYPE='{}'".format(context.connectionType))
    return client

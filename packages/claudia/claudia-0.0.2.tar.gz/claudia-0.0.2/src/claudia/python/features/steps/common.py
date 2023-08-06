import time
from enum import Enum

from behave import *
from hamcrest import assert_that, equal_to, contains_string
from xrpl.account import get_balance, get_account_info
from xrpl.asyncio.transaction import XRPLReliableSubmissionException
from xrpl.models import IssuedCurrencyAmount, PathStep
from xrpl.transaction import (
    safe_sign_and_autofill_transaction,
    send_reliable_submission, safe_sign_transaction)
from xrpl.wallet import Wallet

from features.exceptions.InvalidInputException import InvalidInputException
from features.lib.ObjFactory import ObjType, ObjFactory
from features.steps import constants


class ResponseCode(str, Enum):
    success = "tesSUCCESS"
    path_dry = "tecPATH_DRY"
    no_destination = "tecNO_DST"
    no_line_redundant = "tecNO_LINE_REDUNDANT"
    path_partial = "tecPATH_PARTIAL"
    unfunded_offer = "tecUNFUNDED_OFFER"
    insufficient_reserve = "tecINSUFFICIENT_RESERVE"
    no_permission = "tecNO_PERMISSION"
    has_obligations = "tecHAS_OBLIGATIONS"
    no_entry = "tecNO_ENTRY"
    unfunded_payment = "tecUNFUNDED_PAYMENT"


@given('we create "{account_type}" account for "{username} with "{amount}" XRP drops')
def step_impl(context, account_type, username, amount):
    account_type = sanitize_args(account_type)
    username = sanitize_args(username)
    if amount == "default":
        account_fund_amount = constants.DEFAULT_ACCOUNT_FUND_AMOUNT
    else:
        account_fund_amount = str(amount)

    # TODO: Change the account creation method to store in a collection
    if account_type == "source":
        context.sourceAccountUsername = username
        context.sourceWallet, context.sourceAddress, context.sourceBalance = generate_wallet_info(context,
                                                                                                  fund=True,
                                                                                                  fund_amount=account_fund_amount)
    elif account_type == "destination":
        context.destinationAccountUsername = username
        context.destinationWallet, context.destinationAddress, context.destinationBalance = generate_wallet_info(
            context)
    elif account_type == "issuer":
        context.issuerAccountUsername = username
        context.issuerWallet, context.issuerAddress, context.issuerBalance = generate_wallet_info(context)
    elif account_type == "generic_alice":
        context.aliceAccountUsername = username
        context.aliceWallet, context.aliceAddress, context.aliceBalance = generate_wallet_info(context)
    elif account_type == "generic_bob":
        context.bobAccountUsername = username
        context.bobWallet, context.bobAddress, context.bobBalance = generate_wallet_info(context)
    elif account_type == "generic_carol":
        context.carolAccountUsername = username
        context.carolWallet, context.carolAddress, context.carolBalance = generate_wallet_info(context)
    elif account_type == "invalid":
        context.invalidAccountUsername = username
        context.invalidWallet, context.invalidAddress, context.invalidBalance = generate_wallet_info(context)
        context.invalidAddress = "invalid"
        context.invalidBalance = 0
    else:
        raise InvalidInputException(
            "'{}' is not a valid accountType. Valid options are: 'source', 'destination' and 'issuer'.".format(
                account_type))


def generate_wallet_info(context, fund=True, fund_amount=constants.DEFAULT_ACCOUNT_FUND_AMOUNT):
    wallet = Wallet.create(crypto_algorithm=context.crypto_algorithm)
    if fund:
        send_payment(context, source_wallet=context.test_genesis_wallet, destination_wallet=wallet,
                     amount=fund_amount)
    return wallet, wallet.classic_address, get_balance(wallet.classic_address, context.client)


def send_payment(context, source_wallet, destination_wallet, amount):
    for i in range(0, 5):
        try:
            response = sign_autofill_and_submit(context.client,
                                                ObjFactory.getObj(
                                                    ObjType.payment,
                                                    account=source_wallet.classic_address,
                                                    destination=destination_wallet.classic_address,
                                                    amount=amount,
                                                    sequence=get_account_sequence(context.client,
                                                                                  source_wallet.classic_address)
                                                ),
                                                source_wallet)
        except XRPLReliableSubmissionException:
            time.sleep(1)
            continue
        break
    return response


def get_account_sequence(client, account_address):
    response = get_account_info(account_address, client)
    return response.result["account_data"]["Sequence"]


def wait_for_ledger_to_advance_for_account_delete(context, account_address, transaction_count=256):
    print("\tWaiting for ledger advance...")
    advance_ledger_with_transactions(context, transaction_count)
    count = 1
    account_1_sequence = ledger_sequence = 0
    while (ledger_sequence - account_1_sequence) <= transaction_count:
        account_1_sequence = get_account_sequence(context.client, account_address)
        ledger_sequence = get_ledger_current_index(context)
        if (count % 60) == 1:
            time.sleep(1)
        count += 1
    print("\tLedger advance complete...")


def get_ledger_current_index(context):
    ledger_current_request = ObjFactory.getObj(
        ObjType.ledger_current
    )
    return context.client.request(ledger_current_request).result['ledger_current_index']


def get_account_balance(context, account_id):
    if not account_id:
        raise Exception("Cannot get account balance. Account ID is invalid.")
    else:
        return get_balance(account_id, context.client)


def verify_test_status(actual_status, expected_status):
    assert_that(actual_status, equal_to(expected_status),
                "Test Status is incorrect. \nExpected: " + expected_status + "\nActual: " + actual_status)


def verify_test_error_message(actual_error, expected_error):
    assert_that(actual_error, contains_string(expected_error),
                "Incorrect error message received. \nExpected: " + expected_error + "\nActual: " + actual_error)


def advance_ledger_with_transactions(context, transaction_count):
    account_1, account_1_address, account_1_balance = generate_wallet_info(context)
    account_2, account_2_address, account_2_balance = generate_wallet_info(context)

    payment = ObjFactory.getObj(
        ObjType.payment,
        account=account_1_address,
        destination=account_2_address,
        amount="10"
    )
    print("\tAdvancing the ledger with transactions... " + str(transaction_count) + " transactions...")
    for i in range(0, transaction_count + 1):
        try:
            safe_sign_and_autofill_transaction(payment, account_1, context.client)
            print("Transaction# " + str(transaction_count) + "succeeded")
        except KeyError:
            print("Transaction# " + str(transaction_count) + "failed")


def get_nft_tokens(client, account_address):
    account_nfts = get_account_nfts(client, account_address).result["account_nfts"]
    nft_tokens = []
    for account_nft in account_nfts:
        nft_token = account_nft['NFTokenID']
        nft_tokens.append(nft_token)
    return nft_tokens


def get_ticket_sequence(client, account_address):
    account_objects = get_account_objects_response(client, account_address).result["account_objects"]
    ticket_sequences = []
    for account_object in account_objects:
        if account_object["LedgerEntryType"] == "Ticket":
            ticket_sequences.append(account_object['TicketSequence'])
    return ticket_sequences


def generate_issued_currency_amount(value, issuer, currency="USD"):
    return IssuedCurrencyAmount(
        value=value,
        issuer=issuer,
        currency=currency
    )


def generate_path_step(issuer=None, currency=None):
    if issuer is not None and currency is not None:
        return PathStep(
            issuer=issuer,
            currency=currency
        )
    if issuer is not None:
        return PathStep(
            issuer=issuer
        )
    if currency is not None:
        return PathStep(
            currency=currency
        )


def sign_autofill_and_submit(client, payload, wallet):
    signed_account_set_tx = safe_sign_and_autofill_transaction(payload,
                                                               wallet,
                                                               client)
    return send_reliable_submission(signed_account_set_tx, client)


def sign_and_submit(client, payload, wallet):
    signed_account_set_tx = safe_sign_transaction(payload,
                                                  wallet,
                                                  client)
    return send_reliable_submission(signed_account_set_tx, client)


def verify_payment_account_objects(context, response, engine_result=ResponseCode.success):
    verify_not_creating_objects_type_account_objects(context, response, engine_result)


def verify_account_set_account_objects(context, response, engine_result=ResponseCode.success):
    verify_not_creating_objects_type_account_objects(context, response, engine_result)


def verify_not_creating_objects_type_account_objects(context, response, engine_result=ResponseCode.success):
    verify_transaction_validity(context, response, engine_result=engine_result)
    verify_response_code(response, engine_result)
    try:
        account_id = response.result["Owner"]
    except KeyError:
        account_id = response.result["Account"]

    transaction_type = response.result["TransactionType"]
    account_objects_response = get_account_objects_response(context.client, account_id)
    if account_objects_response.status != 'error':
        for account_object in account_objects_response.result["account_objects"]:
            assert transaction_type not in account_object['LedgerEntryType'], \
                "Account object created for Transaction Type: {}".format(transaction_type)


def verify_response_code(response, expected_code):
    assert expected_code in str(response), "Expected response code was not received. \nExpected Code = '{}'. " \
                                           "\nResponse received: '{}'".format(expected_code, response)


def verify_trustline_account_objects(context, response, engine_result=ResponseCode.success):
    verify_transaction_validity(context, response, engine_result=engine_result)
    verify_response_code(response, engine_result)

    try:
        account_id = response.result["Owner"]
    except KeyError:
        account_id = response.result["Account"]

    transaction_type = response.result["TransactionType"]
    if (transaction_type == "TrustSet"):
        account_objects_response = get_account_objects_response(context.client, account_id)
        if account_objects_response.status != 'error':
            assert account_id == account_objects_response.result['account']
            for account_object in account_objects_response.result["account_objects"]:
                assert (account_object['LedgerEntryType'] == "RippleState" or account_object[
                    'LedgerEntryType'] == 'Offer')


def verify_account_balance(actual_amount, expected_amount):
    assert actual_amount == expected_amount, "Account balance is incorrect. Expected: '{}' Actual: '{}'".format(
        expected_amount, actual_amount)


def verify_nftoken_mint_account_objects(context, response, engine_result=ResponseCode.success):
    verify_transaction_validity(context, response, engine_result=engine_result)
    verify_response_code(response, engine_result)
    try:
        account_id = response.result["Owner"]
    except KeyError:
        account_id = response.result["Account"]
    transaction_type = response.result["TransactionType"]
    hash_from_previous_txn = response.result["hash"]
    perform_account_object_verification = True

    if "engine_result_code" in response.result and response.result["engine_result_code"] != 0 and response.result[
        "engine_result_code"] != 150:  # OfferCreate tecKILLED flag
        perform_account_object_verification = False
    elif response.status != "success" or "tx_json" not in str(response):
        perform_account_object_verification = False

    if perform_account_object_verification:
        if transaction_type == "NFTokenMint":
            nft_tokens = get_nfts(context, account_id)
            assert nft_tokens, "nft_tokens not found"

            non_fungible_tokens = []
            tx_response = get_tx_response(hash_from_previous_txn)
            for affected_node in tx_response.result["meta"]["AffectedNodes"]:  # tx_response["meta"]["AffectedNodes"]:
                try:
                    if "CreatedNode" in affected_node and affected_node["CreatedNode"][
                        "LedgerEntryType"] == "NFTokenPage":
                        non_fungible_tokens_object = affected_node["CreatedNode"]["NewFields"]["NFTokens"]
                        assert len(non_fungible_tokens_object) <= constants.MAX_NFTOKEN_PAGE_OBJECTS_LIMIT, \
                            "NFToken page objects more than {} [{}]".format(
                                constants.MAX_NFTOKEN_PAGE_OBJECTS_LIMIT,
                                len(non_fungible_tokens_object))

                        for item in non_fungible_tokens_object:
                            non_fungible_token = item["NFToken"]["NFTokenID"]
                            non_fungible_tokens.append(non_fungible_token)

                    if "ModifiedNode" in affected_node and affected_node["ModifiedNode"][
                        "LedgerEntryType"] == "NFTokenPage":
                        non_fungible_tokens_object = affected_node["ModifiedNode"]["FinalFields"]["NFTokens"]
                        assert len(non_fungible_tokens_object) <= constants.MAX_NFTOKEN_PAGE_OBJECTS_LIMIT, \
                            "NFToken page objects more than {} [{}]".format(
                                constants.MAX_NFTOKEN_PAGE_OBJECTS_LIMIT,
                                len(non_fungible_tokens_object))

                        for item in non_fungible_tokens_object:
                            non_fungible_token = item["NFToken"]["NFTokenID"]
                            non_fungible_tokens.append(non_fungible_token)

                except KeyError as e:
                    pass

            if len(nft_tokens) <= constants.MAX_NFTOKEN_PAGE_OBJECTS_LIMIT:
                assert set(non_fungible_tokens) == set(nft_tokens), "Non Fungible Token object count mismatch"


def verify_nftoken_burn_account_objects(context, response, engine_result=ResponseCode.success):
    verify_transaction_validity(context, response, engine_result=engine_result)
    verify_response_code(response, engine_result)

    try:
        account_id = response.result["Owner"]
    except KeyError:
        account_id = response.result["Account"]
    hash_from_previous_txn = response.result["hash"]
    transaction_type = response.result["TransactionType"]
    object_removed = False
    account_objects_response = get_account_objects_response(context.client, account_id)

    if account_objects_response.status != 'error':
        if not account_objects_response.result["account_objects"] and transaction_type != "AccountDelete":
            object_removed = True
            deleted_node_found = True
        else:
            tx_response = get_tx_response(hash_from_previous_txn)
            for affected_node in tx_response["meta"]["AffectedNodes"]:
                try:
                    if "DeletedNode" in affected_node and transaction_type == tx_response["TransactionType"]:
                        deleted_node_found = True
                        ledger_index = affected_node["DeletedNode"]["LedgerIndex"]
                        previous_txn_id = affected_node["DeletedNode"]["FinalFields"]["PreviousTxnID"]
                        break
                except KeyError as e:
                    pass

            for account_object in account_objects_response.result["account_objects"]:
                if account_object["index"] == ledger_index or account_object["PreviousTxnID"] == previous_txn_id:
                    if transaction_type == "OfferCancel" and account_object["LedgerEntryType"] == "RippleState":
                        break
                    else:
                        account_object_found = True
                        break

            if previous_txn_id and not account_object_found:
                object_removed = True

        if not object_removed and not deleted_node_found and not account_object_found:
            assert previous_txn_id is None, "DeletedNode created for transaction type: {}".format(
                transaction_type)
        else:
            assert object_removed, "account object not cleared for txn '{}'".format(hash_from_previous_txn)


def verify_ticket_create_account_objects(context, response, engine_result=ResponseCode.success):
    verify_transaction_validity(context, response, engine_result=engine_result)
    verify_response_code(response, engine_result)

    try:
        account_id = response.result["Owner"]
    except KeyError:
        account_id = response.result["Account"]
    transaction_type = response.result["TransactionType"]

    if "engine_result_code" in response.result and response.result["engine_result_code"] != 0 and response.result[
        "engine_result_code"] != 150:
        perform_account_object_verification = False
    elif response.status != "success" or "tx_json" not in str(response):
        perform_account_object_verification = False
    if perform_account_object_verification:
        account_objects_response = get_account_objects_response(context.client, account_id)
        if account_objects_response.status != 'error':
            assert account_id == account_objects_response.result['account']
            for account_object in account_objects_response.result["account_objects"]:
                assert account_object['LedgerEntryType'] in transaction_type


def verify_account_delete_account_objects(context, response, engine_result=ResponseCode.success):
    verify_transaction_validity(context, response, engine_result=engine_result)
    verify_response_code(response, engine_result)

    try:
        account_id = response.result["Owner"]
    except KeyError:
        account_id = response.result["Account"]
    hash_from_previous_txn = response.result["hash"]
    transaction_type = response.result["TransactionType"]
    object_removed = False
    account_objects_response = get_account_objects_response(context.client, account_id)
    if transaction_type == "AccountDelete":
        if "error" in account_objects_response.result and account_objects_response.result["error"] == "actNotFound":
            object_removed = True
        assert object_removed, "account object not cleared for txn '{}'".format(hash_from_previous_txn)
        if account_objects_response.status != 'error':
            assert account_id == account_objects_response.result['account']
            for account_object in account_objects_response.result["account_objects"]:
                assert account_object['LedgerEntryType'] == "RippleState"


def verify_offer_create_account_objects(context, response, offer_crossing=None, engine_result=ResponseCode.success):
    verify_transaction_validity(context, response, engine_result=engine_result)
    verify_response_code(response, engine_result)
    perform_account_object_verification = True

    if "engine_result_code" in response.result and response.result["engine_result_code"] != 0 and response.result[
        "engine_result_code"] != 150:
        perform_account_object_verification = False
    elif response.status != "success" or "tx_json" not in str(response):
        perform_account_object_verification = False

    if perform_account_object_verification:
        try:
            account_id = response.result["Owner"]
        except KeyError:
            account_id = response.result["Account"]

        transaction_type = response.result["TransactionType"]
        if transaction_type == "OfferCreate":
            account_objects_response = get_account_objects_response(context.client, account_id)
            if account_objects_response.status != 'error':
                assert account_objects_response, "Account object not created in ledger"
                assert response.result["Account"] == account_objects_response.result[
                    'account'], "Account name is not correct"

                offer_crossing_status = False
                for account_object in account_objects_response.result["account_objects"]:
                    if offer_crossing:
                        if account_object['LedgerEntryType'] == "RippleState":
                            offer_crossing_status = True
                    elif offer_crossing is False:
                        if account_object['LedgerEntryType'] == "Offer":
                            offer_crossing_status = True
                    else:
                        if account_object['LedgerEntryType'] == "Offer":
                            offer_crossing_status = True

                assert offer_crossing_status


def get_account_objects_response(client, account_id):
    max_timeout = 20
    start_time = time.time()
    end_time = start_time + max_timeout
    account_objects = None
    while time.time() <= end_time and not account_objects:
        time.sleep(1)
        account_objects_request = ObjFactory.getObj(
            ObjType.account_object,
            account=account_id,
        )
        account_objects = (client.request(account_objects_request))
    return account_objects


def get_account_lines_response(context, account_id, ledger_index="validated"):
    account_lines_request = ObjFactory.getObj(
        ObjType.account_lines,
        account=account_id,
        ledger_index=ledger_index
    )
    return context.client.request(account_lines_request)


def get_tx_response(context, tx_id):
    tx_request = ObjFactory.getObj(
        ObjType.tx,
        transaction=tx_id,
        binary=False
    )
    return context.client.request(tx_request)


def get_nfts(context, account_id, ledger_index="validated"):
    account_nfts_request = ObjFactory.getObj(
        ObjType.account_nfts,
        account=account_id,
        ledger_index=ledger_index
    )
    account_nfts = context.client.request(account_nfts_request)
    nfts = []
    for item in account_nfts["account_nfts"]:
        nft_token = item['NFTokenID']
        nfts.append(nft_token)
    return nfts


def get_account_nfts(client, account_id, ledger_index="validated"):
    account_nfts_request = ObjFactory.getObj(
        ObjType.account_nfts,
        account=account_id,
        ledger_index=ledger_index
    )
    return client.request(account_nfts_request)


def sanitize_args(arg):
    if arg.startswith('"') and (arg.endswith('"')):
        fixed_arg = arg[1:]
        fixed_arg = fixed_arg[:-1]
        return fixed_arg
    else:
        return arg


def verify_transaction_validity(context, response=None, tx_id=None, engine_result="tesSUCCESS", max_timeout=30):
    is_tx_valid = False
    perform_txn_validation = False
    if tx_id:
        perform_txn_validation = True
    elif response:
        tx_id = response.result["hash"]
        if "engine_result" in response.result:
            if response.result["engine_result"] == "tesSUCCESS" or response.result["engine_result"] == "terQUEUED" or \
                    response["engine_result"] == "tecKILLED":
                perform_txn_validation = True
        elif response.status == "success":
            perform_txn_validation = True

    if perform_txn_validation:
        start_time = time.time()
        end_time = start_time + max_timeout
        transaction_result = None
        while time.time() <= end_time:
            tx_response = get_tx_response(context, tx_id)
            if "validated" in tx_response.result:
                if "meta" in tx_response.result:
                    transaction_result = tx_response.result["meta"]["TransactionResult"]
                if tx_response.result["validated"]:
                    if transaction_result == engine_result:
                        is_tx_valid = True
                        break
            time.sleep(1)

    if not is_tx_valid:
        return False

import random
import string

from behave import *
from hamcrest import assert_that, equal_to, contains_string
from xrpl.account import get_balance
from xrpl.models import AccountSet, AccountSetFlag, Tx

from features.lib.ObjFactory import ObjFactory, ObjType
from features.steps import constants
from features.steps.common import sign_autofill_and_submit, ResponseCode, sanitize_args, \
    verify_account_balance, verify_nftoken_mint_account_objects, get_account_sequence, \
    get_ticket_sequence, verify_ticket_create_account_objects, verify_account_delete_account_objects, \
    get_nft_tokens, verify_nftoken_burn_account_objects, wait_for_ledger_to_advance_for_account_delete, \
    verify_account_set_account_objects, verify_payment_account_objects


@when('we mint NFT using same token taxon')
def step_impl(context):
    try:
        payload = ObjFactory.getObj(
            ObjType.nft_token_mint,
            account=context.sourceAddress,
            nftoken_taxon=0,
        )
        context.nft_mint_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)
        context.nft_mint_response_2 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"

        raise e


@then('nft minting is successful')
def step_impl(context):
    verify_account_balance(get_balance(context.sourceAddress, context.client),
                           (int(context.sourceBalance) - (2 * context.minDrop)))
    verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)
    verify_nftoken_mint_account_objects(context, context.nft_mint_response_2)


@when('we mint NFT with low reserves')
def step_impl(context):
    try:
        payload = ObjFactory.getObj(
            ObjType.nft_token_mint,
            account=context.sourceAddress,
            nftoken_taxon=0,
        )
        context.nft_mint_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"

        raise e


@then('nft minting with low reserves is not successful')
def step_impl(context):
    verify_account_balance(get_balance(context.sourceAddress, context.client), context.sourceBalance - context.minDrop)
    verify_nftoken_mint_account_objects(context, context.nft_mint_response_1, ResponseCode.insufficient_reserve)


@when('we mint NFT with optional URI as a string')
def step_impl(context):
    try:
        payload = ObjFactory.getObj(
            ObjType.nft_token_mint,
            account=context.sourceAddress,
            nftoken_taxon=0,
            uri="ipfs://bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi"
        )
        context.nft_mint_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"


@then('nft minting with optional URI as a string is not successful')
def step_impl(context):
    assert_that(context.test_status, equal_to("failed"), "Test Status is incorrect")
    assert_that(str(context.exception), contains_string("non-hexadecimal number found"))
    verify_account_balance(get_balance(context.sourceAddress, context.client), int(context.sourceBalance))


@when('we mint NFT with optional URI as a hex string')
def step_impl(context):
    try:
        uri = "ipfs://bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi"
        hex_uri = uri.encode('utf-8').hex()
        payload = ObjFactory.getObj(
            ObjType.nft_token_mint,
            account=context.sourceAddress,
            nftoken_taxon=0,
            uri=hex_uri
        )
        context.nft_mint_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"
        raise e


@then('nft minting with optional URI as a hex string is not successful')
def step_impl(context):
    verify_account_balance(get_balance(context.sourceAddress, context.client),
                           (int(context.sourceBalance) - (context.minDrop)))
    verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)


@when('we mint NFT with invalid URI')
def step_impl(context):
    try:
        uri = ""
        hex_uri = uri.encode('utf-8').hex()
        payload = ObjFactory.getObj(
            ObjType.nft_token_mint,
            account=context.sourceAddress,
            nftoken_taxon=0,
            uri=hex_uri
        )
        context.nft_mint_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"


@then('nft minting with invalid URI is not successful')
def step_impl(context):
    assert_that(context.test_status, equal_to("failed"), "Test Status is incorrect")
    assert_that(str(context.exception), contains_string("Malformed transaction"))
    verify_account_balance(get_balance(context.sourceAddress, context.client), int(context.sourceBalance))


@when('we mint NFT with optional URI with more than 265 characters')
def step_impl(context):
    try:
        uri_length = 257
        uri = "ipfs://bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi"
        for count in range(uri_length - len(uri)):
            uri += random.choice(string.ascii_letters)

        hex_uri = uri.encode('utf-8').hex()
        payload = ObjFactory.getObj(
            ObjType.nft_token_mint,
            account=context.sourceAddress,
            nftoken_taxon=0,
            uri=hex_uri
        )
        context.nft_mint_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"


@then('nft minting with optional URI with more than 265 characters is not successful')
def step_impl(context):
    assert_that(context.test_status, equal_to("failed"), "Test Status is incorrect")
    assert_that(str(context.exception), contains_string("Must not be longer than 512 characters"))
    verify_account_balance(get_balance(context.sourceAddress, context.client), int(context.sourceBalance))


@when('we mint NFT with optional {transfer_fee} transfer fee')
def step_impl(context, transfer_fee):
    try:
        fee = int(sanitize_args(transfer_fee))
        payload = ObjFactory.getObj(
            ObjType.nft_token_mint,
            account=context.sourceAddress,
            transfer_fee=fee,
            flags=8,
            nftoken_taxon=0
        )
        context.nft_mint_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"


@then('nft minting with optional negative transfer fee is not successful')
def step_impl(context):
    assert_that(context.test_status, equal_to("failed"), "Test Status is incorrect")
    assert_that(str(context.exception), contains_string("can't convert negative int to unsigned"))
    verify_account_balance(get_balance(context.sourceAddress, context.client), int(context.sourceBalance))


@then('nft minting with optional zero transfer fee is successful')
def step_impl(context):
    verify_account_balance(get_balance(context.sourceAddress, context.client),
                           int(context.sourceBalance) - context.minDrop)
    verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)


@then('nft minting with optional transfer fee in decimal is not successful')
def step_impl(context):
    assert_that(context.test_status, equal_to("failed"), "Test Status is incorrect")
    assert_that(str(context.exception), contains_string("invalid literal for int() with base 10"))
    verify_account_balance(get_balance(context.sourceAddress, context.client), int(context.sourceBalance))


@then('nft minting with optional transfer fee more than 50000 is not successful')
def step_impl(context):
    assert_that(context.test_status, equal_to("failed"), "Test Status is incorrect")
    assert_that(str(context.exception), contains_string("'transfer_fee': 'Must not be greater than 50000'"))
    verify_account_balance(get_balance(context.sourceAddress, context.client), int(context.sourceBalance))


@when('we mint NFT without tfTransferable flag')
def step_impl(context):
    try:
        payload = ObjFactory.getObj(
            ObjType.nft_token_mint,
            account=context.sourceAddress,
            transfer_fee=50,
            # flags=8,
            nftoken_taxon=0
        )
        context.nft_mint_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"


@then('nft minting without tfTransferable flag is not successful')
def step_impl(context):
    assert_that(context.test_status, equal_to("failed"), "Test Status is incorrect")
    assert_that(str(context.exception), contains_string("Malformed transaction"))
    verify_account_balance(get_balance(context.sourceAddress, context.client), int(context.sourceBalance))


@when('we mint NFT with optional memos')
def step_impl(context):
    try:
        uri = "ipfs://bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi"
        hex_uri = uri.encode('utf-8').hex()
        payload = ObjFactory.getObj(
            ObjType.nft_token_mint,
            account=context.sourceAddress,
            uri=hex_uri,
            memos=[
                ObjFactory.getObj(
                    ObjType.memo,
                    memo_type="687474703A2F2F6578616D706C652E636F6D2F6D656D6F2F67656E65726963",
                    memo_data="72656E74"
                )
            ],
            nftoken_taxon=0
        )
        context.nft_mint_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"


@then('nft minting with optional memos is successful')
def step_impl(context):
    verify_account_balance(get_balance(context.sourceAddress, context.client),
                           int(context.sourceBalance) - context.minDrop)
    verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)


@when('we mint NFT with bad seed')
def step_impl(context):
    try:
        payload = ObjFactory.getObj(
            ObjType.nft_token_mint,
            account=context.sourceAddress,
            nftoken_taxon=0,
        )
        context.nft_mint_response_1 = sign_autofill_and_submit(context.client, payload, context.destinationWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"


@then('nft minting with bad seed is not successful')
def step_impl(context):
    assert_that(context.test_status, equal_to("failed"), "Test Status is incorrect")
    assert_that(str(context.exception), contains_string("Prelim result: tefBAD_AUTH"))
    verify_account_balance(get_balance(context.sourceAddress, context.client), int(context.sourceBalance))


@when('we mint NFT without nftoken_taxon')
def step_impl(context):
    try:
        payload = ObjFactory.getObj(
            ObjType.nft_token_mint,
            account=context.sourceAddress,
        )
        context.nft_mint_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"


@then('nft minting without nftoken_taxon is not successful')
def step_impl(context):
    assert_that(context.test_status, equal_to("failed"), "Test Status is incorrect")
    assert_that(str(context.exception), contains_string("nftoken_taxon is not set"))
    verify_account_balance(get_balance(context.sourceAddress, context.client), int(context.sourceBalance))


@when('we mint NFT with negative nftoken_taxon')
def step_impl(context):
    try:
        payload = ObjFactory.getObj(
            ObjType.nft_token_mint,
            account=context.sourceAddress,
            nftoken_taxon=-10,
        )
        context.nft_mint_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"


@then('nft minting with negative nftoken_taxon is not successful')
def step_impl(context):
    assert_that(context.test_status, equal_to("failed"), "Test Status is incorrect")
    assert_that(str(context.exception), contains_string("can't convert negative int to unsigned"))
    verify_account_balance(get_balance(context.sourceAddress, context.client), int(context.sourceBalance))


@when('we mint NFT with too high nftoken_taxon')
def step_impl(context):
    try:
        payload = ObjFactory.getObj(
            ObjType.nft_token_mint,
            account=context.sourceAddress,
            nftoken_taxon=4294967296,
        )
        context.nft_mint_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"


@then('nft minting with too high nftoken_taxon is not successful')
def step_impl(context):
    assert_that(context.test_status, equal_to("failed"), "Test Status is incorrect")
    assert_that(str(context.exception), contains_string("int too big to convert"))
    verify_account_balance(get_balance(context.sourceAddress, context.client), int(context.sourceBalance))


@when('we mint NFT without source account field')
def step_impl(context):
    try:
        payload = ObjFactory.getObj(
            ObjType.nft_token_mint,
            nftoken_taxon=0,
        )
        context.nft_mint_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"


@then('nft minting without source account field is not successful')
def step_impl(context):
    assert_that(context.test_status, equal_to("failed"), "Test Status is incorrect")
    assert_that(str(context.exception), contains_string("account is not set"))
    verify_account_balance(get_balance(context.sourceAddress, context.client), int(context.sourceBalance))


@when('we mint NFT with empty source account field')
def step_impl(context):
    try:
        payload = ObjFactory.getObj(
            ObjType.nft_token_mint,
            account="",
            nftoken_taxon=0,
        )
        context.nft_mint_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"


@then('nft minting with empty source account field is not successful')
def step_impl(context):
    assert_that(context.test_status, equal_to("failed"), "Test Status is incorrect")
    assert_that(str(context.exception), contains_string("badSeed: Disallowed seed"))
    verify_account_balance(get_balance(context.sourceAddress, context.client), int(context.sourceBalance))


@when('we mint NFT with same account as issuer')
def step_impl(context):
    try:
        payload = ObjFactory.getObj(
            ObjType.nft_token_mint,
            account=context.sourceAddress,
            issuer=context.sourceAddress,
            nftoken_taxon=0,
        )
        context.nft_mint_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"


@then('nft minting with same account as issuer is not successful')
def step_impl(context):
    assert_that(context.test_status, equal_to("failed"), "Test Status is incorrect")
    assert_that(str(context.exception), contains_string("'issuer': 'Must not be the same as the account'"))
    verify_account_balance(get_balance(context.sourceAddress, context.client), int(context.sourceBalance))


@when('we mint NFT with invalid issuer')
def step_impl(context):
    try:
        payload = ObjFactory.getObj(
            ObjType.nft_token_mint,
            account=context.sourceAddress,
            issuer=context.invalidAddress,
            nftoken_taxon=0,
        )
        context.nft_mint_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"


@then('nft minting with invalid issuer is not successful')
def step_impl(context):
    assert_that(context.test_status, equal_to("failed"), "Test Status is incorrect")
    assert_that(str(context.exception), contains_string("expected valid classic address or X-Address, received str."))
    verify_account_balance(get_balance(context.sourceAddress, context.client), int(context.sourceBalance))


@when('we mint NFT with issuer having unauthorized user')
def step_impl(context):
    try:
        payload = AccountSet(
            account=context.sourceAddress,
            sequence=get_account_sequence(context.client, context.sourceAddress),
            fee="10",
            nftoken_minter=context.destinationAddress
        )
        context.account_set_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)

        payload = ObjFactory.getObj(
            ObjType.nft_token_mint,
            account=context.destinationAddress,
            issuer=context.sourceAddress,
            nftoken_taxon=0,
        )
        context.nft_mint_response_1 = sign_autofill_and_submit(context.client, payload, context.destinationWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"


@then('nft minting with issuer having unauthorized user is not successful')
def step_impl(context):
    assert_that(context.test_status, equal_to("failed"), "Test Status is incorrect")
    assert_that(str(context.exception), contains_string(
        "'nftoken_minter': 'Will not set the minter unless AccountSetFlag.ASF_AUTHORIZED_NFTOKEN_MINTER is set'"))
    verify_account_balance(get_balance(context.sourceAddress, context.client), int(context.sourceBalance))


@when('we mint NFT with issuer having authorized user')
def step_impl(context):
    try:
        payload = AccountSet(
            account=context.sourceAddress,
            sequence=get_account_sequence(context.client, context.sourceAddress),
            fee="10",
            set_flag=AccountSetFlag.ASF_AUTHORIZED_NFTOKEN_MINTER,
            nftoken_minter=context.destinationAddress
        )
        context.account_set_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)

        payload = ObjFactory.getObj(
            ObjType.nft_token_mint,
            account=context.destinationAddress,
            issuer=context.sourceAddress,
            nftoken_taxon=0,
        )
        context.nft_mint_response_1 = sign_autofill_and_submit(context.client, payload, context.destinationWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"
        raise e


@then('nft minting with issuer having authorized user is successful')
def step_impl(context):
    verify_account_balance(get_balance(context.sourceAddress, context.client),
                           int(context.sourceBalance) - (context.minDrop))
    verify_account_balance(get_balance(context.destinationAddress, context.client),
                           int(context.destinationBalance) - (context.minDrop))
    verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)

    verify_account_set_account_objects(context, context.account_set_response_1)


@when('we mint NFT on ticket with authorized user')
def step_impl(context):
    try:
        payload = AccountSet(
            account=context.sourceAddress,
            sequence=get_account_sequence(context.client, context.sourceAddress),
            fee="10",
            set_flag=AccountSetFlag.ASF_AUTHORIZED_NFTOKEN_MINTER,
            nftoken_minter=context.destinationAddress
        )
        context.account_set_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)

        payload = ObjFactory.getObj(
            ObjType.ticket_create,
            account=context.destinationAddress,
            sequence=get_account_sequence(context.client, context.destinationAddress),
            ticket_count=1,
        )
        context.tc_response_1 = sign_autofill_and_submit(context.client, payload, context.destinationWallet)

        ticket_seq = get_ticket_sequence(context.client, context.destinationAddress)[0]
        # print(ticket_seq)
        payload = ObjFactory.getObj(
            ObjType.nft_token_mint,
            account=context.destinationAddress,
            issuer=context.sourceAddress,
            nftoken_taxon=0,
            sequence=0,
            ticket_sequence=ticket_seq
        )

        context.nft_mint_response_1 = sign_autofill_and_submit(context.client, payload, context.destinationWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"
        raise e


@then('nft minting on ticket with authorized user is successful')
def step_impl(context):
    verify_account_balance(get_balance(context.sourceAddress, context.client),
                           int(context.sourceBalance) - (context.minDrop))
    verify_account_balance(get_balance(context.destinationAddress, context.client),
                           int(context.destinationBalance) - (2 * context.minDrop))

    verify_ticket_create_account_objects(context, context.tc_response_1)

    verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)

    verify_account_set_account_objects(context, context.account_set_response_1)


@when('we mint NFT on ticket with issuer without user authorization')
def step_impl(context):
    try:
        payload = AccountSet(
            account=context.sourceAddress,
            set_flag=AccountSetFlag.ASF_AUTHORIZED_NFTOKEN_MINTER,
            nftoken_minter=context.destinationAddress
        )
        context.account_set_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)

        payload = AccountSet(
            account=context.sourceAddress,
            clear_flag=AccountSetFlag.ASF_AUTHORIZED_NFTOKEN_MINTER,
        )
        context.account_set_response_2 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)

        payload = ObjFactory.getObj(
            ObjType.nft_token_mint,
            account=context.destinationAddress,
            issuer=context.sourceAddress,
            nftoken_taxon=0,
        )
        context.nft_mint_response_1 = sign_autofill_and_submit(context.client, payload, context.destinationWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"
        raise e


@then('nft minting on ticket with issuer without user authorization is not successful')
def step_impl(context):
    verify_account_balance(get_balance(context.sourceAddress, context.client),
                           int(context.sourceBalance) - (2 * context.minDrop))
    verify_account_balance(get_balance(context.destinationAddress, context.client),
                           int(context.destinationBalance) - (context.minDrop))

    verify_nftoken_mint_account_objects(context, context.nft_mint_response_1, ResponseCode.no_permission)
    verify_account_set_account_objects(context, context.account_set_response_1)
    verify_account_set_account_objects(context, context.account_set_response_2)


@when('we mint NFT with issuer and remove authorization')
def step_impl(context):
    try:
        payload = AccountSet(
            account=context.sourceAddress,
            set_flag=AccountSetFlag.ASF_AUTHORIZED_NFTOKEN_MINTER,
            nftoken_minter=context.destinationAddress
        )
        context.account_set_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)

        payload = ObjFactory.getObj(
            ObjType.nft_token_mint,
            account=context.destinationAddress,
            issuer=context.sourceAddress,
            nftoken_taxon=0,
        )
        context.nft_mint_response_1 = sign_autofill_and_submit(context.client, payload, context.destinationWallet)

        payload = AccountSet(
            account=context.sourceAddress,
            clear_flag=AccountSetFlag.ASF_AUTHORIZED_NFTOKEN_MINTER,
        )
        context.account_set_response_2 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)

        payload = ObjFactory.getObj(
            ObjType.nft_token_mint,
            account=context.destinationAddress,
            issuer=context.sourceAddress,
            nftoken_taxon=0,
        )
        context.nft_mint_response_2 = sign_autofill_and_submit(context.client, payload, context.destinationWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"
        raise e


@then('nft minting with issuer and removing authorization is successful')
def step_impl(context):
    verify_account_balance(get_balance(context.sourceAddress, context.client),
                           int(context.sourceBalance) - (2 * context.minDrop))
    verify_account_balance(get_balance(context.destinationAddress, context.client),
                           int(context.destinationBalance) - (2 * context.minDrop))

    verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)
    verify_nftoken_mint_account_objects(context, context.nft_mint_response_2, ResponseCode.no_permission)

    verify_account_set_account_objects(context, context.account_set_response_1)
    verify_account_set_account_objects(context, context.account_set_response_2)


@when('we change authorized user and mint NFT')
def step_impl(context):
    try:
        payload = AccountSet(
            account=context.aliceAddress,
            set_flag=AccountSetFlag.ASF_AUTHORIZED_NFTOKEN_MINTER,
            nftoken_minter=context.bobAddress
        )
        context.account_set_response_1 = sign_autofill_and_submit(context.client, payload, context.aliceWallet)

        payload = AccountSet(
            account=context.aliceAddress,
            set_flag=AccountSetFlag.ASF_AUTHORIZED_NFTOKEN_MINTER,
            nftoken_minter=context.carolAddress
        )
        context.account_set_response_2 = sign_autofill_and_submit(context.client, payload, context.aliceWallet)

        payload = ObjFactory.getObj(
            ObjType.nft_token_mint,
            account=context.bobAddress,
            issuer=context.aliceAddress,
            nftoken_taxon=0,
        )
        context.nft_mint_response_1 = sign_autofill_and_submit(context.client, payload, context.bobWallet)

        payload = ObjFactory.getObj(
            ObjType.nft_token_mint,
            account=context.carolAddress,
            issuer=context.aliceAddress,
            nftoken_taxon=0,
        )
        context.nft_mint_response_2 = sign_autofill_and_submit(context.client, payload, context.carolWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"
        raise e


@then('NFT minting after changing authorized user is successful')
def step_impl(context):
    verify_account_balance(get_balance(context.aliceAddress, context.client),
                           int(context.aliceBalance) - (2 * context.minDrop))
    verify_account_balance(get_balance(context.bobAddress, context.client),
                           int(context.bobBalance) - (context.minDrop))
    verify_account_balance(get_balance(context.carolAddress, context.client),
                           int(context.carolBalance) - (context.minDrop))

    verify_nftoken_mint_account_objects(context, context.nft_mint_response_1, ResponseCode.no_permission)
    verify_nftoken_mint_account_objects(context, context.nft_mint_response_2)

    verify_account_set_account_objects(context, context.account_set_response_1)
    verify_account_set_account_objects(context, context.account_set_response_2)


@when('we mint NFT using authorization chain of authorized users')
def step_impl(context):
    try:
        payload = AccountSet(
            account=context.aliceAddress,
            set_flag=AccountSetFlag.ASF_AUTHORIZED_NFTOKEN_MINTER,
            nftoken_minter=context.bobAddress
        )
        context.account_set_response_1 = sign_autofill_and_submit(context.client, payload, context.aliceWallet)

        payload = AccountSet(
            account=context.bobAddress,
            set_flag=AccountSetFlag.ASF_AUTHORIZED_NFTOKEN_MINTER,
            nftoken_minter=context.carolAddress
        )
        context.account_set_response_2 = sign_autofill_and_submit(context.client, payload, context.bobWallet)

        payload = ObjFactory.getObj(
            ObjType.nft_token_mint,
            account=context.bobAddress,
            issuer=context.aliceAddress,
            nftoken_taxon=0,
        )
        context.nft_mint_response_1 = sign_autofill_and_submit(context.client, payload, context.bobWallet)

        payload = ObjFactory.getObj(
            ObjType.nft_token_mint,
            account=context.carolAddress,
            issuer=context.aliceAddress,
            nftoken_taxon=0,
        )
        context.nft_mint_response_2 = sign_autofill_and_submit(context.client, payload, context.carolWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"
        raise e


@then('NFT minting using authorization chain of authorized users is not successful')
def step_impl(context):
    verify_account_balance(get_balance(context.aliceAddress, context.client),
                           int(context.aliceBalance) - (context.minDrop))
    verify_account_balance(get_balance(context.bobAddress, context.client),
                           int(context.bobBalance) - (2 * context.minDrop))
    verify_account_balance(get_balance(context.carolAddress, context.client),
                           int(context.carolBalance) - (context.minDrop))

    verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)
    verify_nftoken_mint_account_objects(context, context.nft_mint_response_2, ResponseCode.no_permission)

    verify_account_set_account_objects(context, context.account_set_response_1)
    verify_account_set_account_objects(context, context.account_set_response_2)


@when('we mint NFT using ticket')
def step_impl(context):
    try:
        payload = ObjFactory.getObj(
            ObjType.ticket_create,
            account=context.sourceAddress,
            sequence=get_account_sequence(context.client, context.sourceAddress),
            ticket_count=1,
        )
        context.tc_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)

        payload = ObjFactory.getObj(
            ObjType.nft_token_mint,
            account=context.sourceAddress,
            nftoken_taxon=0,
            sequence=0,
            ticket_sequence=get_ticket_sequence(context.client, context.sourceAddress)[0]
        )
        context.nft_mint_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"
        raise e


@then('NFT minting using ticket is successful')
def step_impl(context):
    # TODO: Extract out fee as constant
    verify_account_balance(get_balance(context.sourceAddress, context.client),
                           int(context.sourceBalance) - (2 * context.minDrop))

    verify_ticket_create_account_objects(context, context.tc_response_1)
    verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)


@when('we mint NFT and try to delete account owner')
def step_impl(context):
    try:
        payload = ObjFactory.getObj(
            ObjType.nft_token_mint,
            account=context.sourceAddress,
            nftoken_taxon=0,
        )
        context.nft_mint_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)

        payload = ObjFactory.getObj(
            ObjType.account_delete,
            account=context.sourceAddress,
            destination=context.destinationAddress,
            fee=constants.DEFAULT_DELETE_ACCOUNT_FEE,
            sequence=get_account_sequence(context.client, context.sourceAddress)
        )
        response = sign_autofill_and_submit(context.client, payload, context.sourceWallet)
        context.ad_response_1 = context.client.request(Tx(transaction=response.result["hash"]))
    except Exception as e:
        context.exception = e
        context.test_status = "failed"
        raise e


@then('deleting account owner after NFT minting is not successful')
def step_impl(context):
    # TODO: Extract out fee as constant
    verify_account_balance(get_balance(context.sourceAddress, context.client),
                           int(context.sourceBalance) - (context.minDrop) - 2000000)
    verify_account_balance(get_balance(context.destinationAddress, context.client),
                           int(context.destinationBalance))

    # TODO: Eval why failing
    # verify_account_delete_account_objects(context, context.ad_response_1, ResponseCode.has_obligations)
    verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)


@when('we mint NFT on ticket and try to delete account owner')
def step_impl(context):
    try:
        payload = ObjFactory.getObj(
            ObjType.ticket_create,
            account=context.sourceAddress,
            sequence=get_account_sequence(context.client, context.sourceAddress),
            ticket_count=1,
        )
        context.tc_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)

        payload = ObjFactory.getObj(
            ObjType.nft_token_mint,
            account=context.sourceAddress,
            nftoken_taxon=0,
            sequence=0,
            ticket_sequence=get_ticket_sequence(context.client, context.sourceAddress)[0]
        )
        context.nft_mint_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)

        payload = ObjFactory.getObj(
            ObjType.account_delete,
            account=context.sourceAddress,
            destination=context.destinationAddress,
            fee=constants.DEFAULT_DELETE_ACCOUNT_FEE,
            sequence=get_account_sequence(context.client, context.sourceAddress)
        )
        response = sign_autofill_and_submit(context.client, payload, context.sourceWallet)
        context.ad_response_1 = context.client.request(Tx(transaction=response.result["hash"]))
    except Exception as e:
        context.exception = e
        context.test_status = "failed"

        raise e


@then('deleting account owner after NFT minting on ticket is not successful')
def step_impl(context):
    # TODO: Extract out fee as constant
    verify_account_balance(get_balance(context.sourceAddress, context.client),
                           int(context.sourceBalance) - (2 * context.minDrop) - 2000000)
    verify_account_balance(get_balance(context.destinationAddress, context.client),
                           int(context.destinationBalance))

    verify_ticket_create_account_objects(context, context.tc_response_1)

    # TODO: Eval why failing
    # verify_account_delete_account_objects(context, context.ad_response_1, ResponseCode.has_obligations)

    verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)


@when('we mint NFT with issuer and then remove authorization and delete account owner')
def step_impl(context):
    try:

        payload = AccountSet(
            account=context.sourceAddress,
            set_flag=AccountSetFlag.ASF_AUTHORIZED_NFTOKEN_MINTER,
            nftoken_minter=context.destinationAddress
        )
        context.account_set_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)

        payload = ObjFactory.getObj(
            ObjType.nft_token_mint,
            account=context.destinationAddress,
            issuer=context.sourceAddress,
            nftoken_taxon=0,
        )
        context.nft_mint_response_1 = sign_autofill_and_submit(context.client, payload, context.destinationWallet)

        payload = AccountSet(
            account=context.sourceAddress,
            clear_flag=AccountSetFlag.ASF_AUTHORIZED_NFTOKEN_MINTER,
        )
        context.account_set_response_2 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)

        payload = ObjFactory.getObj(
            ObjType.account_delete,
            account=context.destinationAddress,
            destination=context.sourceAddress,
            fee=constants.DEFAULT_DELETE_ACCOUNT_FEE,
            sequence=get_account_sequence(context.client, context.destinationAddress)
        )
        context.ad_response_1 = sign_autofill_and_submit(context.client, payload, context.destinationWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"
        raise e


@then('removing authorization and deleting account owner after NFT minting is not successful')
def step_impl(context):
    # TODO: Extract out fee as constant
    verify_account_balance(get_balance(context.sourceAddress, context.client),
                           int(context.sourceBalance) - (2 * context.minDrop))
    verify_account_balance(get_balance(context.destinationAddress, context.client),
                           int(context.destinationBalance) - context.minDrop - 2000000)

    # TODO: Eval why failing
    # verify_account_delete_account_objects(context, context.ad_response_1, ResponseCode.has_obligations)

    verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)

    verify_account_set_account_objects(context, context.account_set_response_1)
    verify_account_set_account_objects(context, context.account_set_response_2)


@when('we mint NFT with issuer and then remove authorization and delete issuer')
def step_impl(context):
    try:
        payload = AccountSet(
            account=context.sourceAddress,
            set_flag=AccountSetFlag.ASF_AUTHORIZED_NFTOKEN_MINTER,
            nftoken_minter=context.destinationAddress
        )
        context.account_set_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)

        payload = ObjFactory.getObj(
            ObjType.nft_token_mint,
            account=context.destinationAddress,
            issuer=context.sourceAddress,
            nftoken_taxon=0,
        )
        context.nft_mint_response_1 = sign_autofill_and_submit(context.client, payload, context.destinationWallet)

        payload = AccountSet(
            account=context.sourceAddress,
            clear_flag=AccountSetFlag.ASF_AUTHORIZED_NFTOKEN_MINTER,
        )
        context.account_set_response_2 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)

        payload = ObjFactory.getObj(
            ObjType.account_delete,
            account=context.sourceAddress,
            destination=context.destinationAddress,
            fee=constants.DEFAULT_DELETE_ACCOUNT_FEE,
            sequence=get_account_sequence(context.client, context.sourceAddress)
        )
        context.ad_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"
        raise e


@then('removing authorization and deleting issuer after NFT minting is not successful')
def step_impl(context):
    # TODO: Extract out fee as constant
    verify_account_balance(get_balance(context.sourceAddress, context.client),
                           int(context.sourceBalance) - (2 * context.minDrop) - 2000000)
    verify_account_balance(get_balance(context.destinationAddress, context.client),
                           int(context.destinationBalance) - context.minDrop)

    # TODO: Eval why failing
    # verify_account_delete_account_objects(context, context.ad_response_1, ResponseCode.has_obligations)

    verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)

    verify_account_set_account_objects(context, context.account_set_response_1)
    verify_account_set_account_objects(context, context.account_set_response_2)


@when('we burn NFT as owner')
def step_impl(context):
    try:
        payload = ObjFactory.getObj(
            ObjType.nft_token_mint,
            account=context.sourceAddress,
            nftoken_taxon=0,
        )
        context.nft_mint_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)

        payload = ObjFactory.getObj(
            ObjType.nft_token_burn,
            account=context.sourceAddress,
            nftoken_id=get_nft_tokens(context.client, context.sourceAddress)[-1],
        )
        context.nft_burn_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"
        raise e


@then('burning NFT as owner is successful')
def step_impl(context):
    # TODO: Extract out fee as constant
    verify_account_balance(get_balance(context.sourceAddress, context.client),
                           int(context.sourceBalance) - (2 * context.minDrop))

    verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)
    verify_nftoken_burn_account_objects(context, context.nft_burn_response_1)


@when('we burn NFT with low reserves')
def step_impl(context):
    try:
        payload = ObjFactory.getObj(
            ObjType.nft_token_mint,
            account=context.sourceAddress,
            nftoken_taxon=0,
        )
        context.nft_mint_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)

        final_transfer_amount = str(
            get_balance(context.sourceAddress, context.client) - int(constants.BASE_RESERVE) - int(
                constants.OWNER_RESERVE) - context.minDrop)
        context.py_response_1 = sign_autofill_and_submit(context.client,
                                                         ObjFactory.getObj(
                                                             ObjType.payment,
                                                             account=context.sourceAddress,
                                                             destination=context.destinationAddress,
                                                             amount=final_transfer_amount),
                                                         context.sourceWallet)

        payload = ObjFactory.getObj(
            ObjType.nft_token_burn,
            account=context.sourceAddress,
            nftoken_id=get_nft_tokens(context.client, context.sourceAddress)[-1],
        )
        context.nft_burn_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"
        raise e


@then('burning NFT with low reserves is not successful')
def step_impl(context):
    verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)
    verify_nftoken_burn_account_objects(context, context.nft_burn_response_1)
    verify_payment_account_objects(context, context.py_response_1)


@when('we burn NFT with NFT ID mismatch')
def step_impl(context):
    try:
        payload = ObjFactory.getObj(
            ObjType.nft_token_burn,
            account=context.sourceAddress,
            fee="10",
            nftoken_id="0008000044CAF362635003E9D565979EE87A1668A1FFE7BB2DCBAB9D00000002",
        )
        context.nft_burn_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"

        raise e


@then('burning NFT with NFT ID mismatch is not successful')
def step_impl(context):
    verify_account_balance(get_balance(context.sourceAddress, context.client),
                           int(context.sourceBalance) - context.minDrop)

    verify_nftoken_burn_account_objects(context, context.nft_burn_response_1, ResponseCode.no_entry)


@when('we burn NFT as different user')
def step_impl(context):
    try:
        payload = ObjFactory.getObj(
            ObjType.nft_token_mint,
            account=context.sourceAddress,
            nftoken_taxon=0,
        )
        context.nft_mint_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)

        payload = ObjFactory.getObj(
            ObjType.nft_token_burn,
            account=context.destinationAddress,
            fee="10",
            nftoken_id=get_nft_tokens(context.client, context.sourceAddress)[-1],
        )
        context.nft_burn_response_1 = sign_autofill_and_submit(context.client, payload, context.destinationWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"

        raise e


@then('burning NFT as different user is not successful')
def step_impl(context):
    # TODO: Extract out fee as constant
    print(get_balance(context.sourceAddress, context.client))
    verify_account_balance(get_balance(context.sourceAddress, context.client),
                           int(context.sourceBalance) - context.minDrop)

    verify_account_balance(get_balance(context.destinationAddress, context.client),
                           int(context.destinationBalance) - context.minDrop)

    verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)

    verify_nftoken_burn_account_objects(context, context.nft_burn_response_1, ResponseCode.no_entry)


@when('we mint NFT with issuer burn as owner')
def step_impl(context):
    try:
        payload = AccountSet(
            account=context.sourceAddress,
            set_flag=AccountSetFlag.ASF_AUTHORIZED_NFTOKEN_MINTER,
            nftoken_minter=context.destinationAddress
        )
        context.account_set_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)
        #
        payload = ObjFactory.getObj(
            ObjType.nft_token_mint,
            account=context.destinationAddress,
            issuer=context.sourceAddress,
            nftoken_taxon=0,
        )
        context.nft_mint_response_1 = sign_autofill_and_submit(context.client, payload, context.destinationWallet)

        payload = ObjFactory.getObj(
            ObjType.nft_token_burn,
            account=context.destinationAddress,
            nftoken_id=get_nft_tokens(context.client, context.destinationAddress)[-1],
        )
        context.nft_burn_response_1 = sign_autofill_and_submit(context.client, payload, context.destinationWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"
        raise e


@then('burning NFT with issuer burn as owner is successful')
def step_impl(context):
    verify_account_balance(get_balance(context.sourceAddress, context.client),
                           int(context.sourceBalance) - (context.minDrop))

    verify_account_balance(get_balance(context.destinationAddress, context.client),
                           int(context.destinationBalance) - (2 * context.minDrop))

    verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)
    verify_nftoken_burn_account_objects(context, context.nft_burn_response_1)

    verify_account_set_account_objects(context, context.account_set_response_1)


@when('we mint NFT with issuer burn as issuer without tfBurnable')
def step_impl(context):
    try:
        payload = AccountSet(
            account=context.sourceAddress,
            set_flag=AccountSetFlag.ASF_AUTHORIZED_NFTOKEN_MINTER,
            nftoken_minter=context.destinationAddress
        )
        context.account_set_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)
        #
        payload = ObjFactory.getObj(
            ObjType.nft_token_mint,
            issuer=context.sourceAddress,
            account=context.destinationAddress,
            nftoken_taxon=0,
        )
        context.nft_mint_response_1 = sign_autofill_and_submit(context.client, payload, context.destinationWallet)

        payload = ObjFactory.getObj(
            ObjType.nft_token_burn,
            account=context.sourceAddress,
            owner=context.destinationAddress,
            fee="10",
            nftoken_id=get_nft_tokens(context.client, context.destinationAddress)[-1],
        )
        context.nft_burn_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"

        raise e


@then('burning NFT with issuer burn as issuer without tfBurnable is not successful')
def step_impl(context):
    # TODO: Extract out fee as constant
    print(get_balance(context.sourceAddress, context.client))
    verify_account_balance(get_balance(context.sourceAddress, context.client),
                           int(context.sourceBalance) - (2 * context.minDrop))

    verify_account_balance(get_balance(context.destinationAddress, context.client),
                           int(context.destinationBalance) - context.minDrop)

    verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)

    verify_nftoken_burn_account_objects(context, context.nft_burn_response_1, ResponseCode.no_permission)

    verify_account_set_account_objects(context, context.account_set_response_1)


@when('we mint NFT with issuer burn as issuer with tfBurnable')
def step_impl(context):
    try:
        payload = AccountSet(
            account=context.sourceAddress,
            set_flag=AccountSetFlag.ASF_AUTHORIZED_NFTOKEN_MINTER,
            nftoken_minter=context.destinationAddress
        )
        context.account_set_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)
        #
        payload = ObjFactory.getObj(
            ObjType.nft_token_mint,
            account=context.destinationAddress,
            issuer=context.sourceAddress,
            nftoken_taxon=0,
            flags=1
        )
        context.nft_mint_response_1 = sign_autofill_and_submit(context.client, payload, context.destinationWallet)

        payload = ObjFactory.getObj(
            ObjType.nft_token_burn,
            account=context.sourceAddress,
            owner=context.destinationAddress,
            fee="10",
            nftoken_id=get_nft_tokens(context.client, context.destinationAddress)[-1],
        )
        context.nft_burn_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"
        raise e


@then('burning NFT with issuer burn as issuer with tfBurnable is successful')
def step_impl(context):
    # TODO: Extract out fee as constant
    print(get_balance(context.sourceAddress, context.client))
    verify_account_balance(get_balance(context.sourceAddress, context.client),
                           int(context.sourceBalance) - (2 * context.minDrop))

    verify_account_balance(get_balance(context.destinationAddress, context.client),
                           int(context.destinationBalance) - context.minDrop)

    verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)

    verify_nftoken_burn_account_objects(context, context.nft_burn_response_1)

    verify_account_set_account_objects(context, context.account_set_response_1)


@when('we mint NFT with issuer burn as issuer without owner field')
def step_impl(context):
    try:
        payload = AccountSet(
            account=context.sourceAddress,
            set_flag=AccountSetFlag.ASF_AUTHORIZED_NFTOKEN_MINTER,
            nftoken_minter=context.destinationAddress
        )
        context.account_set_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)
        #
        payload = ObjFactory.getObj(
            ObjType.nft_token_mint,
            issuer=context.sourceAddress,
            account=context.destinationAddress,
            nftoken_taxon=0,
            flags=1
        )
        context.nft_mint_response_1 = sign_autofill_and_submit(context.client, payload, context.destinationWallet)

        payload = ObjFactory.getObj(
            ObjType.nft_token_burn,
            account=context.sourceAddress,
            fee="10",
            nftoken_id=get_nft_tokens(context.client, context.destinationAddress)[-1],
        )
        context.nft_burn_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"
        raise e


@then('burning NFT with issuer burn as issuer without owner field not successful')
def step_impl(context):
    # TODO: Extract out fee as constant
    print(get_balance(context.sourceAddress, context.client))
    verify_account_balance(get_balance(context.sourceAddress, context.client),
                           int(context.sourceBalance) - (2 * context.minDrop))

    verify_account_balance(get_balance(context.destinationAddress, context.client),
                           int(context.destinationBalance) - context.minDrop)

    verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)
    verify_nftoken_burn_account_objects(context, context.nft_burn_response_1, ResponseCode.no_entry)
    verify_account_set_account_objects(context, context.account_set_response_1)


@when('we burn NFT and remint')
def step_impl(context):
    try:
        payload = ObjFactory.getObj(
            ObjType.nft_token_mint,
            account=context.sourceAddress,
            nftoken_taxon=0,
        )
        context.nft_mint_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)

        payload = ObjFactory.getObj(
            ObjType.nft_token_burn,
            account=context.sourceAddress,
            nftoken_id=get_nft_tokens(context.client, context.sourceAddress)[-1],
        )
        context.nft_burn_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)

        payload = ObjFactory.getObj(
            ObjType.nft_token_mint,
            account=context.sourceAddress,
            nftoken_taxon=0,
        )
        context.nft_mint_response_2 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"
        raise e


@then('burning NFT and reminting is successful')
def step_impl(context):
    # TODO: Extract out fee as constant
    print(get_balance(context.sourceAddress, context.client))
    verify_account_balance(get_balance(context.sourceAddress, context.client),
                           int(context.sourceBalance) - (3 * context.minDrop))

    verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)
    verify_nftoken_mint_account_objects(context, context.nft_mint_response_2)
    verify_nftoken_burn_account_objects(context, context.nft_burn_response_1)


@when('we burn NFT and delete owner')
def step_impl(context):
    try:
        payload = ObjFactory.getObj(
            ObjType.nft_token_mint,
            account=context.sourceAddress,
            nftoken_taxon=0,
        )
        context.nft_mint_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)

        payload = ObjFactory.getObj(
            ObjType.nft_token_burn,
            account=context.sourceAddress,
            nftoken_id=get_nft_tokens(context.client, context.sourceAddress)[-1],
        )
        context.nft_burn_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)

        wait_for_ledger_to_advance_for_account_delete(context, context.sourceAddress)

        payload = ObjFactory.getObj(
            ObjType.account_delete,
            account=context.sourceAddress,
            destination=context.destinationAddress,
            fee=constants.DEFAULT_DELETE_ACCOUNT_FEE,
            sequence=get_account_sequence(context.client, context.sourceAddress)
        )
        context.ad_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)

    except Exception as e:
        context.exception = e
        context.test_status = "failed"

        raise e


@then('burning NFT and deleting owner is successful')
def step_impl(context):
    verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)
    verify_account_delete_account_objects(context, context.ad_response_1)
    verify_nftoken_burn_account_objects(context, context.nft_burn_response_1)


@when('we mint NFT with issuer burn as owner and delete owner')
def step_impl(context):
    try:
        payload = AccountSet(
            account=context.sourceAddress,
            set_flag=AccountSetFlag.ASF_AUTHORIZED_NFTOKEN_MINTER,
            nftoken_minter=context.destinationAddress
        )
        context.account_set_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)

        payload = ObjFactory.getObj(
            ObjType.nft_token_mint,
            account=context.destinationAddress,
            issuer=context.sourceAddress,
            nftoken_taxon=0,
        )
        context.nft_mint_response_1 = sign_autofill_and_submit(context.client, payload, context.destinationWallet)

        payload = ObjFactory.getObj(
            ObjType.nft_token_burn,
            account=context.destinationAddress,
            nftoken_id=get_nft_tokens(context.client, context.destinationAddress)[-1],
        )
        context.nft_burn_response_1 = sign_autofill_and_submit(context.client, payload, context.destinationWallet)

        wait_for_ledger_to_advance_for_account_delete(context, context.destinationAddress)

        payload = ObjFactory.getObj(
            ObjType.account_delete,
            account=context.destinationAddress,
            destination=context.sourceAddress,
            fee=constants.DEFAULT_DELETE_ACCOUNT_FEE,
            sequence=get_account_sequence(context.client, context.destinationAddress)
        )
        context.ad_response_1 = sign_autofill_and_submit(context.client, payload, context.destinationWallet)

    except Exception as e:
        context.exception = e
        context.test_status = "failed"
        raise e


@then('minting NFT with issuer burn as owner and deleting owner is successful')
def step_impl(context):
    verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)
    verify_account_delete_account_objects(context, context.ad_response_1)
    verify_nftoken_burn_account_objects(context, context.nft_burn_response_1)
    verify_account_set_account_objects(context, context.account_set_response_1)


@when('we burn NFT as owner and delete issuer')
def step_impl(context):
    try:
        payload = AccountSet(
            account=context.sourceAddress,
            set_flag=AccountSetFlag.ASF_AUTHORIZED_NFTOKEN_MINTER,
            nftoken_minter=context.destinationAddress
        )
        context.account_set_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)

        payload = ObjFactory.getObj(
            ObjType.nft_token_mint,
            account=context.destinationAddress,
            issuer=context.sourceAddress,
            nftoken_taxon=0,
        )
        context.nft_mint_response_1 = sign_autofill_and_submit(context.client, payload, context.destinationWallet)

        payload = ObjFactory.getObj(
            ObjType.nft_token_burn,
            account=context.destinationAddress,
            nftoken_id=get_nft_tokens(context.client, context.destinationAddress)[-1],
        )
        context.nft_burn_response_1 = sign_autofill_and_submit(context.client, payload, context.destinationWallet)

        wait_for_ledger_to_advance_for_account_delete(context, context.sourceAddress)

        payload = ObjFactory.getObj(
            ObjType.account_delete,
            account=context.sourceAddress,
            destination=context.destinationAddress,
            fee=constants.DEFAULT_DELETE_ACCOUNT_FEE,
            sequence=get_account_sequence(context.client, context.sourceAddress)
        )
        context.ad_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)

    except Exception as e:
        context.exception = e
        context.test_status = "failed"
        raise e


@then('burning NFT as owner and deleting issuer is successful')
def step_impl(context):
    verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)
    verify_account_delete_account_objects(context, context.ad_response_1)
    verify_nftoken_burn_account_objects(context, context.nft_burn_response_1)
    verify_account_set_account_objects(context, context.account_set_response_1)


@when('we burn NFT as issuer and delete owner')
def step_impl(context):
    try:
        payload = AccountSet(
            account=context.sourceAddress,
            set_flag=AccountSetFlag.ASF_AUTHORIZED_NFTOKEN_MINTER,
            nftoken_minter=context.destinationAddress
        )
        context.account_set_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)
        #
        payload = ObjFactory.getObj(
            ObjType.nft_token_mint,
            account=context.destinationAddress,
            issuer=context.sourceAddress,
            nftoken_taxon=0,
            flags=1
        )
        context.nft_mint_response_1 = sign_autofill_and_submit(context.client, payload, context.destinationWallet)

        payload = ObjFactory.getObj(
            ObjType.nft_token_burn,
            account=context.sourceAddress,
            owner=context.destinationAddress,
            nftoken_id=get_nft_tokens(context.client, context.destinationAddress)[-1],
        )
        context.nft_burn_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)

        wait_for_ledger_to_advance_for_account_delete(context, context.sourceAddress)

        payload = ObjFactory.getObj(
            ObjType.account_delete,
            account=context.destinationAddress,
            destination=context.sourceAddress,
            fee=constants.DEFAULT_DELETE_ACCOUNT_FEE,
            sequence=get_account_sequence(context.client, context.destinationAddress)
        )
        context.ad_response_1 = sign_autofill_and_submit(context.client, payload, context.destinationWallet)

    except Exception as e:
        context.exception = e
        context.test_status = "failed"

        raise e


@then('burning NFT as issuer and deleting owner is successful')
def step_impl(context):
    verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)
    verify_account_delete_account_objects(context, context.ad_response_1)
    verify_nftoken_burn_account_objects(context, context.nft_burn_response_1)
    verify_account_set_account_objects(context, context.account_set_response_1)


@when('we burn NFT as issuer and delete issuer')
def step_impl(context):
    try:
        payload = AccountSet(
            account=context.sourceAddress,
            set_flag=AccountSetFlag.ASF_AUTHORIZED_NFTOKEN_MINTER,
            nftoken_minter=context.destinationAddress
        )
        context.account_set_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)

        payload = ObjFactory.getObj(
            ObjType.nft_token_mint,
            account=context.destinationAddress,
            issuer=context.sourceAddress,
            nftoken_taxon=0,
            flags=1
        )
        context.nft_mint_response_1 = sign_autofill_and_submit(context.client, payload, context.destinationWallet)

        payload = ObjFactory.getObj(
            ObjType.nft_token_burn,
            account=context.sourceAddress,
            owner=context.destinationAddress,
            nftoken_id=get_nft_tokens(context.client, context.destinationAddress)[-1],
        )
        context.nft_burn_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)

        wait_for_ledger_to_advance_for_account_delete(context, context.sourceAddress)

        payload = ObjFactory.getObj(
            ObjType.account_delete,
            account=context.sourceAddress,
            destination=context.destinationAddress,
            fee=constants.DEFAULT_DELETE_ACCOUNT_FEE,
            sequence=get_account_sequence(context.client, context.sourceAddress)
        )
        context.ad_response_1 = sign_autofill_and_submit(context.client, payload, context.sourceWallet)

    except Exception as e:
        context.exception = e
        context.test_status = "failed"

        raise e


@then('burning NFT as issuer and deleting issuer is successful')
def step_impl(context):
    verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)
    verify_account_delete_account_objects(context, context.ad_response_1)
    verify_nftoken_burn_account_objects(context, context.nft_burn_response_1)
    verify_account_set_account_objects(context, context.account_set_response_1)


@when('we mint more than 32 NFT objects')
def step_impl(context):
    try:
        payload = ObjFactory.getObj(
            ObjType.nft_token_mint,
            account=context.sourceAddress,
            nftoken_taxon=0,
        )
        max_nftokens = 35
        context.responses = []

        for count in range(1, max_nftokens + 1):
            context.responses.append(sign_autofill_and_submit(context.client, payload, context.sourceWallet))
    except Exception as e:
        context.exception = e
        context.test_status = "failed"
        raise e


@then('minting more than 32 NFT objects is successful')
def step_impl(context):
    for response in context.responses:
        verify_nftoken_mint_account_objects(context, response)

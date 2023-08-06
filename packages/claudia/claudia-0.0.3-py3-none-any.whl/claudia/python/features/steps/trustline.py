from behave import *
from hamcrest import assert_that, equal_to, contains_string
from xrpl.account import get_balance
from xrpl.models import AccountSet, AccountSetFlag

from features.lib.ObjFactory import ObjFactory, ObjType
from features.steps.common import generate_issued_currency_amount, sign_autofill_and_submit, \
    verify_trustline_account_objects, verify_payment_account_objects, ResponseCode, \
    generate_path_step, verify_offer_create_account_objects, sanitize_args


@when('we send a trustline payment using one currency from Alice to Bob')
def step_impl(context):
    try:
        context.transferAmount = "10000"
        limit_amount = generate_issued_currency_amount(context.transferAmount, context.sourceAddress, "USD")

        trust_set_tx = ObjFactory.getObj(
            "trust_set",
            limit_amount=limit_amount,
            account=context.destinationAddress,
        )
        context.ts_response_1 = sign_autofill_and_submit(context.client, trust_set_tx, context.destinationWallet)
        payment_tx = ObjFactory.getObj(
            ObjType.payment,
            destination=context.destinationAddress,
            account=context.sourceAddress,
            amount=limit_amount
        )
        context.py_response_1 = sign_autofill_and_submit(context.client, payment_tx, context.sourceWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"


@when('we send issued currency payment from Alice to Bob')
def step_impl(context):
    try:
        context.transferAmount = "10000"
        account_set_tx = AccountSet(
            account=context.issuerAddress,
            set_flag=AccountSetFlag.ASF_DEFAULT_RIPPLE,
        )
        sign_autofill_and_submit(context.client, account_set_tx, context.issuerWallet)
        limit_amount = generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD")

        trust_set_tx = ObjFactory.getObj(
            "trust_set",
            account=context.sourceAddress,
            limit_amount=limit_amount
        )
        context.ts_response_1 = sign_autofill_and_submit(context.client, trust_set_tx, context.sourceWallet)

        payment_tx = ObjFactory.getObj(
            ObjType.payment,
            account=context.issuerAddress,
            destination=context.sourceAddress,
            amount=limit_amount
        )
        context.py_response_1 = sign_autofill_and_submit(context.client, payment_tx, context.issuerWallet)

        trust_set_tx = ObjFactory.getObj(
            "trust_set",
            account=context.destinationAddress,
            limit_amount=limit_amount
        )
        context.ts_response_2 = sign_autofill_and_submit(context.client, trust_set_tx, context.destinationWallet)

        payment_tx = ObjFactory.getObj(
            ObjType.payment,
            account=context.sourceAddress,
            destination=context.destinationAddress,
            amount=limit_amount
        )
        context.py_response_2 = sign_autofill_and_submit(context.client, payment_tx, context.sourceWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"


@when('we send issued currency payment without trustline from Alice to Bob')
def step_impl(context):
    try:
        context.transferAmount = "10000"
        account_set_tx = AccountSet(
            account=context.issuerAddress,
            set_flag=AccountSetFlag.ASF_DEFAULT_RIPPLE,
        )
        sign_autofill_and_submit(context.client, account_set_tx, context.issuerWallet)
        limit_amount = generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD")

        trust_set_tx = ObjFactory.getObj(
            "trust_set",
            account=context.sourceAddress,
            limit_amount=limit_amount
        )
        context.ts_response_1 = sign_autofill_and_submit(context.client, trust_set_tx, context.sourceWallet)

        payment_tx = ObjFactory.getObj(
            ObjType.payment,
            account=context.issuerAddress,
            destination=context.sourceAddress,
            amount=limit_amount
        )
        context.py_response_1 = sign_autofill_and_submit(context.client, payment_tx, context.issuerWallet)

        payment_tx = ObjFactory.getObj(
            ObjType.payment,
            account=context.sourceAddress,
            destination=context.destinationAddress,
            amount=limit_amount
        )
        context.py_response_2 = sign_autofill_and_submit(context.client, payment_tx, context.sourceWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"


@when('we send issued currency payment in decimals from Alice to Bob')
def step_impl(context):
    try:
        trust_set_tx = ObjFactory.getObj(
            ObjType.trust_set,
            account=context.destinationAddress,
            limit_amount=generate_issued_currency_amount(context.transferAmount, context.sourceAddress, "USD")
        )
        context.ts_response_1 = sign_autofill_and_submit(context.client, trust_set_tx, context.destinationWallet)
        payment_tx = ObjFactory.getObj(
            ObjType.payment,
            account=context.sourceAddress,
            destination=context.destinationAddress,
            amount=generate_issued_currency_amount("10.5", context.sourceAddress, "USD")
        )
        context.py_response_1 = sign_autofill_and_submit(context.client, payment_tx, context.sourceWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"


@when('we send issued currency payment in non-string decimals from Alice to Bob')
def step_impl(context):
    try:
        trust_set_tx = ObjFactory.getObj(
            ObjType.trust_set,
            account=context.destinationAddress,
            limit_amount=generate_issued_currency_amount(context.transferAmount, context.sourceAddress, "USD")
        )
        context.ts_response_1 = sign_autofill_and_submit(context.client, trust_set_tx, context.destinationWallet)
        payment_tx = ObjFactory.getObj(
            ObjType.payment,
            account=context.sourceAddress,
            destination=context.destinationAddress,
            amount=generate_issued_currency_amount(10.5, context.sourceAddress, "USD")
        )
        context.py_response_1 = sign_autofill_and_submit(context.client, payment_tx, context.sourceWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"


@when('we send issued currency payment from Invalid issuer to Bob')
def step_impl(context):
    try:
        trust_set_tx = ObjFactory.getObj(
            ObjType.trust_set,
            account=context.destinationAddress,
            limit_amount=generate_issued_currency_amount(context.transferAmount, context.invalidAddress, "USD")
        )
        context.ts_response_1 = sign_autofill_and_submit(context.client, trust_set_tx, context.destinationWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"


@when('we send issued currency payment from Alice to Invalid recipient')
def step_impl(context):
    try:
        trust_set_tx = ObjFactory.getObj(
            ObjType.trust_set,
            account=context.invalidAddress,
            limit_amount=generate_issued_currency_amount(context.transferAmount, context.sourceAddress, "USD")
        )
        context.ts_response_1 = sign_autofill_and_submit(context.client, trust_set_tx, context.invalidWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"


@when('we establish trustline with {limit_amount} amount in {currency_code} currency code')
def step_impl(context, limit_amount, currency_code):
    limit_amount = sanitize_args(limit_amount)
    currency_code = sanitize_args(currency_code)
    amount = context.transferAmount if (limit_amount == "default") else limit_amount

    try:
        trust_set_tx = ObjFactory.getObj(
            ObjType.trust_set,
            account=context.destinationAddress,
            limit_amount=generate_issued_currency_amount(amount, context.sourceAddress, currency_code)
        )
        context.ts_response_1 = sign_autofill_and_submit(context.client, trust_set_tx, context.destinationWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"


@when('we establish trustline from Alice to self')
def step_impl(context):
    try:
        trust_set_tx = ObjFactory.getObj(
            ObjType.trust_set,
            account=context.sourceAddress,
            limit_amount=generate_issued_currency_amount(context.transferAmount, context.sourceAddress, "USD")
        )
        context.ts_response_1 = sign_autofill_and_submit(context.client, trust_set_tx, context.sourceWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"


@when('we send issued currency payment with amount more than limit amount from Alice to Bob')
def step_impl(context):
    try:
        trust_set_tx = ObjFactory.getObj(
            ObjType.trust_set,
            account=context.destinationAddress,
            limit_amount=generate_issued_currency_amount(context.transferAmount, context.sourceAddress, "USD")
        )
        context.ts_response_1 = sign_autofill_and_submit(context.client, trust_set_tx, context.destinationWallet)
        payment_tx = ObjFactory.getObj(
            ObjType.payment,
            account=context.sourceAddress,
            destination=context.destinationAddress,
            amount=generate_issued_currency_amount(str(int(context.transferAmount) + 1), context.sourceAddress, "USD")
        )
        context.py_response_1 = sign_autofill_and_submit(context.client, payment_tx, context.sourceWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"


@when('we send cross currency payment using BTC and USD')
def step_impl(context):
    try:
        account_set_tx = AccountSet(
            account=context.issuerAddress,
            set_flag=AccountSetFlag.ASF_DEFAULT_RIPPLE,
        )
        sign_autofill_and_submit(context.client, account_set_tx, context.issuerWallet)

        trust_set_tx_1 = ObjFactory.getObj(
            ObjType.trust_set,
            account=context.carolAddress,
            limit_amount=generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD")
        )
        context.ts_response_1 = sign_autofill_and_submit(context.client, trust_set_tx_1, context.carolWallet)

        trust_set_tx_2 = ObjFactory.getObj(
            ObjType.trust_set,
            account=context.aliceAddress,
            limit_amount=generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "BTC")
        )
        context.ts_response_2 = sign_autofill_and_submit(context.client, trust_set_tx_2, context.aliceWallet)

        payment_tx_1 = ObjFactory.getObj(
            ObjType.payment,
            account=context.issuerAddress,
            destination=context.aliceAddress,
            amount=generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "BTC")
        )
        context.py_response_1 = sign_autofill_and_submit(context.client, payment_tx_1, context.issuerWallet)

        trust_set_tx_3 = ObjFactory.getObj(
            ObjType.trust_set,
            account=context.bobAddress,
            limit_amount=generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD")
        )
        context.ts_response_3 = sign_autofill_and_submit(context.client, trust_set_tx_3, context.bobWallet)

        payment_tx_2 = ObjFactory.getObj(
            ObjType.payment,
            account=context.issuerAddress,
            destination=context.bobAddress,
            amount=generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD")
        )
        context.py_response_2 = sign_autofill_and_submit(context.client, payment_tx_2, context.issuerWallet)

        offer_create_tx_1 = ObjFactory.getObj(
            ObjType.offer_create,
            account=context.bobAddress,
            taker_pays=generate_issued_currency_amount("20", context.issuerAddress, "BTC"),
            taker_gets=generate_issued_currency_amount("20", context.issuerAddress, "USD")
        )

        context.offer_create_response_1 = sign_autofill_and_submit(context.client, offer_create_tx_1, context.bobWallet)

        payment_tx_3 = ObjFactory.getObj(
            ObjType.payment,
            account=context.aliceAddress,
            destination=context.carolAddress,
            amount=generate_issued_currency_amount("20", context.issuerAddress, "USD"),
            paths=[[generate_path_step(context.issuerAddress, "USD")]],
            flags=131072,
            send_max=generate_issued_currency_amount("20", context.issuerAddress, "BTC")
        )
        context.py_response_3 = sign_autofill_and_submit(context.client, payment_tx_3, context.aliceWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"
        raise e


@when('we send cross currency payment using BTC and USD without specifying paths')
def step_impl(context):
    try:
        account_set_tx = AccountSet(
            account=context.issuerAddress,
            set_flag=AccountSetFlag.ASF_DEFAULT_RIPPLE,
        )
        sign_autofill_and_submit(context.client, account_set_tx, context.issuerWallet)

        trust_set_tx_1 = ObjFactory.getObj(
            ObjType.trust_set,
            account=context.carolAddress,
            limit_amount=generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD")
        )
        context.ts_response_1 = sign_autofill_and_submit(context.client, trust_set_tx_1, context.carolWallet)

        trust_set_tx_2 = ObjFactory.getObj(
            ObjType.trust_set,
            account=context.aliceAddress,
            limit_amount=generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "BTC")
        )
        context.ts_response_2 = sign_autofill_and_submit(context.client, trust_set_tx_2, context.aliceWallet)

        payment_tx_1 = ObjFactory.getObj(
            ObjType.payment,
            account=context.issuerAddress,
            destination=context.aliceAddress,
            amount=generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "BTC")
        )
        context.py_response_1 = sign_autofill_and_submit(context.client, payment_tx_1, context.issuerWallet)

        trust_set_tx_3 = ObjFactory.getObj(
            ObjType.trust_set,
            account=context.bobAddress,
            limit_amount=generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD")
        )
        context.ts_response_3 = sign_autofill_and_submit(context.client, trust_set_tx_3, context.bobWallet)

        payment_tx_2 = ObjFactory.getObj(
            ObjType.payment,
            account=context.issuerAddress,
            destination=context.bobAddress,
            amount=generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD")
        )
        context.py_response_2 = sign_autofill_and_submit(context.client, payment_tx_2, context.issuerWallet)

        offer_create_tx_1 = ObjFactory.getObj(
            ObjType.offer_create,
            account=context.bobAddress,
            taker_pays=generate_issued_currency_amount("20", context.issuerAddress, "BTC"),
            taker_gets=generate_issued_currency_amount("20", context.issuerAddress, "USD")
        )
        context.offer_create_response_1 = sign_autofill_and_submit(context.client, offer_create_tx_1, context.bobWallet)

        offer_create_tx_2 = ObjFactory.getObj(
            ObjType.offer_create,
            account=context.aliceAddress,
            taker_pays=generate_issued_currency_amount("20", context.issuerAddress, "USD"),
            taker_gets=generate_issued_currency_amount("20", context.issuerAddress, "BTC")
        )

        context.offer_create_response_2 = sign_autofill_and_submit(context.client, offer_create_tx_2,
                                                                   context.aliceWallet)

        payment_tx_3 = ObjFactory.getObj(
            ObjType.payment,
            account=context.aliceAddress,
            destination=context.carolAddress,
            amount=generate_issued_currency_amount("20", context.issuerAddress, "USD"),
            flags=131072,
            send_max=generate_issued_currency_amount("20", context.issuerAddress, "BTC")
        )
        context.py_response_3 = sign_autofill_and_submit(context.client, payment_tx_3, context.aliceWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"
        raise e


@when('we send cross currency payment using BTC and USD with offer and payment')
def step_impl(context):
    try:
        account_set_tx = AccountSet(
            account=context.issuerAddress,
            set_flag=AccountSetFlag.ASF_DEFAULT_RIPPLE,
        )
        sign_autofill_and_submit(context.client, account_set_tx, context.issuerWallet)

        trust_set_tx_1 = ObjFactory.getObj(
            ObjType.trust_set,
            account=context.carolAddress,
            limit_amount=generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD")
        )
        context.ts_response_1 = sign_autofill_and_submit(context.client, trust_set_tx_1, context.carolWallet)

        trust_set_tx_2 = ObjFactory.getObj(
            ObjType.trust_set,
            account=context.aliceAddress,
            limit_amount=generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "BTC")
        )
        context.ts_response_2 = sign_autofill_and_submit(context.client, trust_set_tx_2, context.aliceWallet)

        payment_tx_1 = ObjFactory.getObj(
            ObjType.payment,
            account=context.issuerAddress,
            destination=context.aliceAddress,
            amount=generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "BTC")
        )
        context.py_response_1 = sign_autofill_and_submit(context.client, payment_tx_1, context.issuerWallet)

        trust_set_tx_3 = ObjFactory.getObj(
            ObjType.trust_set,
            account=context.bobAddress,
            limit_amount=generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD")
        )
        context.ts_response_3 = sign_autofill_and_submit(context.client, trust_set_tx_3, context.bobWallet)

        payment_tx_2 = ObjFactory.getObj(
            ObjType.payment,
            account=context.issuerAddress,
            destination=context.bobAddress,
            amount=generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD")
        )
        context.py_response_2 = sign_autofill_and_submit(context.client, payment_tx_2, context.issuerWallet)

        offer_create_tx_1 = ObjFactory.getObj(
            ObjType.offer_create,
            account=context.bobAddress,
            taker_pays=generate_issued_currency_amount("20", context.issuerAddress, "BTC"),
            taker_gets=generate_issued_currency_amount("20", context.issuerAddress, "USD")
        )

        context.offer_create_response_1 = sign_autofill_and_submit(context.client, offer_create_tx_1, context.bobWallet)

        payment_tx_3 = ObjFactory.getObj(
            ObjType.payment,
            account=context.aliceAddress,
            destination=context.carolAddress,
            amount=generate_issued_currency_amount("20", context.issuerAddress, "USD"),
            flags=131072,
            send_max=generate_issued_currency_amount("20", context.issuerAddress, "BTC")
        )
        context.py_response_3 = sign_autofill_and_submit(context.client, payment_tx_3, context.aliceWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"
        raise e


@when('we send cross currency payment using XRP and USD')
def step_impl(context):
    try:
        account_set_tx = AccountSet(
            account=context.issuerAddress,
            set_flag=AccountSetFlag.ASF_DEFAULT_RIPPLE,
        )
        sign_autofill_and_submit(context.client, account_set_tx, context.issuerWallet)

        trust_set_tx_1 = ObjFactory.getObj(
            ObjType.trust_set,
            account=context.carolAddress,
            limit_amount=generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD")
        )
        context.ts_response_1 = sign_autofill_and_submit(context.client, trust_set_tx_1, context.carolWallet)

        trust_set_tx_2 = ObjFactory.getObj(
            ObjType.trust_set,
            account=context.bobAddress,
            limit_amount=generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD")
        )
        context.ts_response_2 = sign_autofill_and_submit(context.client, trust_set_tx_2, context.bobWallet)

        payment_tx_1 = ObjFactory.getObj(
            ObjType.payment,
            account=context.issuerAddress,
            destination=context.bobAddress,
            amount=generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD")
        )
        context.py_response_1 = sign_autofill_and_submit(context.client, payment_tx_1, context.issuerWallet)

        offer_create_tx_1 = ObjFactory.getObj(
            ObjType.offer_create,
            account=context.bobAddress,
            taker_pays="100",
            taker_gets=generate_issued_currency_amount("20", context.issuerAddress, "USD")
        )
        context.offer_create_response_1 = sign_autofill_and_submit(context.client, offer_create_tx_1, context.bobWallet)

        payment_tx_2 = ObjFactory.getObj(
            ObjType.payment,
            account=context.aliceAddress,
            destination=context.carolAddress,
            amount=generate_issued_currency_amount("20", context.issuerAddress, "USD"),
            paths=[[generate_path_step(context.issuerAddress, "USD")]],
            flags=131072,
            send_max="100"
        )
        context.py_response_2 = sign_autofill_and_submit(context.client, payment_tx_2, context.aliceWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"
        raise e


@when('we send cross currency payment to self using XRP and USD')
def step_impl(context):
    try:
        account_set_tx = AccountSet(
            account=context.issuerAddress,
            set_flag=AccountSetFlag.ASF_DEFAULT_RIPPLE,
        )
        sign_autofill_and_submit(context.client, account_set_tx, context.issuerWallet)

        trust_set_tx_1 = ObjFactory.getObj(
            ObjType.trust_set,
            account=context.aliceAddress,
            limit_amount=generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD")
        )
        context.ts_response_1 = sign_autofill_and_submit(context.client, trust_set_tx_1, context.aliceWallet)

        payment_tx_1 = ObjFactory.getObj(
            ObjType.payment,
            account=context.issuerAddress,
            destination=context.aliceAddress,
            amount=generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD")
        )
        context.py_response_1 = sign_autofill_and_submit(context.client, payment_tx_1, context.issuerWallet)

        offer_create_tx_1 = ObjFactory.getObj(
            ObjType.offer_create,
            account=context.bobAddress,
            taker_pays="35000000",
            taker_gets=generate_issued_currency_amount("20", context.issuerAddress, "USD")
        )
        context.offer_create_response_1 = sign_autofill_and_submit(context.client, offer_create_tx_1, context.bobWallet)

        payment_tx_2 = ObjFactory.getObj(
            ObjType.payment,
            account=context.aliceAddress,
            destination=context.aliceAddress,
            amount="35000000",
            flags=131072,
            send_max=generate_issued_currency_amount("20", context.issuerAddress, "USD")
        )
        context.py_response_2 = sign_autofill_and_submit(context.client, payment_tx_2, context.aliceWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"
        raise e


@when('we send cross currency payment using USD and XRP')
def step_impl(context):
    try:
        account_set_tx = AccountSet(
            account=context.issuerAddress,
            set_flag=AccountSetFlag.ASF_DEFAULT_RIPPLE,
        )
        sign_autofill_and_submit(context.client, account_set_tx, context.issuerWallet)

        trust_set_tx_1 = ObjFactory.getObj(
            ObjType.trust_set,
            account=context.aliceAddress,
            limit_amount=generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD")
        )
        context.ts_response_1 = sign_autofill_and_submit(context.client, trust_set_tx_1, context.aliceWallet)

        payment_tx_1 = ObjFactory.getObj(
            ObjType.payment,
            account=context.issuerAddress,
            destination=context.aliceAddress,
            amount=generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD")
        )
        context.py_response_1 = sign_autofill_and_submit(context.client, payment_tx_1, context.issuerWallet)

        offer_create_tx_1 = ObjFactory.getObj(
            ObjType.offer_create,
            account=context.bobAddress,
            taker_pays=generate_issued_currency_amount("20", context.issuerAddress, "USD"),
            taker_gets="25000000"
        )
        context.offer_create_response_1 = sign_autofill_and_submit(context.client, offer_create_tx_1, context.bobWallet)

        payment_tx_2 = ObjFactory.getObj(
            ObjType.payment,
            account=context.aliceAddress,
            destination=context.carolAddress,
            amount="25000000",
            flags=131072,
            send_max=generate_issued_currency_amount("20", context.issuerAddress, "USD")
        )
        context.py_response_2 = sign_autofill_and_submit(context.client, payment_tx_2, context.aliceWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"
        raise e


@when('we send cross currency payment using USD and XRP without specifying send_max')
def step_impl(context):
    try:
        account_set_tx = AccountSet(
            account=context.issuerAddress,
            set_flag=AccountSetFlag.ASF_DEFAULT_RIPPLE,
        )
        sign_autofill_and_submit(context.client, account_set_tx, context.issuerWallet)

        trust_set_tx_1 = ObjFactory.getObj(
            ObjType.trust_set,
            account=context.aliceAddress,
            limit_amount=generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD")
        )
        context.ts_response_1 = sign_autofill_and_submit(context.client, trust_set_tx_1, context.aliceWallet)

        payment_tx_1 = ObjFactory.getObj(
            ObjType.payment,
            account=context.issuerAddress,
            destination=context.aliceAddress,
            amount=generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD")
        )
        context.py_response_1 = sign_autofill_and_submit(context.client, payment_tx_1, context.issuerWallet)

        offer_create_tx_1 = ObjFactory.getObj(
            ObjType.offer_create,
            account=context.bobAddress,
            taker_pays=generate_issued_currency_amount("20", context.issuerAddress, "USD"),
            taker_gets="25000000"
        )
        context.offer_create_response_1 = sign_autofill_and_submit(context.client, offer_create_tx_1, context.bobWallet)

        payment_tx_2 = ObjFactory.getObj(
            ObjType.payment,
            account=context.aliceAddress,
            destination=context.carolAddress,
            amount="25000000",
            flags=131072,
        )
        context.py_response_2 = sign_autofill_and_submit(context.client, payment_tx_2, context.aliceWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"


@when('we send cross currency payment using BTC, USD and XRP')
def step_impl(context):
    try:
        account_set_tx = AccountSet(
            account=context.issuerAddress,
            set_flag=AccountSetFlag.ASF_DEFAULT_RIPPLE,
        )
        sign_autofill_and_submit(context.client, account_set_tx, context.issuerWallet)

        trust_set_tx_1 = ObjFactory.getObj(
            ObjType.trust_set,
            account=context.carolAddress,
            limit_amount=generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD")
        )
        context.ts_response_1 = sign_autofill_and_submit(context.client, trust_set_tx_1, context.carolWallet)

        trust_set_tx_2 = ObjFactory.getObj(
            ObjType.trust_set,
            account=context.aliceAddress,
            limit_amount=generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "BTC")
        )
        context.ts_response_2 = sign_autofill_and_submit(context.client, trust_set_tx_2, context.aliceWallet)

        payment_tx_1 = ObjFactory.getObj(
            ObjType.payment,
            account=context.issuerAddress,
            destination=context.aliceAddress,
            amount=generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "BTC")
        )
        context.py_response_1 = sign_autofill_and_submit(context.client, payment_tx_1, context.issuerWallet)

        trust_set_tx_3 = ObjFactory.getObj(
            ObjType.trust_set,
            account=context.bobAddress,
            limit_amount=generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD")
        )
        context.ts_response_3 = sign_autofill_and_submit(context.client, trust_set_tx_3, context.bobWallet)

        payment_tx_2 = ObjFactory.getObj(
            ObjType.payment,
            account=context.issuerAddress,
            destination=context.bobAddress,
            amount=generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD")
        )
        context.py_response_2 = sign_autofill_and_submit(context.client, payment_tx_2, context.issuerWallet)

        offer_create_tx_1 = ObjFactory.getObj(
            ObjType.offer_create,
            account=context.bobAddress,
            taker_pays="100",
            taker_gets=generate_issued_currency_amount("20", context.issuerAddress, "USD")
        )
        context.offer_create_response_1 = sign_autofill_and_submit(context.client, offer_create_tx_1, context.bobWallet)

        offer_create_tx_2 = ObjFactory.getObj(
            ObjType.offer_create,
            account=context.bobAddress,
            taker_pays=generate_issued_currency_amount("20", context.issuerAddress, "BTC"),
            taker_gets="100"
        )
        context.offer_create_response_2 = sign_autofill_and_submit(context.client, offer_create_tx_2, context.bobWallet)
        payment_tx_2 = ObjFactory.getObj(
            ObjType.payment,
            account=context.aliceAddress,
            destination=context.carolAddress,
            amount=generate_issued_currency_amount("20", context.issuerAddress, "USD"),
            paths=[[generate_path_step(currency="USD")], [generate_path_step(context.issuerAddress, "USD")]],
            flags=131072,
            send_max=generate_issued_currency_amount("20", context.issuerAddress, "BTC")
        )
        context.py_response_3 = sign_autofill_and_submit(context.client, payment_tx_2, context.aliceWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"


@when('we send cross currency payment using BTC, USD and XRP without specifying paths')
def step_impl(context):
    try:
        account_set_tx = AccountSet(
            account=context.issuerAddress,
            set_flag=AccountSetFlag.ASF_DEFAULT_RIPPLE,
        )
        sign_autofill_and_submit(context.client, account_set_tx, context.issuerWallet)

        trust_set_tx_1 = ObjFactory.getObj(
            ObjType.trust_set,
            account=context.carolAddress,
            limit_amount=generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD")
        )
        context.ts_response_1 = sign_autofill_and_submit(context.client, trust_set_tx_1, context.carolWallet)

        trust_set_tx_2 = ObjFactory.getObj(
            ObjType.trust_set,
            account=context.aliceAddress,
            limit_amount=generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "BTC")
        )
        context.ts_response_2 = sign_autofill_and_submit(context.client, trust_set_tx_2, context.aliceWallet)

        payment_tx_1 = ObjFactory.getObj(
            ObjType.payment,
            account=context.issuerAddress,
            destination=context.aliceAddress,
            amount=generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "BTC")
        )
        context.py_response_1 = sign_autofill_and_submit(context.client, payment_tx_1, context.issuerWallet)

        trust_set_tx_3 = ObjFactory.getObj(
            ObjType.trust_set,
            account=context.bobAddress,
            limit_amount=generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD")
        )
        context.ts_response_3 = sign_autofill_and_submit(context.client, trust_set_tx_3, context.bobWallet)

        payment_tx_2 = ObjFactory.getObj(
            ObjType.payment,
            account=context.issuerAddress,
            destination=context.bobAddress,
            amount=generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD")
        )
        context.py_response_2 = sign_autofill_and_submit(context.client, payment_tx_2, context.issuerWallet)

        offer_create_tx_1 = ObjFactory.getObj(
            ObjType.offer_create,
            account=context.bobAddress,
            taker_pays="100",
            taker_gets=generate_issued_currency_amount("20", context.issuerAddress, "USD")
        )
        context.offer_create_response_1 = sign_autofill_and_submit(context.client, offer_create_tx_1, context.bobWallet)

        offer_create_tx_2 = ObjFactory.getObj(
            ObjType.offer_create,
            account=context.bobAddress,
            taker_pays=generate_issued_currency_amount("20", context.issuerAddress, "BTC"),
            taker_gets="100"
        )
        context.offer_create_response_2 = sign_autofill_and_submit(context.client, offer_create_tx_2, context.bobWallet)
        payment_tx_2 = ObjFactory.getObj(
            ObjType.payment,
            account=context.aliceAddress,
            destination=context.carolAddress,
            amount=generate_issued_currency_amount("20", context.issuerAddress, "USD"),
            flags=131072,
            send_max=generate_issued_currency_amount("20", context.issuerAddress, "BTC")
        )
        context.py_response_3 = sign_autofill_and_submit(context.client, payment_tx_2, context.aliceWallet)
    except Exception as e:
        context.exception = e
        context.test_status = "failed"


@then('trustline payment using one currency is successful')
def step_impl(context):
    assert get_balance(context.sourceAddress, context.client) == (
            int(context.sourceBalance) - int(context.minDrop)), \
        "Source account balance is incorrect"
    assert get_balance(context.destinationAddress, context.client) == (
            int(context.destinationBalance) - int(context.minDrop)), "Destination account balance is incorrect"

    verify_trustline_account_objects(context, context.ts_response_1)

    verify_payment_account_objects(context, context.py_response_1)


@then('issued currency payment is successful')
def step_impl(context):
    assert get_balance(context.issuerAddress, context.client) == (
            int(context.issuerBalance) - int(context.minDrop) - int(context.minDrop)), \
        "Issuer account balance is incorrect"
    assert get_balance(context.sourceAddress, context.client) == (
            int(context.sourceBalance) - int(context.minDrop) - int(context.minDrop)), \
        "Source account balance is incorrect"
    assert get_balance(context.destinationAddress, context.client) == (
            int(context.destinationBalance) - int(context.minDrop)), "Destination account balance is incorrect"

    verify_trustline_account_objects(context, context.ts_response_1)
    verify_payment_account_objects(context, context.py_response_1)
    verify_trustline_account_objects(context, context.ts_response_2)
    verify_payment_account_objects(context, context.py_response_2)


@then('issued currency payment without trustline is not successful')
def step_impl(context):
    assert get_balance(context.issuerAddress, context.client) == (
            int(context.issuerBalance) - int(context.minDrop) - int(context.minDrop)), \
        "Issuer account balance is incorrect"
    assert get_balance(context.sourceAddress, context.client) == (
            int(context.sourceBalance) - int(context.minDrop) - int(context.minDrop)), \
        "Source account balance is incorrect"
    assert get_balance(context.destinationAddress, context.client) == (
        int(context.destinationBalance)), "Destination account balance is incorrect"

    verify_trustline_account_objects(context, context.ts_response_1)
    verify_payment_account_objects(context, context.py_response_1)
    verify_payment_account_objects(context, context.py_response_2, ResponseCode.path_dry)


@then('issued currency payment in decimal is successful')
def step_impl(context):
    assert get_balance(context.sourceAddress, context.client) == (
            int(context.sourceBalance) - int(context.minDrop)), \
        "Source account balance is incorrect"
    assert get_balance(context.destinationAddress, context.client) == (
            int(context.destinationBalance) - int(context.minDrop)), "Destination account balance is incorrect"
    verify_trustline_account_objects(context, context.ts_response_1)

    verify_payment_account_objects(context, context.py_response_1)


@then('issued currency payment in non-string decimal is successful')
def step_impl(context):
    assert get_balance(context.sourceAddress, context.client) == (
            int(context.sourceBalance) - int(context.minDrop)), \
        "Source account balance is incorrect"
    assert get_balance(context.destinationAddress, context.client) == (
            int(context.destinationBalance) - int(context.minDrop)), "Destination account balance is incorrect"
    verify_trustline_account_objects(context, context.ts_response_1)

    verify_payment_account_objects(context, context.py_response_1)


@then('issued currency payment from Invalid issuer is not successful')
def step_impl(context):
    assert get_balance(context.destinationAddress, context.client) == (int(context.destinationBalance)), \
        "Destination account balance is incorrect"

    assert_that(context.test_status, equal_to("failed"), "Test Status is incorrect")
    assert_that(str(context.exception),
                contains_string("Invalid value to construct an AccountID: expected valid classic address or "
                                "X-Address, received str."),
                "Incorrect error message received.")


@then('issued currency payment to invalid recipient is not successful')
def step_impl(context):
    assert get_balance(context.sourceAddress, context.client) == (int(context.sourceBalance)), \
        "Source account balance is incorrect"

    assert_that(context.test_status, equal_to("failed"), "Test Status is incorrect")
    assert_that(str(context.exception),
                contains_string("Request failed, actNotFound: Account not found."),
                "Incorrect error message received.")


@then('trustline creation with invalid currency code --- fails')
def step_impl(context):
    assert get_balance(context.sourceAddress, context.client) == (int(context.sourceBalance)), \
        "Source account balance is incorrect"
    assert get_balance(context.destinationAddress, context.client) == (
        int(context.destinationBalance)), "Destination account balance is incorrect"

    assert_that(context.test_status, equal_to("failed"), "Test Status is incorrect")
    assert_that(str(context.exception), contains_string("Invalid currency"))


@then('trustline creation with invalid currency code USDX fails')
def step_impl(context):
    assert get_balance(context.sourceAddress, context.client) == (int(context.sourceBalance)), \
        "Source account balance is incorrect"
    assert get_balance(context.destinationAddress, context.client) == (
        int(context.destinationBalance)), "Destination account balance is incorrect"
    assert_that(context.test_status, equal_to("failed"), "Test Status is incorrect")
    assert_that(str(context.exception), contains_string("Invalid currency"))


@then('trustline creation with invalid currency code XRP fails')
def step_impl(context):
    assert get_balance(context.sourceAddress, context.client) == (int(context.sourceBalance)), \
        "Source account balance is incorrect"
    assert get_balance(context.destinationAddress, context.client) == (
        int(context.destinationBalance)), "Destination account balance is incorrect"

    assert_that(context.test_status, equal_to("failed"), "Test Status is incorrect")
    assert_that(str(context.exception), contains_string('Currency must not be XRP for issued currency'))


@then('trustline creation with non-standard currency code is successful')
def step_impl(context):
    print(get_balance(context.destinationAddress, context.client))
    print(int(context.destinationBalance))
    assert get_balance(context.sourceAddress, context.client) == (int(context.sourceBalance)), \
        "Source account balance is incorrect"
    assert get_balance(context.destinationAddress, context.client) == (
            int(context.destinationBalance) - int(context.minDrop)), "Destination account balance is incorrect"

    verify_trustline_account_objects(context, context.ts_response_1)


@then('trustline creation to self is not successful')
def step_impl(context):
    assert get_balance(context.sourceAddress, context.client) == (int(context.sourceBalance)), \
        "Source account balance is incorrect"

    assert_that(context.test_status, equal_to("failed"), "Test Status is incorrect")
    assert_that(str(context.exception),
                contains_string("Destination may not be source."))


@then('trustline creation with negative limit amount is not successful')
def step_impl(context):
    assert get_balance(context.sourceAddress, context.client) == (int(context.sourceBalance)), \
        "Source account balance is incorrect"
    assert get_balance(context.destinationAddress, context.client) == (
        int(context.destinationBalance)), "Destination account balance is incorrect"

    assert_that(context.test_status, equal_to("failed"), "Test Status is incorrect")
    assert_that(str(context.exception),
                contains_string("Limits must be non-negative."))


@then('trustline creation with invalid limit amount fails with {error_message} error message')
def step_impl(context, error_message):
    error_message = sanitize_args(error_message)
    assert get_balance(context.sourceAddress, context.client) == (int(context.sourceBalance)), \
        "Source account balance is incorrect"
    assert get_balance(context.destinationAddress, context.client) == (
        int(context.destinationBalance)), "Destination account balance is incorrect"

    assert_that(context.test_status, equal_to("failed"), "Test Status is incorrect")
    assert_that(str(context.exception),
                contains_string(error_message))


@then('trustline creation with zero limit amount is not successful')
def step_impl(context):
    assert get_balance(context.sourceAddress, context.client) == (int(context.sourceBalance)), \
        "Source account balance is incorrect"
    assert get_balance(context.destinationAddress, context.client) == (
            int(context.destinationBalance) - int(context.minDrop)), "Destination account balance is incorrect"

    verify_trustline_account_objects(context, context.ts_response_1, ResponseCode.no_line_redundant)


@then('issued currency payment with amount more than limit amount recipient is not successful')
def step_impl(context):
    assert get_balance(context.sourceAddress, context.client) == (int(context.sourceBalance) - int(context.minDrop)), \
        "Source account balance is incorrect"
    assert get_balance(context.destinationAddress, context.client) == (
            int(context.destinationBalance) - int(context.minDrop)), "Destination account balance is incorrect"

    verify_trustline_account_objects(context, context.ts_response_1)
    verify_trustline_account_objects(context, context.py_response_1, ResponseCode.path_partial)


@then('cross currency payment using BTC and USD is successful')
def step_impl(context):
    assert get_balance(context.aliceAddress, context.client) == (
            int(context.aliceBalance) - int(context.minDrop) - int(context.minDrop)), \
        "Alice account balance is incorrect"
    assert get_balance(context.bobAddress, context.client) == (
            int(context.bobBalance) - int(context.minDrop) - int(context.minDrop)), \
        "Bob account balance is incorrect"
    assert get_balance(context.carolAddress, context.client) == (
            int(context.carolBalance) - int(context.minDrop)), "Carol account balance is incorrect"

    verify_trustline_account_objects(context, context.ts_response_1)
    verify_trustline_account_objects(context, context.ts_response_2)
    verify_trustline_account_objects(context, context.ts_response_3)

    verify_payment_account_objects(context, context.py_response_1)
    verify_payment_account_objects(context, context.py_response_2)
    verify_payment_account_objects(context, context.py_response_3)

    verify_offer_create_account_objects(context, context.offer_create_response_1, offer_crossing=True)


@then('cross currency payment using BTC and USD without specifying paths is successful')
def step_impl(context):
    assert get_balance(context.aliceAddress, context.client) == (
            int(context.aliceBalance) - int(context.minDrop) - int(context.minDrop) - int(context.minDrop)), \
        "Alice account balance is incorrect"
    assert get_balance(context.bobAddress, context.client) == (
            int(context.bobBalance) - int(context.minDrop) - int(context.minDrop)), \
        "Bob account balance is incorrect"
    assert get_balance(context.carolAddress, context.client) == (
            int(context.carolBalance) - int(context.minDrop)), "Carol account balance is incorrect"

    verify_trustline_account_objects(context, context.ts_response_1)
    verify_trustline_account_objects(context, context.ts_response_2)
    verify_trustline_account_objects(context, context.ts_response_3)

    verify_payment_account_objects(context, context.py_response_1)
    verify_payment_account_objects(context, context.py_response_2)
    verify_payment_account_objects(context, context.py_response_3, ResponseCode.path_dry)

    verify_offer_create_account_objects(context, context.offer_create_response_1, offer_crossing=True)
    verify_offer_create_account_objects(context, context.offer_create_response_2)


@then('cross currency payment using BTC and USD with offer and payment is successful')
def step_impl(context):
    assert get_balance(context.aliceAddress, context.client) == (
            int(context.aliceBalance) - int(context.minDrop) - int(context.minDrop)), \
        "Alice account balance is incorrect"
    assert get_balance(context.bobAddress, context.client) == (
            int(context.bobBalance) - int(context.minDrop) - int(context.minDrop)), \
        "Bob account balance is incorrect"
    assert get_balance(context.carolAddress, context.client) == (
            int(context.carolBalance) - int(context.minDrop)), "Carol account balance is incorrect"

    verify_trustline_account_objects(context, context.ts_response_1)
    verify_trustline_account_objects(context, context.ts_response_2)
    verify_trustline_account_objects(context, context.ts_response_3)
    verify_payment_account_objects(context, context.py_response_1)
    verify_payment_account_objects(context, context.py_response_2)
    verify_payment_account_objects(context, context.py_response_3)

    verify_offer_create_account_objects(context, context.offer_create_response_1, offer_crossing=True)


@then('cross currency payment using XRP and USD is successful')
def step_impl(context):
    assert get_balance(context.aliceAddress, context.client) == (
            int(context.aliceBalance) - int(context.minDrop) - 100), \
        "Alice account balance is incorrect"
    assert get_balance(context.bobAddress, context.client) == (
            int(context.bobBalance) + (8 * int(context.minDrop))), \
        "Bob account balance is incorrect"
    assert get_balance(context.carolAddress, context.client) == (
            int(context.carolBalance) - int(context.minDrop)), "Carol account balance is incorrect"

    verify_trustline_account_objects(context, context.ts_response_1)
    verify_trustline_account_objects(context, context.ts_response_2)
    verify_payment_account_objects(context, context.py_response_1)
    verify_payment_account_objects(context, context.py_response_2)

    verify_offer_create_account_objects(context, context.offer_create_response_1, offer_crossing=True)


@then('cross currency payment to self using XRP and USD is not successful')
def step_impl(context):
    verify_trustline_account_objects(context, context.ts_response_1)

    verify_payment_account_objects(context, context.py_response_1)

    verify_payment_account_objects(context, context.py_response_2, ResponseCode.path_dry)

    verify_offer_create_account_objects(context, context.offer_create_response_1, offer_crossing=True,
                                        engine_result=ResponseCode.unfunded_offer)


@then('cross currency payment using USD and XRP is successful')
def step_impl(context):
    assert get_balance(context.aliceAddress, context.client) == (
            int(context.aliceBalance) - int(context.minDrop) - int(context.minDrop)), \
        "Alice account balance is incorrect"
    assert get_balance(context.bobAddress, context.client) == (
            int(context.bobBalance) - int(context.minDrop) - 25000000), \
        "Bob account balance is incorrect"
    assert get_balance(context.carolAddress, context.client) == (
            int(context.carolBalance) + 25000000), "Carol account balance is incorrect"

    verify_trustline_account_objects(context, context.ts_response_1)

    verify_payment_account_objects(context, context.py_response_1)
    verify_payment_account_objects(context, context.py_response_2)

    verify_offer_create_account_objects(context, context.offer_create_response_1, offer_crossing=True)


@then('cross currency payment using USD and XRP without specifying send_max fails')
def step_impl(context):
    error_message = "Partial payment is not allowed for XRP to XRP"
    assert_that(context.test_status, equal_to("failed"), "Test Status is incorrect")
    assert_that(str(context.exception), contains_string(error_message))

    assert get_balance(context.aliceAddress, context.client) == (
            int(context.aliceBalance) - int(context.minDrop)), \
        "Alice account balance is incorrect"
    assert get_balance(context.bobAddress, context.client) == (
            int(context.bobBalance) - int(context.minDrop)), \
        "Bob account balance is incorrect"
    assert get_balance(context.carolAddress, context.client) == (
        int(context.carolBalance)), "Carol account balance is incorrect"

    verify_trustline_account_objects(context, context.ts_response_1)
    verify_payment_account_objects(context, context.py_response_1)
    verify_offer_create_account_objects(context, context.offer_create_response_1)


@then('cross currency payment using BTC, USD and XRP is successful')
def step_impl(context):
    assert get_balance(context.aliceAddress, context.client) == (
            int(context.aliceBalance) - (2 * int(context.minDrop))), \
        "Alice account balance is incorrect"
    assert get_balance(context.bobAddress, context.client) == (
            int(context.bobBalance) - (3 * int(context.minDrop))), \
        "Bob account balance is incorrect"
    assert get_balance(context.carolAddress, context.client) == (
            int(context.carolBalance) - int(context.minDrop)), \
        "Carol account balance is incorrect"

    verify_trustline_account_objects(context, context.ts_response_1)
    verify_trustline_account_objects(context, context.ts_response_2)

    verify_payment_account_objects(context, context.py_response_1)
    verify_payment_account_objects(context, context.py_response_2)

    verify_offer_create_account_objects(context, context.offer_create_response_1)
    verify_offer_create_account_objects(context, context.offer_create_response_2)


@then('cross currency payment using BTC, USD and XRP without specifying paths is not successful')
def step_impl(context):
    assert get_balance(context.aliceAddress, context.client) == (
            int(context.aliceBalance) - (2 * int(context.minDrop))), \
        "Alice account balance is incorrect"
    assert get_balance(context.bobAddress, context.client) == (
            int(context.bobBalance) - (3 * int(context.minDrop))), \
        "Bob account balance is incorrect"
    assert get_balance(context.carolAddress, context.client) == (
            int(context.carolBalance) - int(context.minDrop)), "Carol account balance is incorrect"

    verify_trustline_account_objects(context, context.ts_response_1)
    verify_trustline_account_objects(context, context.ts_response_2)
    verify_trustline_account_objects(context, context.ts_response_3)

    verify_payment_account_objects(context, context.py_response_1)
    verify_payment_account_objects(context, context.py_response_2)
    verify_payment_account_objects(context, context.py_response_3, ResponseCode.path_dry)

    verify_offer_create_account_objects(context, context.offer_create_response_1)
    verify_offer_create_account_objects(context, context.offer_create_response_2)

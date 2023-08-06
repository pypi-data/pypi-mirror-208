const {When, Then} = require('@cucumber/cucumber')
const xrpl = require("xrpl");
const {AccountSetAsfFlags, PaymentFlags} = require("xrpl");
const {} = require('../context.js');
let context = require('../context.js');
const assert = require('assert');
const ObjFactory = require("../lib/ObjFactory");
const ObjType = require("../lib/ObjFactory");
const {
    sign_autofill_and_submit,
    verify_account_balance,
    verify_payment_account_objects,
    ResponseCode,
    get_account_balance,
    generate_issued_currency_amount,
    generate_path_step,
    verify_trustline_account_objects,
    verify_test_status,
    verify_test_error_message,
    verify_offer_create_account_objects,
} = require("./common");


When('we send a trustline payment using one currency from Alice to Bob', {timeout: 180000}, async () => {
    try {
        let limit_amount = await generate_issued_currency_amount(
            value = context.transferAmount,
            issuer = context.sourceAddress,
            currency = "USD"
        )

        let payload = ObjFactory.getObj(
            "trustset",
            {
                "Account": context.destinationAddress,
                "LimitAmount": limit_amount,
            });
        context.ts_response_1 = await sign_autofill_and_submit(context, payload, context.destinationWallet)

        payload = ObjFactory.getObj(
            "payment",
            {
                "Destination": context.destinationAddress,
                "Account": context.sourceAddress,
                "Amount": limit_amount,
            });
        context.py_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
        throw error
    }
})

When('we send issued currency payment from Alice to Bob', {timeout: 180000}, async () => {
    try {
        let payload = ObjFactory.getObj(
            ObjFactory.ObjType.AccountSet,
            {
                "Account": context.issuerAddress,
                "SetFlag": AccountSetAsfFlags.asfDefaultRipple,
            });
        await sign_autofill_and_submit(context, payload, context.issuerWallet)

        let limit_amount = await generate_issued_currency_amount(
            value = context.transferAmount,
            issuer = context.issuerAddress,
            currency = "USD"
        )

        payload = ObjFactory.getObj(
            "trustset",
            {
                "Account": context.sourceAddress,
                "LimitAmount": limit_amount,
            });
        context.ts_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)

        payload = ObjFactory.getObj(
            "payment",
            {
                "Account": context.issuerAddress,
                "Destination": context.sourceAddress,
                "Amount": limit_amount,
            });
        context.py_response_1 = await sign_autofill_and_submit(context, payload, context.issuerWallet)

        payload = ObjFactory.getObj(
            "trustset",
            {
                "Account": context.destinationAddress,
                "LimitAmount": limit_amount,
            });
        context.ts_response_2 = await sign_autofill_and_submit(context, payload, context.destinationWallet)

        payload = ObjFactory.getObj(
            "payment",
            {
                "Account": context.sourceAddress,
                "Destination": context.destinationAddress,
                "Amount": limit_amount,
            });
        context.py_response_2 = await sign_autofill_and_submit(context, payload, context.sourceWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
    }
})

When('we send issued currency payment without trustline from Alice to Bob', {timeout: 180000}, async () => {
    try {
        let payload = ObjFactory.getObj(
            ObjFactory.ObjType.AccountSet,
            {
                "Account": context.issuerAddress,
                "SetFlag": AccountSetAsfFlags.asfDefaultRipple,
            });
        await sign_autofill_and_submit(context, payload, context.issuerWallet)

        let limit_amount = await generate_issued_currency_amount(
            value = context.transferAmount,
            issuer = context.issuerAddress,
            currency = "USD"
        )

        payload = ObjFactory.getObj(
            "trustset",
            {
                "Account": context.sourceAddress,
                "LimitAmount": limit_amount,
            });
        context.ts_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)

        payload = ObjFactory.getObj(
            "payment",
            {
                "Account": context.issuerAddress,
                "Destination": context.sourceAddress,
                "Amount": limit_amount,
            });
        context.py_response_1 = await sign_autofill_and_submit(context, payload, context.issuerWallet)

        payload = ObjFactory.getObj(
            "payment",
            {
                "Account": context.sourceAddress,
                "Destination": context.destinationAddress,
                "Amount": limit_amount,
            });
        context.py_response_2 = await sign_autofill_and_submit(context, payload, context.sourceWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
    }
})

When('we send issued currency payment in decimals from Alice to Bob', {timeout: 180000}, async () => {
    try {
        let limit_amount = await generate_issued_currency_amount(
            value = context.transferAmount,
            issuer = context.sourceAddress,
            currency = "USD"
        )

        let payload = ObjFactory.getObj(
            "trustset",
            {
                "Account": context.destinationAddress,
                "LimitAmount": limit_amount,
            });
        context.ts_response_1 = await sign_autofill_and_submit(context, payload, context.destinationWallet)

        payload = ObjFactory.getObj(
            "payment",
            {
                "Destination": context.destinationAddress,
                "Account": context.sourceAddress,
                "Amount": await generate_issued_currency_amount(
                    value = "10.5",
                    issuer = context.sourceAddress,
                    currency = "USD"
                ),
            });
        context.py_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
    }
})

When('we send issued currency payment in non-string decimals from Alice to Bob', {timeout: 180000}, async () => {
    // This test may not be possible with JS client. JS Lib does not allow non-string input. Returning early
    return
    // try {
    //
    //     let limit_amount = await generate_issued_currency_amount(
    //         value = context.transferAmount,
    //         issuer = context.sourceAddress,
    //         currency = "USD"
    //     )
    //
    //     let payload = ObjFactory.getObj(
    //         "trustset",
    //         {
    //             "Account": context.destinationAddress,
    //             "LimitAmount": limit_amount,
    //         });
    //
    //     context.ts_response_1 = await sign_autofill_and_submit(context, payload, context.destinationWallet)
    //
    //     payload = ObjFactory.getObj(
    //         "payment",
    //         {
    //             "Destination": context.destinationAddress,
    //             "Account": context.sourceAddress,
    //             "Amount": await generate_issued_currency_amount(
    //                 value = 10.5,
    //                 issuer = context.sourceAddress,
    //                 currency = "USD"
    //             ),
    //         });
    //     context.py_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)
    // } catch (error) {
    //     context.exception = error
    //     context.testStatus = "failed"
    //     console.log("Error was thrown... Error:\n" + error.toString())
    //
    // }
})

When('we send issued currency payment from Invalid issuer to Bob', {timeout: 180000}, async () => {
    try {
        let limit_amount = await generate_issued_currency_amount(
            value = context.transferAmount,
            issuer = context.invalidAddress,
            currency = "USD"
        )

        let payload = ObjFactory.getObj(
            "trustset",
            {
                "Account": context.destinationAddress,
                "LimitAmount": limit_amount,
            });

        context.ts_response_1 = await sign_autofill_and_submit(context, payload, context.destinationWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"

    }
})

When('we send issued currency payment from Alice to Invalid recipient', {timeout: 180000}, async () => {
    try {
        let limit_amount = await generate_issued_currency_amount(
            value = context.transferAmount,
            issuer = context.sourceAddress,
            currency = "USD"
        )

        let payload = ObjFactory.getObj(
            "trustset",
            {
                "Account": context.invalidAddress,
                "LimitAmount": limit_amount,
            });
        context.ts_response_1 = await sign_autofill_and_submit(context, payload, context.invalidWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
    }
})

When('we establish trustline with {string} amount in {string} currency code', {timeout: 180000}, async function (limit_amount, currency_code) {
    try {
        if (limit_amount !== "default") {
            context.transferAmount = limit_amount
        }
        limit_amount = await generate_issued_currency_amount(
            value = context.transferAmount,
            issuer = context.sourceAddress,
            currency = currency_code
        )

        let payload = ObjFactory.getObj(
            "trustset",
            {
                "Account": context.destinationAddress,
                "LimitAmount": limit_amount
            });

        context.ts_response_1 = await sign_autofill_and_submit(context, payload, context.destinationWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
    }
})

When('we establish trustline from Alice to self', {timeout: 180000}, async () => {
    try {
        let payload = ObjFactory.getObj(
            "trustset",
            {
                "Account": context.sourceAddress,
                "LimitAmount": await generate_issued_currency_amount(
                    value = context.transferAmount,
                    issuer = context.sourceAddress,
                    currency = "USD"
                )
            });

        context.ts_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"

    }
})

When('we send issued currency payment with amount more than limit amount from Alice to Bob', {timeout: 180000}, async () => {
    try {
        let payload = ObjFactory.getObj(
            "trustset",
            {
                "Account": context.destinationAddress,
                "LimitAmount": await generate_issued_currency_amount(
                    value = context.transferAmount,
                    issuer = context.sourceAddress,
                    currency = "USD"
                ),
            });
        context.ts_response_1 = await sign_autofill_and_submit(context, payload, context.destinationWallet)

        payload = ObjFactory.getObj(
            "payment",
            {
                "Destination": context.destinationAddress,
                "Account": context.sourceAddress,
                "Amount": await generate_issued_currency_amount(
                    value = (parseInt(context.transferAmount) + 1).toString(),
                    issuer = context.sourceAddress,
                    currency = "USD"
                ),
            });
        context.py_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"

    }
})

When('we send cross currency payment using BTC and USD', {timeout: 180000}, async () => {
    try {
        let payload = ObjFactory.getObj(
            ObjFactory.ObjType.AccountSet,
            {
                "Account": context.issuerAddress,
                "SetFlag": AccountSetAsfFlags.asfDefaultRipple,
            });
        await sign_autofill_and_submit(context, payload, context.issuerWallet)

        payload = ObjFactory.getObj(
            "trustset",
            {
                "Account": context.carolAddress,
                "LimitAmount": await generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD")
            });
        context.ts_response_1 = await sign_autofill_and_submit(context, payload, context.carolWallet)

        payload = ObjFactory.getObj(
            "trustset",
            {
                "Account": context.aliceAddress,
                "LimitAmount": await generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "BTC")
            });
        context.ts_response_2 = await sign_autofill_and_submit(context, payload, context.aliceWallet)

        payload = ObjFactory.getObj(
            "payment",
            {
                "Account": context.issuerAddress,
                "Destination": context.aliceAddress,
                "Amount": await generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "BTC"),
            });
        context.py_response_1 = await sign_autofill_and_submit(context, payload, context.issuerWallet)

        payload = ObjFactory.getObj(
            "trustset",
            {
                "Account": context.bobAddress,
                "LimitAmount": await generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD"),
            });
        context.ts_response_3 = await sign_autofill_and_submit(context, payload, context.bobWallet)

        payload = ObjFactory.getObj(
            "payment",
            {
                "Account": context.issuerAddress,
                "Destination": context.bobAddress,
                "Amount": await generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD"),
            });
        context.py_response_2 = await sign_autofill_and_submit(context, payload, context.issuerWallet)

        payload = ObjFactory.getObj(
            "offercreate",
            {
                "Account": context.bobAddress,
                "TakerPays": await generate_issued_currency_amount("20", context.issuerAddress, "BTC"),
                "TakerGets": await generate_issued_currency_amount("20", context.issuerAddress, "USD")
            }
        )
        context.offer_create_response_1 = await sign_autofill_and_submit(context, payload, context.bobWallet)

        payload = ObjFactory.getObj(
            "payment",
            {
                "Account": context.aliceAddress,
                "Destination": context.carolAddress,
                "Amount": await generate_issued_currency_amount("20", context.issuerAddress, "USD"),
                "Paths": [[await generate_path_step(context.issuerAddress, "USD")]],
                "Flags": PaymentFlags.tfPartialPayment,
                "SendMax": await generate_issued_currency_amount("20", context.issuerAddress, "BTC")
            });
        context.py_response_3 = await sign_autofill_and_submit(context, payload, context.aliceWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"

    }
})

When('we send cross currency payment using BTC and USD without specifying paths', {timeout: 180000}, async () => {
    try {
        let payload = ObjFactory.getObj(
            ObjFactory.ObjType.AccountSet,
            {
                "Account": context.issuerAddress,
                "SetFlag": AccountSetAsfFlags.asfDefaultRipple,
            });
        await sign_autofill_and_submit(context, payload, context.issuerWallet)

        payload = ObjFactory.getObj(
            "trustset",
            {
                "Account": context.carolAddress,
                "LimitAmount": await generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD")
            });
        context.ts_response_1 = await sign_autofill_and_submit(context, payload, context.carolWallet)

        payload = ObjFactory.getObj(
            "trustset",
            {
                "Account": context.aliceAddress,
                "LimitAmount": await generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "BTC")
            });
        context.ts_response_2 = await sign_autofill_and_submit(context, payload, context.aliceWallet)

        payload = ObjFactory.getObj(
            "payment",
            {
                "Account": context.issuerAddress,
                "Destination": context.aliceAddress,
                "Amount": await generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "BTC"),
            });
        context.py_response_1 = await sign_autofill_and_submit(context, payload, context.issuerWallet)

        payload = ObjFactory.getObj(
            "trustset",
            {
                "Account": context.bobAddress,
                "LimitAmount": await generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD"),
            });
        context.ts_response_3 = await sign_autofill_and_submit(context, payload, context.bobWallet)

        payload = ObjFactory.getObj(
            "payment",
            {
                "Account": context.issuerAddress,
                "Destination": context.bobAddress,
                "Amount": await generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD"),
            });
        context.py_response_2 = await sign_autofill_and_submit(context, payload, context.issuerWallet)

        payload = ObjFactory.getObj(
            "offercreate",
            {
                "Account": context.bobAddress,
                "TakerPays": await generate_issued_currency_amount("20", context.issuerAddress, "BTC"),
                "TakerGets": await generate_issued_currency_amount("20", context.issuerAddress, "USD")
            }
        )
        context.offer_create_response_1 = await sign_autofill_and_submit(context, payload, context.bobWallet)

        payload = ObjFactory.getObj(
            "offercreate",
            {
                "Account": context.aliceAddress,
                "TakerPays": await generate_issued_currency_amount("20", context.issuerAddress, "USD"),
                "TakerGets": await generate_issued_currency_amount("20", context.issuerAddress, "BTC")
            }
        )
        context.offer_create_response_2 = await sign_autofill_and_submit(context, payload, context.aliceWallet)


        payload = ObjFactory.getObj(
            "payment",
            {
                "Account": context.aliceAddress,
                "Destination": context.carolAddress,
                "Amount": await generate_issued_currency_amount("20", context.issuerAddress, "USD"),
                "Flags": PaymentFlags.tfPartialPayment,
                "SendMax": await generate_issued_currency_amount("20", context.issuerAddress, "BTC")
            });
        context.py_response_3 = await sign_autofill_and_submit(context, payload, context.aliceWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"

    }
})

When('we send cross currency payment using BTC and USD with offer and payment', {timeout: 180000}, async () => {
    try {
        let payload = ObjFactory.getObj(
            ObjFactory.ObjType.AccountSet,
            {
                "Account": context.issuerAddress,
                "SetFlag": AccountSetAsfFlags.asfDefaultRipple,
            });
        await sign_autofill_and_submit(context, payload, context.issuerWallet)

        payload = ObjFactory.getObj(
            "trustset",
            {
                "Account": context.carolAddress,
                "LimitAmount": await generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD")
            });
        context.ts_response_1 = await sign_autofill_and_submit(context, payload, context.carolWallet)

        payload = ObjFactory.getObj(
            "trustset",
            {
                "Account": context.aliceAddress,
                "LimitAmount": await generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "BTC")
            });
        context.ts_response_2 = await sign_autofill_and_submit(context, payload, context.aliceWallet)

        payload = ObjFactory.getObj(
            "payment",
            {
                "Account": context.issuerAddress,
                "Destination": context.aliceAddress,
                "Amount": await generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "BTC"),
            });
        context.py_response_1 = await sign_autofill_and_submit(context, payload, context.issuerWallet)

        payload = ObjFactory.getObj(
            "trustset",
            {
                "Account": context.bobAddress,
                "LimitAmount": await generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD"),
            });
        context.ts_response_3 = await sign_autofill_and_submit(context, payload, context.bobWallet)

        payload = ObjFactory.getObj(
            "payment",
            {
                "Account": context.issuerAddress,
                "Destination": context.bobAddress,
                "Amount": await generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD"),
            });
        context.py_response_2 = await sign_autofill_and_submit(context, payload, context.issuerWallet)

        payload = ObjFactory.getObj(
            "offercreate",
            {
                "Account": context.bobAddress,
                "TakerPays": await generate_issued_currency_amount("20", context.issuerAddress, "BTC"),
                "TakerGets": await generate_issued_currency_amount("20", context.issuerAddress, "USD")
            }
        )
        context.offer_create_response_1 = await sign_autofill_and_submit(context, payload, context.bobWallet)
        payload = ObjFactory.getObj(
            "payment",
            {
                "Account": context.aliceAddress,
                "Destination": context.carolAddress,
                "Amount": await generate_issued_currency_amount("20", context.issuerAddress, "USD"),
                "Flags": PaymentFlags.tfPartialPayment,
                "SendMax": await generate_issued_currency_amount("20", context.issuerAddress, "BTC")
            });
        context.py_response_3 = await sign_autofill_and_submit(context, payload, context.aliceWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
    }
})

When('we send cross currency payment using XRP and USD', {timeout: 180000}, async () => {
    try {
        let payload = ObjFactory.getObj(
            ObjFactory.ObjType.AccountSet,
            {
                "Account": context.issuerAddress,
                "SetFlag": AccountSetAsfFlags.asfDefaultRipple,
            });
        await sign_autofill_and_submit(context, payload, context.issuerWallet)

        payload = ObjFactory.getObj(
            "trustset",
            {
                "Account": context.carolAddress,
                "LimitAmount": await generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD")
            });
        context.ts_response_1 = await sign_autofill_and_submit(context, payload, context.carolWallet)

        payload = ObjFactory.getObj(
            "trustset",
            {
                "Account": context.bobAddress,
                "LimitAmount": await generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD")
            });
        context.ts_response_2 = await sign_autofill_and_submit(context, payload, context.bobWallet)

        payload = ObjFactory.getObj(
            "payment",
            {
                "Account": context.issuerAddress,
                "Destination": context.bobAddress,
                "Amount": await generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD"),
            });
        context.py_response_1 = await sign_autofill_and_submit(context, payload, context.issuerWallet)

        payload = ObjFactory.getObj(
            "offercreate",
            {
                "Account": context.bobAddress,
                "TakerPays": "100",
                "TakerGets": await generate_issued_currency_amount("20", context.issuerAddress, "USD")
            }
        )
        context.offer_create_response_1 = await sign_autofill_and_submit(context, payload, context.bobWallet)

        payload = ObjFactory.getObj(
            "payment",
            {
                "Account": context.aliceAddress,
                "Destination": context.carolAddress,
                "Amount": await generate_issued_currency_amount("20", context.issuerAddress, "USD"),
                "Paths": [[await generate_path_step(context.issuerAddress, "USD")]],
                "Flags": PaymentFlags.tfPartialPayment,
                "SendMax": "100"
            });
        context.py_response_2 = await sign_autofill_and_submit(context, payload, context.aliceWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
    }
})

When('we send cross currency payment to self using XRP and USD', {timeout: 180000}, async () => {
    try {
        let payload = ObjFactory.getObj(
            ObjFactory.ObjType.AccountSet,
            {
                "Account": context.issuerAddress,
                "SetFlag": AccountSetAsfFlags.asfDefaultRipple,
            });
        await sign_autofill_and_submit(context, payload, context.issuerWallet)

        payload = ObjFactory.getObj(
            "trustset",
            {
                "Account": context.aliceAddress,
                "LimitAmount": await generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD")
            });
        context.ts_response_1 = await sign_autofill_and_submit(context, payload, context.aliceWallet)

        payload = ObjFactory.getObj(
            "payment",
            {
                "Account": context.issuerAddress,
                "Destination": context.aliceAddress,
                "Amount": await generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD"),
            });
        context.py_response_1 = await sign_autofill_and_submit(context, payload, context.issuerWallet)
        payload = ObjFactory.getObj(
            "offercreate",
            {
                "Account": context.bobAddress,
                "TakerPays": "35000000",
                "TakerGets": await generate_issued_currency_amount("20", context.issuerAddress, "USD")
            }
        )
        context.offer_create_response_1 = await sign_autofill_and_submit(context, payload, context.bobWallet)

        payload = ObjFactory.getObj(
            "payment",
            {
                "Account": context.aliceAddress,
                "Destination": context.aliceAddress,
                "Amount": "35000000",
                "Flags": PaymentFlags.tfPartialPayment,
                "SendMax": await generate_issued_currency_amount("20", context.issuerAddress, "USD")
            });
        context.py_response_2 = await sign_autofill_and_submit(context, payload, context.aliceWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
    }
})

When('we send cross currency payment using USD and XRP', {timeout: 180000}, async () => {
    try {
        let payload = ObjFactory.getObj(
            ObjFactory.ObjType.AccountSet,
            {
                "Account": context.issuerAddress,
                "SetFlag": AccountSetAsfFlags.asfDefaultRipple,
            });
        await sign_autofill_and_submit(context, payload, context.issuerWallet)

        payload = ObjFactory.getObj(
            "trustset",
            {
                "Account": context.aliceAddress,
                "LimitAmount": await generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD")
            });
        context.ts_response_1 = await sign_autofill_and_submit(context, payload, context.aliceWallet)

        payload = ObjFactory.getObj(
            "payment",
            {
                "Account": context.issuerAddress,
                "Destination": context.aliceAddress,
                "Amount": await generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD"),
            });
        context.py_response_1 = await sign_autofill_and_submit(context, payload, context.issuerWallet)

        payload = ObjFactory.getObj(
            "offercreate",
            {
                "Account": context.bobAddress,
                "TakerPays": await generate_issued_currency_amount("20", context.issuerAddress, "USD"),
                "TakerGets": "25000000"
            }
        )
        context.offer_create_response_1 = await sign_autofill_and_submit(context, payload, context.bobWallet)

        payload = ObjFactory.getObj(
            "payment",
            {
                "Account": context.aliceAddress,
                "Destination": context.carolAddress,
                "Amount": "25000000",
                "Flags": PaymentFlags.tfPartialPayment,
                "SendMax": await generate_issued_currency_amount("20", context.issuerAddress, "USD")
            });
        context.py_response_2 = await sign_autofill_and_submit(context, payload, context.aliceWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"

    }
})

When('we send cross currency payment using USD and XRP without specifying send_max', {timeout: 180000}, async () => {
    try {
        let payload = ObjFactory.getObj(
            ObjFactory.ObjType.AccountSet,
            {
                "Account": context.issuerAddress,
                "SetFlag": AccountSetAsfFlags.asfDefaultRipple,
            });
        await sign_autofill_and_submit(context, payload, context.issuerWallet)

        payload = ObjFactory.getObj(
            "trustset",
            {
                "Account": context.aliceAddress,
                "LimitAmount": await generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD")
            });
        context.ts_response_1 = await sign_autofill_and_submit(context, payload, context.aliceWallet)

        payload = ObjFactory.getObj(
            "payment",
            {
                "Account": context.issuerAddress,
                "Destination": context.aliceAddress,
                "Amount": await generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD"),
            });
        context.py_response_1 = await sign_autofill_and_submit(context, payload, context.issuerWallet)

        payload = ObjFactory.getObj(
            "offercreate",
            {
                "Account": context.bobAddress,
                "TakerPays": await generate_issued_currency_amount("20", context.issuerAddress, "USD"),
                "TakerGets": "25000000"
            }
        )
        context.offer_create_response_1 = await sign_autofill_and_submit(context, payload, context.bobWallet)

        payload = ObjFactory.getObj(
            "payment",
            {
                "Account": context.aliceAddress,
                "Destination": context.carolAddress,
                "Amount": "25000000",
                "Flags": PaymentFlags.tfPartialPayment,
            });
        context.py_response_2 = await sign_autofill_and_submit(context, payload, context.aliceWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
    }
})

When('we send cross currency payment using BTC, USD and XRP', {timeout: 180000}, async () => {
    try {
        let payload = ObjFactory.getObj(
            ObjFactory.ObjType.AccountSet,
            {
                "Account": context.issuerAddress,
                "SetFlag": AccountSetAsfFlags.asfDefaultRipple,
            });
        await sign_autofill_and_submit(context, payload, context.issuerWallet)

        payload = ObjFactory.getObj(
            "trustset",
            {
                "Account": context.carolAddress,
                "LimitAmount": await generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD")
            });
        context.ts_response_1 = await sign_autofill_and_submit(context, payload, context.carolWallet)

        payload = ObjFactory.getObj(
            "trustset",
            {
                "Account": context.aliceAddress,
                "LimitAmount": await generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "BTC")
            });
        context.ts_response_2 = await sign_autofill_and_submit(context, payload, context.aliceWallet)

        payload = ObjFactory.getObj(
            "payment",
            {
                "Account": context.issuerAddress,
                "Destination": context.aliceAddress,
                "Amount": await generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "BTC"),
            });
        context.py_response_1 = await sign_autofill_and_submit(context, payload, context.issuerWallet)

        payload = ObjFactory.getObj(
            "trustset",
            {
                "Account": context.bobAddress,
                "LimitAmount": await generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD"),
            });
        context.ts_response_3 = await sign_autofill_and_submit(context, payload, context.bobWallet)

        payload = ObjFactory.getObj(
            "payment",
            {
                "Account": context.issuerAddress,
                "Destination": context.bobAddress,
                "Amount": await generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD"),
            });
        context.py_response_2 = await sign_autofill_and_submit(context, payload, context.issuerWallet)

        payload = ObjFactory.getObj(
            "offercreate",
            {
                "Account": context.bobAddress,
                "TakerPays": "100",
                "TakerGets": await generate_issued_currency_amount("20", context.issuerAddress, "USD")
            }
        )
        context.offer_create_response_1 = await sign_autofill_and_submit(context, payload, context.bobWallet)

        payload = ObjFactory.getObj(
            "offercreate",
            {
                "Account": context.bobAddress,
                "TakerPays": await generate_issued_currency_amount("20", context.issuerAddress, "BTC"),
                "TakerGets": "100"
            }
        )
        context.offer_create_response_2 = await sign_autofill_and_submit(context, payload, context.bobWallet)
        payload = ObjFactory.getObj(
            "payment",
            {
                "Account": context.aliceAddress,
                "Destination": context.carolAddress,
                "Amount": await generate_issued_currency_amount("20", context.issuerAddress, "USD"),
                "Paths": [
                    [await generate_path_step(issuer = undefined, currency = "USD")],
                    [await generate_path_step(context.issuerAddress, "USD")]
                ],
                "Flags": PaymentFlags.tfPartialPayment,
                "SendMax": await generate_issued_currency_amount("20", context.issuerAddress, "BTC")
            });
        context.py_response_3 = await sign_autofill_and_submit(context, payload, context.aliceWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
    }
})

When('we send cross currency payment using BTC, USD and XRP without specifying paths', {timeout: 180000}, async () => {
    try {
        let payload = ObjFactory.getObj(
            ObjFactory.ObjType.AccountSet,
            {
                "Account": context.issuerAddress,
                "SetFlag": AccountSetAsfFlags.asfDefaultRipple,
            });
        await sign_autofill_and_submit(context, payload, context.issuerWallet)

        payload = ObjFactory.getObj(
            "trustset",
            {
                "Account": context.carolAddress,
                "LimitAmount": await generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD")
            });
        context.ts_response_1 = await sign_autofill_and_submit(context, payload, context.carolWallet)

        payload = ObjFactory.getObj(
            "trustset",
            {
                "Account": context.aliceAddress,
                "LimitAmount": await generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "BTC")
            });
        context.ts_response_2 = await sign_autofill_and_submit(context, payload, context.aliceWallet)

        payload = ObjFactory.getObj(
            "payment",
            {
                "Account": context.issuerAddress,
                "Destination": context.aliceAddress,
                "Amount": await generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "BTC"),
            });
        context.py_response_1 = await sign_autofill_and_submit(context, payload, context.issuerWallet)

        payload = ObjFactory.getObj(
            "trustset",
            {
                "Account": context.bobAddress,
                "LimitAmount": await generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD"),
            });
        context.ts_response_3 = await sign_autofill_and_submit(context, payload, context.bobWallet)

        payload = ObjFactory.getObj(
            "payment",
            {
                "Account": context.issuerAddress,
                "Destination": context.bobAddress,
                "Amount": await generate_issued_currency_amount(context.transferAmount, context.issuerAddress, "USD"),
            });
        context.py_response_2 = await sign_autofill_and_submit(context, payload, context.issuerWallet)

        payload = ObjFactory.getObj(
            "offercreate",
            {
                "Account": context.bobAddress,
                "TakerPays": "100",
                "TakerGets": await generate_issued_currency_amount("20", context.issuerAddress, "USD")
            }
        )
        context.offer_create_response_1 = await sign_autofill_and_submit(context, payload, context.bobWallet)

        payload = ObjFactory.getObj(
            "offercreate",
            {
                "Account": context.bobAddress,
                "TakerPays": await generate_issued_currency_amount("20", context.issuerAddress, "BTC"),
                "TakerGets": "100"
            }
        )
        context.offer_create_response_2 = await sign_autofill_and_submit(context, payload, context.bobWallet)

        payload = ObjFactory.getObj(
            "payment",
            {
                "Account": context.aliceAddress,
                "Destination": context.carolAddress,
                "Amount": await generate_issued_currency_amount("20", context.issuerAddress, "USD"),
                "Flags": PaymentFlags.tfPartialPayment,
                "SendMax": await generate_issued_currency_amount("20", context.issuerAddress, "BTC")
            });
        context.py_response_3 = await sign_autofill_and_submit(context, payload, context.aliceWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
        throw error
    }
})

Then('trustline payment using one currency is successful', {timeout: 180000}, async () => {
    verify_account_balance(await get_account_balance(context, context.sourceAddress), (parseFloat(context.sourceBalance) - (xrpl.dropsToXrp(context.minDrop))));
    verify_account_balance(await get_account_balance(context, context.destinationAddress),
        (parseFloat(context.destinationBalance) - (xrpl.dropsToXrp(context.minDrop)))
    );

    await verify_trustline_account_objects(context.client, context.ts_response_1)
    await verify_payment_account_objects(context.client, context.py_response_1)
})

Then('issued currency payment is successful', {timeout: 180000}, async () => {
    verify_account_balance(await get_account_balance(context, context.sourceAddress), (parseFloat(context.sourceBalance) - (2 * xrpl.dropsToXrp(context.minDrop))));
    verify_account_balance(await get_account_balance(context, context.issuerAddress), (parseFloat(context.issuerBalance) - (2 * xrpl.dropsToXrp(context.minDrop))));
    verify_account_balance(await get_account_balance(context, context.destinationAddress), (parseFloat(context.destinationBalance) - (xrpl.dropsToXrp(context.minDrop))));
    await verify_trustline_account_objects(context.client, context.ts_response_1)

    await verify_payment_account_objects(context.client, context.py_response_1)

    await verify_trustline_account_objects(context.client, context.ts_response_2)

    await verify_payment_account_objects(context.client, context.py_response_2)
})

Then('issued currency payment without trustline is not successful', {timeout: 180000}, async () => {
    verify_account_balance(await get_account_balance(context, context.sourceAddress), (parseFloat(context.sourceBalance) - (2 * xrpl.dropsToXrp(context.minDrop))));
    verify_account_balance(await get_account_balance(context, context.issuerAddress), (parseFloat(context.issuerBalance) - (2 * xrpl.dropsToXrp(context.minDrop))));
    verify_account_balance(await get_account_balance(context, context.destinationAddress), (parseFloat(context.destinationBalance)));
    await verify_trustline_account_objects(context.client, context.ts_response_1)

    await verify_payment_account_objects(context.client, context.py_response_1)

    await verify_payment_account_objects(context.client, context.py_response_2, ResponseCode.path_dry)
})

Then('issued currency payment in decimal is successful', {timeout: 180000}, async () => {
    verify_account_balance(await get_account_balance(context, context.sourceAddress), (parseFloat(context.sourceBalance) - (xrpl.dropsToXrp(context.minDrop))));
    verify_account_balance(await get_account_balance(context, context.destinationAddress), (parseFloat(context.destinationBalance) - (xrpl.dropsToXrp(context.minDrop))));
    await verify_trustline_account_objects(context.client, context.ts_response_1)

    await verify_payment_account_objects(context.client, context.py_response_1)
})

Then('issued currency payment in non-string decimal is successful', {timeout: 180000}, async () => {
    // This test may not be possible with JS client. Returning early.
    return

    // verify_account_balance(await get_account_balance(context, context.sourceAddress), (parseFloat(context.sourceBalance) - (xrpl.dropsToXrp(context.minDrop))));
    // verify_account_balance(await get_account_balance(context, context.destinationAddress), (parseFloat(context.destinationBalance) - (xrpl.dropsToXrp(context.minDrop))));
    // await verify_trustline_account_objects(context.client, context.ts_response_1)
    // // await verify_response_code(context.ts_response_1, ResponseCode.success)
    //
    // await verify_payment_account_objects(context.client, context.py_response_1)
    // // await verify_response_code(context.py_response_1, ResponseCode.success)
})

Then('issued currency payment from Invalid issuer is not successful', {timeout: 180000}, async () => {
    verify_test_status(context.testStatus, "failed")
    verify_test_error_message(context.exception.toString(), /Error: Non-base58 character/, "Incorrect error message received.")
    verify_account_balance(await get_account_balance(context, context.destinationAddress), (parseFloat(context.destinationBalance)));
})

Then('issued currency payment to invalid recipient is not successful', {timeout: 180000}, async () => {
    verify_test_status(context.testStatus, "failed")
    verify_test_error_message(context.exception.toString(), /error_code: 19/, "Incorrect error message received.")
    verify_account_balance(await get_account_balance(context, context.sourceAddress), (parseFloat(context.sourceBalance)));
})

Then('trustline creation with non-standard currency code is successful', {timeout: 180000}, async () => {
    verify_account_balance(await get_account_balance(context, context.sourceAddress), parseFloat(context.sourceBalance));
    verify_account_balance(await get_account_balance(context, context.destinationAddress), (parseFloat(context.destinationBalance) - (xrpl.dropsToXrp(context.minDrop))));
    await verify_trustline_account_objects(context.client, context.ts_response_1)
})

Then('trustline creation with invalid currency code --- fails', {timeout: 180000}, async () => {
    verify_account_balance(await get_account_balance(context, context.sourceAddress), parseFloat(context.sourceBalance));
    verify_account_balance(await get_account_balance(context, context.destinationAddress), (parseFloat(context.destinationBalance) - (xrpl.dropsToXrp(context.minDrop))));
    await verify_trustline_account_objects(context.client, context.ts_response_1)
})

Then('trustline creation with invalid currency code USDX fails', {timeout: 180000}, async () => {
    verify_account_balance(await get_account_balance(context, context.sourceAddress), parseFloat(context.sourceBalance));
    verify_account_balance(await get_account_balance(context, context.destinationAddress), parseFloat(context.destinationBalance));
    verify_test_status(context.testStatus, "failed")
    verify_test_error_message(context.exception.toString(), /Error: Unsupported Currency representation: USDX/, "Incorrect error message received.")

})

Then('trustline creation to self is not successful', {timeout: 180000}, async () => {
    verify_account_balance(await get_account_balance(context, context.sourceAddress), parseFloat(context.sourceBalance));
    verify_test_status(context.testStatus, "failed")
    verify_test_error_message(context.exception.toString(), /Preliminary result: temDST_IS_SRC/, "Incorrect error message received.")
})

Then('trustline creation with invalid currency code XRP fails', {timeout: 180000}, async () => {
    verify_account_balance(await get_account_balance(context, context.sourceAddress), parseFloat(context.sourceBalance));
    verify_account_balance(await get_account_balance(context, context.destinationAddress), parseFloat(context.destinationBalance));
    verify_test_status(context.testStatus, "failed")
    verify_test_error_message(context.exception.toString(), /XRP is not an issued currency/, "Incorrect error message received.")
    await verify_trustline_account_objects(context.client, context.ts_response_1)
})

Then('trustline creation with negative limit amount is not successful', {timeout: 180000}, async () => {
    verify_account_balance(await get_account_balance(context, context.sourceAddress), parseFloat(context.sourceBalance));
    verify_account_balance(await get_account_balance(context, context.destinationAddress), parseFloat(context.destinationBalance));
    verify_test_status(context.testStatus, "failed")
    verify_test_error_message(context.exception.toString(), /Preliminary result: temBAD_LIMIT/, "Incorrect error message received.")
    await verify_trustline_account_objects(context.client, context.ts_response_1)
})

Then('trustline creation with zero limit amount is not successful', {timeout: 180000}, async () => {
    verify_account_balance(await get_account_balance(context, context.sourceAddress), parseFloat(context.sourceBalance));
    verify_account_balance(await get_account_balance(context, context.destinationAddress), (parseFloat(context.destinationBalance) - (xrpl.dropsToXrp(context.minDrop))));
    await verify_trustline_account_objects(context.client, context.ts_response_1, ResponseCode.no_line_redundant)
})

Then('issued currency payment with amount more than limit amount recipient is not successful', {timeout: 180000}, async () => {
    verify_account_balance(await get_account_balance(context, context.sourceAddress), (parseFloat(context.sourceBalance) - (xrpl.dropsToXrp(context.minDrop))));
    verify_account_balance(await get_account_balance(context, context.destinationAddress), (parseFloat(context.destinationBalance) - (xrpl.dropsToXrp(context.minDrop))));
    await verify_trustline_account_objects(context.client, context.ts_response_1)
    await verify_payment_account_objects(context.client, context.py_response_1, ResponseCode.path_partial)
})

Then('cross currency payment using BTC and USD is successful', {timeout: 180000}, async () => {
    verify_account_balance(await get_account_balance(context, context.aliceAddress), (parseFloat(context.aliceBalance) - (2 * xrpl.dropsToXrp(context.minDrop))));
    verify_account_balance(await get_account_balance(context, context.bobAddress), (parseFloat(context.bobBalance) - (2 * xrpl.dropsToXrp(context.minDrop))));
    verify_account_balance(await get_account_balance(context, context.carolAddress), (parseFloat(context.carolBalance) - (xrpl.dropsToXrp(context.minDrop))));

    await verify_trustline_account_objects(context.client, context.ts_response_1)
    await verify_trustline_account_objects(context.client, context.ts_response_2)
    await verify_trustline_account_objects(context.client, context.ts_response_3)

    await verify_payment_account_objects(context.client, context.py_response_1)
    await verify_payment_account_objects(context.client, context.py_response_2)
    await verify_payment_account_objects(context.client, context.py_response_3)

    await verify_offer_create_account_objects(context.client, context.offer_create_response_1, true)
})

Then('cross currency payment using BTC and USD without specifying paths is successful', {timeout: 180000}, async () => {
    verify_account_balance(await get_account_balance(context, context.aliceAddress), (parseFloat(context.aliceBalance) - (3 * xrpl.dropsToXrp(context.minDrop))));
    verify_account_balance(await get_account_balance(context, context.bobAddress), (parseFloat(context.bobBalance) - (2 * xrpl.dropsToXrp(context.minDrop))));
    verify_account_balance(await get_account_balance(context, context.carolAddress), (parseFloat(context.carolBalance) - (xrpl.dropsToXrp(context.minDrop))));

    await verify_trustline_account_objects(context.client, context.ts_response_1)
    await verify_trustline_account_objects(context.client, context.ts_response_2)
    await verify_trustline_account_objects(context.client, context.ts_response_3)

    await verify_payment_account_objects(context.client, context.py_response_1)
    await verify_payment_account_objects(context.client, context.py_response_2)
    await verify_payment_account_objects(context.client, context.py_response_3, ResponseCode.path_dry)

    await verify_offer_create_account_objects(context.client, context.offer_create_response_1, true)
    await verify_offer_create_account_objects(context.client, context.offer_create_response_2, true)
})

Then('cross currency payment using BTC and USD with offer and payment is successful', {timeout: 180000}, async () => {
    verify_account_balance(await get_account_balance(context, context.aliceAddress), (parseFloat(context.aliceBalance) - (2 * xrpl.dropsToXrp(context.minDrop))));
    verify_account_balance(await get_account_balance(context, context.bobAddress), (parseFloat(context.bobBalance) - (2 * xrpl.dropsToXrp(context.minDrop))));
    verify_account_balance(await get_account_balance(context, context.carolAddress), (parseFloat(context.carolBalance) - (xrpl.dropsToXrp(context.minDrop))));

    await verify_trustline_account_objects(context.client, context.ts_response_1)
    await verify_trustline_account_objects(context.client, context.ts_response_2)
    await verify_trustline_account_objects(context.client, context.ts_response_3)

    await verify_payment_account_objects(context.client, context.py_response_1)
    await verify_payment_account_objects(context.client, context.py_response_2)
    await verify_payment_account_objects(context.client, context.py_response_3)

    await verify_offer_create_account_objects(context.client, context.offer_create_response_1, true)
})

Then('cross currency payment using XRP and USD is successful', {timeout: 180000}, async () => {
    verify_account_balance(await get_account_balance(context, context.aliceAddress), (parseFloat(context.aliceBalance) - (xrpl.dropsToXrp(context.minDrop + 100))));
    verify_account_balance(await get_account_balance(context, context.bobAddress), (parseFloat(context.bobBalance) + (8 * xrpl.dropsToXrp(context.minDrop))));
    verify_account_balance(await get_account_balance(context, context.carolAddress), (parseFloat(context.carolBalance) - (xrpl.dropsToXrp(context.minDrop))));

    await verify_trustline_account_objects(context.client, context.ts_response_1)
    await verify_trustline_account_objects(context.client, context.ts_response_2)

    await verify_payment_account_objects(context.client, context.py_response_1)
    await verify_payment_account_objects(context.client, context.py_response_2)

    await verify_offer_create_account_objects(context.client, context.offer_create_response_1, true)
})

Then('cross currency payment to self using XRP and USD is not successful', {timeout: 180000}, async () => {
    verify_account_balance(await get_account_balance(context, context.aliceAddress), (parseFloat(context.aliceBalance) - (2 * xrpl.dropsToXrp(context.minDrop))));
    verify_account_balance(await get_account_balance(context, context.bobAddress), (parseFloat(context.bobBalance) - (xrpl.dropsToXrp(context.minDrop))));
    verify_account_balance(await get_account_balance(context, context.issuerAddress), (parseFloat(context.issuerBalance) - (2 * xrpl.dropsToXrp(context.minDrop))));
    await verify_trustline_account_objects(context.client, context.ts_response_1)

    await verify_payment_account_objects(context.client, context.py_response_1)
    await verify_payment_account_objects(context.client, context.py_response_2, ResponseCode.path_dry)

    await verify_offer_create_account_objects(context.client, context.offer_create_response_1, true, ResponseCode.unfunded_offer)
})

Then('cross currency payment using USD and XRP is successful', {timeout: 180000}, async () => {
    verify_account_balance(await get_account_balance(context, context.aliceAddress), (parseFloat(context.aliceBalance) - (2 * xrpl.dropsToXrp(context.minDrop))));
    verify_account_balance(await get_account_balance(context, context.bobAddress), (parseFloat(context.bobBalance) - (xrpl.dropsToXrp(context.minDrop + 25000000))));
    verify_account_balance(await get_account_balance(context, context.carolAddress), (parseFloat(context.carolBalance)) + parseFloat(xrpl.dropsToXrp(25000000)));

    await verify_trustline_account_objects(context.client, context.ts_response_1)
    await verify_payment_account_objects(context.client, context.py_response_1)
    await verify_payment_account_objects(context.client, context.py_response_2)

    await verify_offer_create_account_objects(context.client, context.offer_create_response_1, true)
})

Then('cross currency payment using USD and XRP without specifying send_max fails', {timeout: 180000}, async () => {
    verify_account_balance(await get_account_balance(context, context.aliceAddress), (parseFloat(context.aliceBalance) - (xrpl.dropsToXrp(context.minDrop))));
    verify_account_balance(await get_account_balance(context, context.bobAddress), (parseFloat(context.bobBalance) - (xrpl.dropsToXrp(context.minDrop))));
    verify_account_balance(await get_account_balance(context, context.carolAddress), (parseFloat(context.carolBalance)));

    verify_test_status(context.testStatus, "failed")
    verify_test_error_message(context.exception.toString(), /temBAD_SEND_XRP_PARTIAL/)

    await verify_trustline_account_objects(context.client, context.ts_response_1)

    await verify_payment_account_objects(context.client, context.py_response_1)
    await verify_payment_account_objects(context.client, context.py_response_2)

    await verify_offer_create_account_objects(context.client, context.offer_create_response_1, true)
})

Then('cross currency payment using BTC, USD and XRP is successful', {timeout: 180000}, async () => {
    verify_account_balance(await get_account_balance(context, context.aliceAddress), (parseFloat(context.aliceBalance) - (2 * xrpl.dropsToXrp(context.minDrop))));
    verify_account_balance(await get_account_balance(context, context.bobAddress), (parseFloat(context.bobBalance) - (3 * xrpl.dropsToXrp(context.minDrop))));
    verify_account_balance(await get_account_balance(context, context.carolAddress), (parseFloat(context.carolBalance) - (xrpl.dropsToXrp(context.minDrop))));

    await verify_trustline_account_objects(context.client, context.ts_response_1)
    await verify_trustline_account_objects(context.client, context.ts_response_2)
    await verify_payment_account_objects(context.client, context.py_response_1)
    await verify_payment_account_objects(context.client, context.py_response_2)
    await verify_payment_account_objects(context.client, context.py_response_3, ResponseCode.path_dry)
    await verify_offer_create_account_objects(context.client, context.offer_create_response_1)
    await verify_offer_create_account_objects(context.client, context.offer_create_response_2)
})

Then('cross currency payment using BTC, USD and XRP without specifying paths is not successful', {timeout: 180000}, async () => {
    verify_account_balance(await get_account_balance(context, context.aliceAddress), (parseFloat(context.aliceBalance) - (2 * xrpl.dropsToXrp(context.minDrop))));
    verify_account_balance(await get_account_balance(context, context.bobAddress), (parseFloat(context.bobBalance) - (3 * xrpl.dropsToXrp(context.minDrop))));
    verify_account_balance(await get_account_balance(context, context.carolAddress), (parseFloat(context.carolBalance) - (xrpl.dropsToXrp(context.minDrop))));
    await verify_trustline_account_objects(context.client, context.ts_response_1)
    await verify_trustline_account_objects(context.client, context.ts_response_2)

    await verify_payment_account_objects(context.client, context.py_response_1)
    await verify_payment_account_objects(context.client, context.py_response_2)
    await verify_payment_account_objects(context.client, context.py_response_3, ResponseCode.path_dry)

    await verify_offer_create_account_objects(context.client, context.offer_create_response_1)
    await verify_offer_create_account_objects(context.client, context.offer_create_response_2)
})

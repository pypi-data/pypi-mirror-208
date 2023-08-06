const {BeforeAll, AfterAll, Given, When, Then, Before, After} = require('@cucumber/cucumber')
const xrpl = require("xrpl");
const {AccountSetAsfFlags} = require("xrpl");
const {} = require('../context.js');
let context = require('../context.js');
const assert = require('assert');
const ObjFactory = require("../lib/ObjFactory");
const {ObjType} = require("../lib/ObjFactory");
const {
    verify_account_balance,
    verify_payment_account_objects,
    ResponseCode,
    get_account_balance,
    verify_test_status,
    verify_test_error_message,
} = require("./common");

When('we send a payment of {string} XRP from Alice to Bob', {timeout: 180000}, async (transferAmount) => {
    try {

        context.transferAmount = ((transferAmount == ("10000000000000") || transferAmount.toString().includes(".")) ? transferAmount : xrpl.xrpToDrops(transferAmount))
        context.prepared = await context.client.autofill(ObjFactory.getObj(ObjFactory.ObjType.Payment, {
            "Account": context.sourceAddress,
            "Amount": context.transferAmount,
            "Destination": context.destinationAddress,
        }));
        context.signed_payment_tx = context.sourceWallet.sign(context.prepared).tx_blob;
        context.response = await context.client.submitAndWait(context.signed_payment_tx);
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
    }
});

When('we send a payment of {string} XRP from Alice to self', {timeout: 180000}, async (transferAmount) => {
    try {
        context.transferAmount = transferAmount
        context.prepared = await context.client.autofill(ObjFactory.getObj(ObjFactory.ObjType.Payment, {
            "Account": context.sourceAddress, "Amount": context.transferAmount, "Destination": context.sourceAddress,
        }));
        context.signed_payment_tx = context.sourceWallet.sign(context.prepared).tx_blob;
        context.response = await context.client.submitAndWait(context.signed_payment_tx);
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
    }
});

When('we only submit a payment of {string} XRP from Alice to Bob', {timeout: 180000}, async (transferAmount) => {
    try {
        context.transferAmount = transferAmount
        context.prepared = await context.client.autofill(ObjFactory.getObj(ObjFactory.ObjType.Payment, {
            "Account": context.sourceAddress,
            "Amount": context.transferAmount,
            "Destination": context.destinationAddress,
        }));
        context.signed_payment_tx = context.sourceWallet.sign(context.prepared).tx_blob;
        context.payment_response = await context.client.submit(context.signed_payment_tx);
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
    }
});

When('we send a payment with amount greater than balance from Alice to Bob', {timeout: 180000}, async () => {
    try {
        context.transferAmount = await context.client.getXrpBalance(context.sourceAddress) + xrpl.xrpToDrops(1)
        context.prepared = await context.client.autofill(ObjFactory.getObj(ObjFactory.ObjType.Payment, {
            "Account": context.sourceAddress,
            "Amount": context.transferAmount,
            "Destination": context.destinationAddress,
        }));
        context.signed_payment_tx = context.sourceWallet.sign(context.prepared).tx_blob;
        context.response = await context.client.submitAndWait(context.signed_payment_tx);
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
    }
});

When('we send a payment of {string} XRP from Alice to Invalid', {timeout: 180000}, async (transferAmount) => {
    try {
        context.transferAmount = transferAmount
        context.prepared = await context.client.autofill(ObjFactory.getObj(ObjFactory.ObjType.Payment, {
            "Account": context.sourceAddress, "Amount": context.transferAmount, "Destination": context.invalidAddress,
        }));

        context.signed_payment_tx = context.sourceWallet.sign(context.prepared).tx_blob;
        context.payment_response = await context.client.submit(context.signed_payment_tx);
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
    }
});

When('we send a payment of {string} XRP to Bob without providing source information', {timeout: 180000}, async (transferAmount) => {
    try {
        context.transferAmount = transferAmount
        context.prepared = await context.client.autofill(ObjFactory.getObj(ObjFactory.ObjType.Payment, {
            "Account": "", "Amount": context.transferAmount, "Destination": context.destinationAddress,
        }));
        context.signed_payment_tx = context.sourceWallet.sign(context.prepared).tx_blob;
        context.payment_response = await context.client.submit(context.signed_payment_tx);
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
    }
});

When('we send a payment of {string} XRP from Alice without providing destination information', {timeout: 180000}, async (transferAmount) => {
    try {
        context.transferAmount = transferAmount
        context.prepared = await context.client.autofill(ObjFactory.getObj(ObjFactory.ObjType.Payment, {
            "Account": context.sourceAddress, "Amount": context.transferAmount, "Destination": "",
        }));
        context.signed_payment_tx = context.sourceWallet.sign(context.prepared).tx_blob;
        context.payment_response = await context.client.submit(context.signed_payment_tx);
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
    }
});

When('we send a payment of {string} USD from Alice to Bob', {timeout: 180000}, async (transferAmountInUSD) => {
    try {
        context.transferAmount = {
            currency: "USD", value: transferAmountInUSD, issuer: "rf1BiGeXwwQoi8Z2ueFYTEXSwuJYfV2Jpn"
        }
        context.prepared = await context.client.autofill(ObjFactory.getObj(ObjFactory.ObjType.Payment, {
            "Account": context.sourceAddress,
            "Amount": context.transferAmount,
            "Destination": context.destinationAddress,
        }));
        context.signed_payment_tx = context.sourceWallet.sign(context.prepared).tx_blob;
        context.response = await context.client.submitAndWait(context.signed_payment_tx);
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
    }
});

When('we send a payment of {string} XRP with destination tag {string} info from Alice to Bob', {timeout: 180000}, async (transferAmount, destinationTag) => {
    try {
        context.transferAmount = transferAmount
        context.prepared = await context.client.autofill(ObjFactory.getObj(ObjFactory.ObjType.Payment, {
            "Account": context.sourceAddress,
            "Amount": context.transferAmount,
            "Destination": context.destinationAddress,
            "DestinationTag": parseInt(destinationTag)
        }));
        context.signed_payment_tx = context.sourceWallet.sign(context.prepared).tx_blob;
        context.response = await context.client.submitAndWait(context.signed_payment_tx);
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
    }
});


When('we send a payment of {string} XRP with invoice id {string} from Alice to Bob', {timeout: 180000}, async (transferAmount, invoiceID) => {
    try {
        context.transferAmount = transferAmount
        context.prepared = await context.client.autofill(ObjFactory.getObj(ObjFactory.ObjType.Payment, {
            "Account": context.sourceAddress,
            "Amount": context.transferAmount,
            "Destination": context.destinationAddress,
            "InvoiceID": invoiceID
        }));
        context.signed_payment_tx = context.sourceWallet.sign(context.prepared).tx_blob;
        context.response = await context.client.submitAndWait(context.signed_payment_tx);
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
    }
});

When('we send a payment of {string} XRP from Alice as a preauth account to Bob', {timeout: 180000}, async (transferAmount) => {
    try {
        context.transferAmount = transferAmount
        const autofilled_account_set_tx = await context.client.autofill({
            TransactionType: 'AccountSet',
            Account: context.destinationAddress,
            SetFlag: AccountSetAsfFlags.asfDepositAuth
        })
        let signed_autofilled_account_set_tx = context.destinationWallet.sign(autofilled_account_set_tx).tx_blob;
        await context.client.submitAndWait(signed_autofilled_account_set_tx);
        const account_info_request = {
            command: 'account_info', account: context.destinationAddress,
        }
        const last_sequence = (await context.client.request(account_info_request)).result.account_data.Sequence;
        const autofilled_deposit_preauth_tx = await context.client.autofill({
            TransactionType: "DepositPreauth",
            Account: context.destinationAddress,
            Sequence: last_sequence,
            Authorize: context.sourceAddress,
        })
        let signed_autofilled_deposit_preauth_tx = context.destinationWallet.sign(autofilled_deposit_preauth_tx).tx_blob;
        await context.client.submitAndWait(signed_autofilled_deposit_preauth_tx);
        context.destinationBalance = await context.client.getXrpBalance(context.destinationAddress)
        context.prepared = await context.client.autofill(ObjFactory.getObj(ObjFactory.ObjType.Payment, {
            "Account": context.sourceAddress,
            "Amount": context.transferAmount,
            "Destination": context.destinationAddress,
        }));
        context.signed_payment_tx = context.sourceWallet.sign(context.prepared).tx_blob;
        context.response = await context.client.submitAndWait(context.signed_payment_tx);
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
    }
});

When('we send a payment of {string} XRP from Alice as a non-preauth account to Bob', {timeout: 180000}, async (transferAmount) => {
    try {
        context.transferAmount = transferAmount
        const autofilled_account_set_tx = await context.client.autofill({
            TransactionType: 'AccountSet',
            Account: context.destinationAddress,
            SetFlag: AccountSetAsfFlags.asfDepositAuth
        })
        await context.client.submitAndWait(autofilled_account_set_tx, {
            wallet: context.destinationWallet,
        });
        context.destinationBalance = await context.client.getXrpBalance(context.destinationAddress)
        context.prepared = await context.client.autofill(ObjFactory.getObj(ObjFactory.ObjType.Payment, {
            "Account": context.sourceAddress,
            "Amount": context.transferAmount,
            "Destination": context.destinationAddress,
        }));
        context.signed_payment_tx = context.sourceWallet.sign(context.prepared).tx_blob;
        context.response = await context.client.submitAndWait(context.signed_payment_tx);
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
    }
});

Then('the balances after a valid payment are correct', {timeout: 180000}, async () => {
    await verify_payment_account_objects(context.client, context.response)
    verify_account_balance(await get_account_balance(context, context.sourceAddress), (parseFloat(context.sourceBalance) - (xrpl.dropsToXrp(context.minDrop)) - xrpl.dropsToXrp(context.transferAmount)));
    verify_account_balance(await get_account_balance(context, context.destinationAddress), (parseFloat(context.destinationBalance) + parseFloat(xrpl.dropsToXrp(context.transferAmount))));
});

Then('the balances are correct in submit only mode', {timeout: 180000}, async () => {
    verify_account_balance(await get_account_balance(context, context.sourceAddress), (parseFloat(context.sourceBalance)));
    verify_account_balance(await get_account_balance(context, context.destinationAddress), (parseFloat(context.destinationBalance)));
});

Then('the self-payment should fail', {timeout: 180000}, async () => {
    verify_test_status(context.testStatus, "failed")
    verify_test_error_message(context.exception.toString(), /temREDUNDANT/, "Incorrect error message received.")
    verify_account_balance(await get_account_balance(context, context.sourceAddress), (parseFloat(context.sourceBalance)));
});

Then('the payment with amount greater than balance should fail', {timeout: 180000}, async () => {
    await verify_payment_account_objects(context.client, context.response, ResponseCode.unfunded_payment)
    verify_account_balance(await get_account_balance(context, context.sourceAddress), (parseFloat(context.sourceBalance) - xrpl.dropsToXrp(context.minDrop)));
    verify_account_balance(await get_account_balance(context, context.destinationAddress), (parseFloat(context.destinationBalance)));
});

Then('the payment with invalid destination should fail', {timeout: 180000}, async () => {
    verify_test_status(context.testStatus, "failed")
    verify_test_error_message(context.exception.toString(), /Error: Non-base58 character/, "Incorrect error message received.")
    verify_account_balance(await get_account_balance(context, context.sourceAddress), (parseFloat(context.sourceBalance)));
});

Then('the payment with zero amount should fail', {timeout: 180000}, async () => {
    verify_test_status(context.testStatus, "failed")
    verify_test_error_message(context.exception.toString(), /temBAD_AMOUNT/, "Incorrect error message received.")
    verify_account_balance(await get_account_balance(context, context.sourceAddress), (parseFloat(context.sourceBalance)));
    verify_account_balance(await get_account_balance(context, context.destinationAddress), (parseFloat(context.destinationBalance)));
});

Then('the payment with decimal amount should fail', {timeout: 180000}, async () => {
    verify_test_status(context.testStatus, "failed")
    verify_test_error_message(context.exception.toString(), /Error: 10.5 is an illegal amount/, "Incorrect error message received.")
    verify_account_balance(await get_account_balance(context, context.sourceAddress), (parseFloat(context.sourceBalance)));
    verify_account_balance(await get_account_balance(context, context.destinationAddress), (parseFloat(context.destinationBalance)));
});

Then('the payment without source information should fail', {timeout: 180000}, async () => {
    verify_test_status(context.testStatus, "failed")
    verify_test_error_message(context.exception.toString(), /Missing field 'account'/, "Incorrect error message received.")
    verify_account_balance(await get_account_balance(context, context.destinationAddress), (parseFloat(context.destinationBalance)));
});

Then('the payment without destination information should fail', {timeout: 180000}, async () => {
    verify_test_status(context.testStatus, "failed")
    verify_test_error_message(context.exception.toString(), /Serialized transaction does not match original txJSON/, "Incorrect error message received.")
    verify_account_balance(await get_account_balance(context, context.sourceAddress), (parseFloat(context.sourceBalance)));
});

Then('the payment of 10 million XRP should fail', {timeout: 180000}, async () => {
    verify_account_balance(await get_account_balance(context, context.sourceAddress), (parseFloat(context.sourceBalance) - (xrpl.dropsToXrp(context.minDrop))));
    verify_account_balance(await get_account_balance(context, context.destinationAddress), (parseFloat(context.destinationBalance)));
});

Then('the balances after a non-xrp payment are correct', {timeout: 180000}, async () => {
    await verify_payment_account_objects(context.client, context.response, ResponseCode.path_dry)
    verify_account_balance(await get_account_balance(context, context.sourceAddress), (parseFloat(context.sourceBalance) - (xrpl.dropsToXrp(context.minDrop))));
    verify_account_balance(await get_account_balance(context, context.destinationAddress), (parseFloat(context.destinationBalance)));
});

Then('the balances after a payment with destination tag info are correct', {timeout: 180000}, async () => {
    await verify_payment_account_objects(context.client, context.response)
    verify_account_balance(await get_account_balance(context, context.sourceAddress), (parseFloat(context.sourceBalance) - (xrpl.dropsToXrp(context.minDrop)) - xrpl.dropsToXrp(context.transferAmount)).toFixed(6));
    verify_account_balance(await get_account_balance(context, context.destinationAddress), (parseFloat(context.destinationBalance) + parseFloat(xrpl.dropsToXrp(context.transferAmount))).toFixed(6));
});

Then('the balances after a payment with invoice id info are correct', {timeout: 180000}, async () => {
    await verify_payment_account_objects(context.client, context.response)
    verify_account_balance(await get_account_balance(context, context.sourceAddress), (parseFloat(context.sourceBalance) - xrpl.dropsToXrp(context.transferAmount) - xrpl.dropsToXrp(context.minDrop)));
    verify_account_balance(await get_account_balance(context, context.destinationAddress), (parseFloat(context.destinationBalance) + parseFloat(xrpl.dropsToXrp(context.transferAmount))));
});

Then('the balances after a payment with invalid invoice id info are correct', {timeout: 180000}, async () => {
    verify_test_status(context.testStatus, "failed")
    verify_test_error_message(context.exception.toString(), /Error: Invalid Hash length 1/, "Incorrect error message received.")
    verify_account_balance(await get_account_balance(context, context.sourceAddress), (parseFloat(context.sourceBalance)));
    verify_account_balance(await get_account_balance(context, context.destinationAddress), (parseFloat(context.destinationBalance)));
});

Then('the balances after a payment from preauth account are correct', {timeout: 180000}, async () => {
    await verify_payment_account_objects(context.client, context.response)
    verify_account_balance(await get_account_balance(context, context.sourceAddress), (parseFloat(context.sourceBalance) - xrpl.dropsToXrp(context.transferAmount) - xrpl.dropsToXrp(context.minDrop)));
    verify_account_balance(await get_account_balance(context, context.destinationAddress), (parseFloat(context.destinationBalance) + parseFloat(xrpl.dropsToXrp(context.transferAmount))));
});

Then('the balances after a payment from non-preauth account are correct', {timeout: 180000}, async () => {
    await verify_payment_account_objects(context.client, context.response, ResponseCode.no_permission)
    verify_account_balance(await get_account_balance(context, context.sourceAddress), (parseFloat(context.sourceBalance) - xrpl.dropsToXrp(context.minDrop)));
    verify_account_balance(await get_account_balance(context, context.destinationAddress), (parseFloat(context.destinationBalance)));
});

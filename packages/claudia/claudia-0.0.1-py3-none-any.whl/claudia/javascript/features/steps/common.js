const {BeforeAll, AfterAll, Given, When, Then, Before, After} = require('@cucumber/cucumber')
const xrpl = require("xrpl");
const {AccountSetAsfFlags, Wallet} = require("xrpl");
const {} = require('../context.js');
let context = require('../context.js');
const assert = require('assert');
const ObjFactory = require("../lib/ObjFactory");
const {ObjType} = require("../lib/ObjFactory");
const constants = require("./constants");
const ECDSA = require("xrpl/dist/npm/ECDSA");
const getFeeXrp = require("xrpl/dist/npm/sugar/getFeeXrp");

BeforeAll({timeout: 180000}, async () => {
    context.connectionScheme = process.env.CONNECTION_SCHEME;
    context.connectionUrl = process.env.CONNECTION_URL;
    context.connectionType = process.env.CONNECTION_TYPE;
    context.client = await getClient();
    context.crypto_algorithm = ECDSA.secp256k1
    context.test_genesis_wallet = await get_test_genesis_wallet(context)
    context.default_fee = parseInt(await get_fee(context))
})

Before({timeout: 180000}, async () => {
    context.minDrop = context.default_fee;
    context.exception = null
    context.testStatus = null
    context.transferAmount = "10000"
})

AfterAll({timeout: 180000}, async () => {
    if (context.client.isConnected()) {
        await context.client.disconnect()
    }
});

Given('we create {string} account for {string} with {string} XRP drops', {timeout: 180000}, async function (account_type, username, amount) {
    let account_fund_amount = null;
    if (amount == "default") {
        account_fund_amount = xrpl.dropsToXrp(constants.DEFAULT_ACCOUNT_FUND_AMOUNT)
    } else {
        account_fund_amount = xrpl.dropsToXrp(amount)
    }

    let wallet = await generate_wallet_info(context, true, account_fund_amount)

    if (account_type == "source") {
        context.sourceAccountUsername = username
        context.sourceWallet = wallet;
        context.sourceAddress = context.sourceWallet.address;
        context.sourceBalance = await context.client.getXrpBalance(context.sourceAddress)
    } else if (account_type == "destination") {
        context.destinationAccountUsername = username
        context.destinationWallet = wallet;
        context.destinationAddress = context.destinationWallet.address;
        context.destinationBalance = await context.client.getXrpBalance(context.destinationAddress)
    } else if (account_type == "issuer") {
        context.issuerAccountUsername = username
        context.issuerWallet = wallet;
        context.issuerAddress = context.issuerWallet.address;
        context.issuerBalance = await context.client.getXrpBalance(context.issuerAddress)
    } else if (account_type == "generic_alice") {
        context.aliceAccountUsername = username
        context.aliceWallet = wallet;
        context.aliceAddress = context.aliceWallet.address;
        context.aliceBalance = await context.client.getXrpBalance(context.aliceAddress)
    } else if (account_type == "generic_bob") {
        context.bobAccountUsername = username
        context.bobWallet = wallet;
        context.bobAddress = context.bobWallet.address;
        context.bobBalance = await context.client.getXrpBalance(context.bobAddress)
    } else if (account_type == "generic_carol") {
        context.carolAccountUsername = username
        context.carolWallet = wallet;
        context.carolAddress = context.carolWallet.address;
        context.carolBalance = await context.client.getXrpBalance(context.carolAddress)
    } else if (account_type == "invalid") {
        context.invalidAccountUsername = username
        context.invalidWallet = wallet;
        context.invalidAddress = "invalid";
        context.invalidBalance = 0
    } else {
        throw new Error("'{}' is not a valid accountType. Valid options are: 'source' and 'destination'.".format(account_type))
    }
});

async function get_fee(context) {
    let fee_request = ObjFactory.getObj(ObjType.Fee)
    let fee_response = await (context.client.request(fee_request))
    return fee_response.result["drops"]["base_fee"]
}

async function get_test_genesis_wallet(context) {
    let test_genesis_account_id = "rh1HPuRVsYYvThxG2Bs1MfjmrVC73S16Fb"
    let test_genesis_account_seed = "snRzwEoNTReyuvz6Fb1CDXcaJUQdp"
    let test_genesis_wallet = await Wallet.fromSeed(test_genesis_account_seed, algorithm = context.crypto_algorithm)
    if (is_network_local(context)) {
        if (!await does_account_exist(context, test_genesis_account_id)) {
            let master_account_seed = "snoPBrXtMeMyMHUVTgbuqAfg1SUTb"
            let master_genesis_wallet = await Wallet.fromSeed(master_account_seed, algorithm = context.crypto_algorithm)
            await send_payment(context, master_genesis_wallet, test_genesis_wallet, constants.DEFAULT_TEST_GENESIS_ACCOUNT_FUND)
        }
    } else {
        if (!await does_account_exist(context, test_genesis_account_id)) {
            throw new Error("Genesis account is not created. Please create and fund the account first.")
        }
    }
    return test_genesis_wallet
}

function is_network_local(context) {
    return context.url.includes("127.0.0") || context.url.includes("localhost")
}

async function does_account_exist(context, account_id) {
    try {
        await get_account_info_response(context, account_id)
        return true
    } catch (error) {
        return false
    }
}


async function generate_wallet_info(context, fund = true, fund_amount = constants.DEFAULT_ACCOUNT_FUND_AMOUNT) {
    let wallet = Wallet.generate(context.crypto_algorithm)
    if (fund) {
        await send_payment(context, context.test_genesis_wallet, wallet, xrpl.xrpToDrops(fund_amount))
    }
    return wallet
}

async function send_payment(context, source_wallet, destination_wallet, amount) {
    let response = null
    for (i = 1; i <= 5; i++) {
        try {
            let payload = ObjFactory.getObj(
                ObjFactory.ObjType.Payment,
                {
                    Account: source_wallet.address,
                    Destination: destination_wallet.address,
                    Amount: amount,
                    Sequence: await get_account_sequence(context, source_wallet.address)
                }
            );
            response = await sign_autofill_and_submit(context, payload, source_wallet)
        } catch (error) {
            sleep(1000)
            continue
        }
        break
    }
    return response
}

async function getClient() {
    let client = null
    context.url = `${context.connectionScheme}://${context.connectionUrl}`;
    if (context.connectionType == "websocket") {
        client = new xrpl.Client(context.url, {
            feeCushion: 1
        });
        await client.connect()
    } else {
        throw "Unsupported CONNECTION_TYPE = '" + context.connectionType + "'";
    }
    return client;
}

async function get_account_info_response(context, account_id) {
    let account_info_request = ObjFactory.getObj(
        ObjType.AccountInfo,
        {
            account: account_id
        }
    )
    return await (context.client.request(account_info_request))
}

async function abc(abc, def) {

}

const ResponseCode = {
    success: "tesSUCCESS",
    path_dry: "tecPATH_DRY",
    no_destination: "tecNO_DST",
    no_line_redundant: "tecNO_LINE_REDUNDANT",
    path_partial: "tecPATH_PARTIAL",
    unfunded_offer: "tecUNFUNDED_OFFER",
    insufficient_reserve: "tecINSUFFICIENT_RESERVE",
    no_permission: "tecNO_PERMISSION",
    has_obligations: "tecHAS_OBLIGATIONS",
    no_entry: "tecNO_ENTRY",
    unfunded_payment: "tecUNFUNDED_PAYMENT",

}

async function sleep(timeout_in_ms) {
    await new Promise(r => setTimeout(r, timeout_in_ms));
}

async function verify_transaction_validity(context, response = null, tx_id = null, engine_result = "tesSUCCESS", max_timeout = 30000) {
    let is_tx_valid = false
    let perform_txn_validation = false
    if (tx_id != null) {
        perform_txn_validation = true
    } else if (response) {
        tx_id = response.result["hash"]

        if ("engine_result" in response.result) {
            if ((response.result["engine_result"] == "tesSUCCESS") || (response.result["engine_result"] == "terQUEUED") || (response["engine_result"] == "tecKILLED")) {
                perform_txn_validation = true
            }
        } else if (response.status == "success") {
            perform_txn_validation = true
        }
    }

    if (perform_txn_validation) {
        let start_time = Date.now()
        let transaction_result = null
        while ((Date.now() - start_time) <= max_timeout) {
            let tx_response = await get_tx_response(context, tx_id)
            if (JSON.stringify(tx_response.result).includes("validated")) {
                if (JSON.stringify(tx_response.result).includes("meta")) {
                    transaction_result = tx_response.result["meta"]["TransactionResult"]
                }
                if (tx_response.result["validated"] == "true") {
                    if (transaction_result == engine_result) {
                        is_tx_valid = true
                        break
                    }
                }
            }
            await sleep(1000)
        }
    }
    if (!is_tx_valid) {
        return false
    }
}

async function get_nfts(context, account_id, ledger_index = "validated") {
    let account_nfts_request = ObjFactory.getObj(
        ObjType.account_nfts,
        {
            "account": account_id,
            "ledger_index": ledger_index
        }
    )
    let account_nfts = context.client.request(account_nfts_request)
    let nfts = []
    for (let account_nft in account_nfts["account_nfts"]) {
        let nft_token = item['NFTokenID']
        nfts.push(nft_token)
    }
    return nfts
}

async function get_account_nfts(context, account_id, ledger_index = "validated") {
    let account_nfts_request = ObjFactory.getObj(
        ObjType.account_nfts,
        {
            "command": "account_nfts",
            "account": account_id,
            "ledger_index": ledger_index
        }
    )
    return context.client.request(account_nfts_request)
}


async function get_nft_tokens(context, account_address) {
    let account_nfts = (await get_account_nfts(context, account_address)).result["account_nfts"]
    let nft_tokens = []
    for (const account_nft of account_nfts) {
        let nft_token = account_nft['NFTokenID']
        nft_tokens.push(nft_token)
    }
    return nft_tokens
}

async function wait_for_ledger_to_advance_for_account_delete(context, account_address, transaction_count = 256) {
    console.log("\tWaiting for ledger advance...")
    await advance_ledger_with_transactions(context, transaction_count)
    let count = 1
    let account_1_sequence = 0
    let ledger_sequence = 0
    while ((ledger_sequence - account_1_sequence) <= transaction_count) {
        account_1_sequence = await get_account_sequence(context, account_address)
        ledger_sequence = await get_ledger_current_index(context)
        if ((count % 60) == 1) {
            await sleep(1000);
        }
        count += 1
    }
    console.log("\tLedger advance complete...")
}

async function get_ledger_current_index(context) {
    return (await get_ledger_current_response(context)).result.ledger_current_index
}

async function advance_ledger_with_transactions(context, transaction_count) {
    let source_wallet = await generate_wallet_info(context, true, xrpl.dropsToXrp(constants.DEFAULT_ACCOUNT_FUND_AMOUNT));
    let destination_wallet = await generate_wallet_info(context, true, xrpl.dropsToXrp(constants.DEFAULT_ACCOUNT_FUND_AMOUNT));
    let payload
    console.log("\tAdvancing the ledger with transactions... " + transaction_count.toString() + " transactions...")
    for (let i = 0; i < transaction_count + 1; i++) {
        payload = await context.client.autofill(
            ObjFactory.getObj(
                "payment",
                {
                    "Account": source_wallet.address,
                    "Destination": destination_wallet.address,
                    "Amount": "10",
                    "Sequence": await get_account_sequence(context, source_wallet.address)
                }
            )
        );
        await sign_autofill_and_submit(context, payload, source_wallet)
    }
    console.log("\tDone");
}

async function get_account_objects_response(context, account_address, max_timeout = 5000) {
    let start_time = Date.now()
    let account_objects = null
    while ((Date.now() - start_time) <= max_timeout && account_objects == null) {
        let account_objects_request = ObjFactory.getObj(
            ObjType.AccountObjects,
            {
                account: account_address
            }
        )
        try {
            account_objects = await (context.client.request(account_objects_request))
        } catch (error) {
        }
    }
    return account_objects
}

async function get_account_lines_response(context, account_id, ledger_index = "validated") {
    let account_lines
    let account_lines_request = ObjFactory.getObj(
        ObjType.AccountLines,
        {
            account: account_id,
            ledger_index: ledger_index
        }
    )
    account_lines = await (context.client.request(account_lines_request))
    return account_lines
}

async function get_tx_response(context, tx_id) {
    let tx
    let tx_request = ObjFactory.getObj(
        ObjType.Tx,
        {
            transaction: tx_id,
            binary: false
        }
    )
    tx = await (context.client.request(tx_request))
    return tx
}

async function get_account_nfts_response(context, account_id) {
    let account_nfts
    let account_nfts_request = ObjFactory.getObj(
        ObjType.AccountNFTs,
        {
            account: account_id
        }
    )
    account_nfts = await (context.client.request(account_nfts_request))
    return account_nfts
}

async function get_ledger_current_response(context) {
    let ledger_current
    let ledger_current_request = ObjFactory.getObj(ObjType.LedgerCurrent)
    ledger_current = await (context.client.request(ledger_current_request))
    return ledger_current
}

async function get_account_info(context, account_address) {
    return await get_account_info_response(context, account_address)
}

async function get_account_sequence(context, account_address) {
    return (await get_account_info(context, account_address)).result.account_data.Sequence
}

async function generate_issued_currency_amount(value, issuer, currency = "USD") {
    return {
        value: value,
        issuer: issuer,
        currency: currency
    }
}

async function generate_path_step(issuer = undefined, currency = undefined) {
    if (issuer == undefined && currency != undefined) {
        return {
            currency: currency
        }
    } else if (issuer != undefined && currency == undefined) {
        return {
            issuer: issuer,
        }
    } else {
        return {
            issuer: issuer,
            currency: currency
        }
    }
}

async function get_account_balance(context, account_id) {
    if (!account_id) {
        throw new Error("Cannot get account balance. Account ID is invalid.")
    }
    let balance = await context.client.getXrpBalance(account_id)
    return balance
}

async function verify_trustline_account_objects(context, response, engine_result = ResponseCode.success) {
    if (response) {
        await verify_transaction_validity(context, response = response, tx_id = null, engine_result = engine_result)
        await verify_response_code(response, engine_result)

        let account_id = response.result["Owner"] != undefined ? response.result["Owner"] : response.result["Account"]
        let transaction_type = response.result["TransactionType"]
        let account_objects_response = await get_account_objects_response(context, account_id)
        if (account_objects_response == null || account_objects_response.status != 'error') { // if(!account_objects_response) {
            return
        }
        assert.strictEqual(account_id, account_objects_response.result['account'])
        for (const account_object of account_objects_response.result["account_objects"]) {
            if (transaction_type == "TrustSet") {
                assert.strictEqual(account_object['LedgerEntryType'], "RippleState")
                assert(!JSON.stringify(account_object['LedgerEntryType']).includes(transaction_type), "Account object created for Transaction Type: " + transaction_type)
            }
        }
    }
}

async function verify_payment_account_objects(context, response) {
    let account_id = response.result["Owner"] != undefined ? response.result["Owner"] : response.result["Account"]
    let transaction_type = response.result["TransactionType"]
    let account_objects_response = await get_account_objects_response(context, account_id)
    if (account_objects_response == null || account_objects_response.status != 'error') { // if(!account_objects_response) {
        return
    }
    for (const account_object of account_objects_response.result["account_objects"]) {
        assert(!JSON.stringify(account_object['LedgerEntryType']).includes(transaction_type), "Account object created for Transaction Type: " + transaction_type)
    }
}

async function verify_offer_create_account_objects(context, response, offer_crossing = undefined, engine_result = ResponseCode.success) {
    if (response) {
        await verify_transaction_validity(context, response = response, tx_id = null, engine_result = engine_result)
        await verify_response_code(response, engine_result)

        let SIDECHAIN_IGNORE_VALIDATION = "auto-submitted"
        if (response == SIDECHAIN_IGNORE_VALIDATION) {
            return
        }

        if (JSON.stringify(response.result).includes("engine_result_code")) {
            if (JSON.stringify(response.result["engine_result_code"]) != 0 && JSON.stringify(response.result["engine_result_code"]) != 150) {
                return
            }
        } else {
            if (response.status != "success" || !JSON.stringify(response).includes("tx_json")) {
                return;
            }
        }
        let account_id
        if (response.result["Owner"]) {
            account_id = response.result["Owner"]
        } else {
            account_id = response.result["Account"]
        }
        if (account_id == null) {
            throw new Error("Account ID could not be retrieved.")
        }

        let transaction_type = response.result["TransactionType"]
        let account_objects_response = await get_account_objects_response(context, account_id)
        if (account_objects_response == null || account_objects_response.status != 'error') {
            return
        }
        assert(account_objects_response, "Account object not created in ledger")
        assert(response.result["Account"] == account_objects_response.result['account'], "Account name is not correct")

        let offer_crossing_status = False
        for (const account_object of account_objects_response.result["account_objects"]) {
            if (offer_crossing === true) {
                if (account_object['LedgerEntryType'] == "RippleState") {
                    offer_crossing_status = true
                }
            } else if (offer_crossing === false) {
                if (account_object['LedgerEntryType'] == "Offer") {
                    offer_crossing_status = true
                }
            } else {
                if (account_object['LedgerEntryType'] == "Offer") {
                    offer_crossing_status = true
                }
            }
        }

        assert(offer_crossing_status, "Offer Crossing Status is invalid")
    }
}

async function verify_response_code(response, expected_code) {
    assert(JSON.stringify(response.result).includes(expected_code), "Expected response code was not received. " +
        "\nExpected Code = " + expected_code + ". \nResponse received: " + JSON.stringify(response.result))
}


async function verify_offer_create_account_objects(context, response, offer_crossing = null, engine_result = ResponseCode.success) {
    if (response) {
        await verify_transaction_validity(context, response = response, tx_id = null, engine_result = engine_result)
        await verify_response_code(response, engine_result)
        let perform_account_object_verification = true

        if ("engine_result_code" in response.result && response.result["engine_result_code"] != 0 && response.result["engine_result_code"] != 150) {
            perform_account_object_verification = false
        } else if ((response.status != "success") || (!JSON.stringify(response).includes("tx_json"))) {
            perform_account_object_verification = false
        }

        if (perform_account_object_verification) {
            let account_id

            if (response.result["Owner"]) {
                account_id = response.result["Owner"]
            } else {
                account_id = response.result["Account"]
            }
            if (account_id == null) {
                throw new Error("Account ID could not be retrieved.")
            }

            let transaction_type = response.result["TransactionType"]
            if (transaction_type == "OfferCreate") {
                let account_objects_response = await get_account_objects_response(context, account_id)
                if (account_objects_response == null || account_objects_response.status != 'error') { // if(!account_objects_response) {
                    return
                }

                if (account_objects_response != null && account_objects_response.status != 'error') {
                    assert.strictEqual(account_objects_response, true, "Account object not created in ledger")
                    assert.strictEqual(response.result["Account"], account_objects_response.result['account'], "Account name is not correct")

                    let offer_crossing_status = false
                    for (let account_object of account_objects_response.result["account_objects"]) {
                        if (offer_crossing == null) {
                            if (account_object['LedgerEntryType'] == "Offer") {
                                offer_crossing_status = true
                            }
                        } else if (offer_crossing) {
                            if (account_object['LedgerEntryType'] == "RippleState") {
                                offer_crossing_status = true
                            }
                        } else if (!offer_crossing) {
                            if (account_object['LedgerEntryType'] == "Offer") {
                                offer_crossing_status = true
                            }
                        }
                    }
                    assert.strictEqual(offer_crossing_status, true)
                }
            }
        }
    }
}


async function verify_account_delete_account_objects(context, response, engine_result = ResponseCode.success) {
    if (response) {
        await verify_transaction_validity(context, response = response, tx_id = null, engine_result = engine_result)
        await verify_response_code(response, engine_result)
        let account_id = null
        if (response.result["Owner"]) {// != undefined) {
            account_id = response.result["Owner"]
        } else {
            account_id = response.result["Account"]
        }
        if (account_id == null) {
            throw new Error("Account ID could not be retrieved.")
        }
        let hash_from_previous_txn = response.result["hash"]
        let transaction_type = response.result["TransactionType"]
        let object_removed = false
        let account_objects_response = await get_account_objects_response(context, account_id)
        if (account_objects_response == null || account_objects_response.status != 'error') { // if(!account_objects_response) {
            return
        }
        if (transaction_type == "AccountDelete") {
            if ((JSON.stringify(account_objects_response.result).includes("error")) && (account_objects_response.result["error"] == "actNotFound")) {
                object_removed = true
            }
            assert.strictEqual(object_removed, true, "account object not cleared for txn " + hash_from_previous_txn.toString())
            if (account_objects_response != null && account_objects_response.status != 'error') {
                assert.strictEqual(account_id, account_objects_response.result['account'])
                for (let account_object of account_objects_response.result["account_objects"]) {
                    assert.strictEqual(account_object['LedgerEntryType'], "RippleState")

                    // TODO: Failing for some tests
                    assert.strictEqual(JSON.stringify(account_object['LedgerEntryType']).includes(transaction_type), false, "Account object created for Transaction Type: {}".format(transaction_type))
                }
            }
        }
    }
}

async function verify_ticket_create_account_objects(context, response, engine_result = ResponseCode.success) {
    if (response) {
        await verify_transaction_validity(context, response = response, tx_id = null, engine_result = engine_result)
        await verify_response_code(response, engine_result)
        let account_id
        if (response.result["Owner"]) {
            account_id = response.result["Owner"]
        } else {
            account_id = response.result["Account"]
        }
        if (account_id == null) {
            throw new Error("Account ID could not be retrieved.")
        }
        let transaction_type = response.result["TransactionType"]

        let perform_account_object_verification;
        if ("engine_result_code" in response.result && response.result["engine_result_code"] != 0 && response.result["engine_result_code"] != 150) {
            perform_account_object_verification = false
        } else if ((response.status != "success") || (!JSON.stringify(response).includes("tx_json"))) {
            perform_account_object_verification = false
        }
        if (perform_account_object_verification) {
            let account_objects_response = await get_account_objects_response(context, account_id)
            if (account_objects_response == null || account_objects_response.status != 'error') { // if(!account_objects_response) {
                return
            }
            if (account_objects_response != null && account_objects_response.status != 'error') {
                assert.strictEqual(account_id, account_objects_response.result['account'])
                for (let account_object of account_objects_response.result["account_objects"]) {
                    assert.strictEqual(transaction_type == account_object['LedgerEntryType'], true)
                }
            }
        }
    }
}

async function verify_nftoken_burn_account_objects(context, response, engine_result = ResponseCode.success) {
    if (response) {
        await verify_transaction_validity(context, response = response, tx_id = null, engine_result = engine_result)
        await verify_response_code(response, engine_result)

        let account_id
        if (response.result["Owner"]) {
            account_id = response.result["Owner"]
        } else {
            account_id = response.result["Account"]
        }
        if (account_id == null) {
            throw new Error("Account ID could not be retrieved.")
        }
        let hash_from_previous_txn = response.result["hash"]
        let transaction_type = response.result["TransactionType"]
        let object_removed = false
        let deleted_node_found = false
        let account_objects_response
        let previous_txn_id = null
        let ledger_index = null
        account_objects_response = await get_account_objects_response(context, account_id)
        if (account_objects_response == null || account_objects_response.status != 'error') { // if(!account_objects_response) {
            return
        }

        let account_object_found;
        if (account_objects_response != null && account_objects_response.status != 'error') {
            if ((account_objects_response.result["account_objects"] != null) && (transaction_type != "AccountDelete")) {
                object_removed = true
                deleted_node_found = true
            } else {
                let tx_response = await get_tx_response(hash_from_previous_txn)
                for (let affected_node of tx_response["meta"]["AffectedNodes"]) {
                    try {
                        if ((JSON.stringify(affected_node).includes("DeletedNode")) && (transaction_type == tx_response["TransactionType"])) {
                            deleted_node_found = true
                            ledger_index = affected_node["DeletedNode"]["LedgerIndex"]
                            previous_txn_id = affected_node["DeletedNode"]["FinalFields"]["PreviousTxnID"]
                            break
                        }
                    } catch (error) {
                    }
                }

                for (let account_object of account_objects_response.result["account_objects"]) {
                    if ((account_object["index"] == ledger_index) || (account_object["PreviousTxnID"] == previous_txn_id)) {
                        if ((transaction_type == "OfferCancel") && (account_object["LedgerEntryType"] == "RippleState")) {
                            break
                        } else {
                            account_object_found = true
                            break
                        }
                    }
                }

                if ((previous_txn_id != null) && (!account_object_found)) {
                    object_removed = true
                }
            }
            if (!object_removed && !deleted_node_found && !account_object_found) {
                assert.strictEqual(previous_txn_id, null, "DeletedNode created for transaction type: " + transaction_type)
            } else {
                assert.strictEqual(object_removed, true, "account object not cleared for txn " + hash_from_previous_txn)
            }
        }
    }
}

async function verify_nftoken_mint_account_objects(context, response, engine_result = ResponseCode.success) {
    if (response) {
        await verify_transaction_validity(context, response = response, tx_id = null, engine_result = engine_result)
        await verify_response_code(response, engine_result)

        let account_id
        if (response.result["Owner"]) {
            account_id = response.result["Owner"]
        } else {
            account_id = response.result["Account"]
        }
        if (account_id == null) {
            throw new Error("Account ID could not be retrieved.")
        }
        let transaction_type = response.result["TransactionType"]
        let hash_from_previous_txn = response.result["hash"]
        let perform_account_object_verification = true
        let nft_tokens = null

        if ("engine_result_code" in response.result && response.result["engine_result_code"] != 0 && response.result["engine_result_code"] != 150) {
            perform_account_object_verification = false
        } else if (response.status != "success" || !JSON.stringify(response).includes("tx_json")) {
            perform_account_object_verification = false
        }

        if (perform_account_object_verification) {
            if (transaction_type == "NFTokenMint") {
                nft_tokens = await get_nfts(context, account_id)
                assert.strictEqual(nft_tokens != null, true, "nft_tokens not found")

                let non_fungible_tokens = []
                let tx_response = await get_tx_response(hash_from_previous_txn)

                for (let affected_node of tx_response.result["meta"]["AffectedNodes"]) {
                    try {
                        if ((JSON.stringify(affected_node).includes("CreatedNode") && (affected_node["CreatedNode"]["LedgerEntryType"] == "NFTokenPage"))) {
                            let non_fungible_tokens_object = affected_node["CreatedNode"]["NewFields"]["NFTokens"]
                            assert.strictEqual(non_fungible_tokens_object.length <= constants.MAX_NFTOKEN_PAGE_OBJECTS_LIMIT, true, "NFToken page objects more than " + constants.MAX_NFTOKEN_PAGE_OBJECTS_LIMIT)
                            for (let item of non_fungible_tokens_object) {
                                let non_fungible_token = item["NFToken"]["NFTokenID"]
                                non_fungible_tokens.push(non_fungible_token)
                            }
                        }

                        if (("ModifiedNode") in affected_node && affected_node["ModifiedNode"]["LedgerEntryType"] == "NFTokenPage") {
                            let non_fungible_tokens_object = affected_node["ModifiedNode"]["FinalFields"]["NFTokens"]
                            assert.strictEqual(non_fungible_tokens_object.length <= constants.MAX_NFTOKEN_PAGE_OBJECTS_LIMIT, true, "NFToken page objects more than " + constants.MAX_NFTOKEN_PAGE_OBJECTS_LIMIT)

                            for (let item of non_fungible_tokens_object) {
                                let non_fungible_token = item["NFToken"]["NFTokenID"]
                                non_fungible_tokens.push(non_fungible_token)
                            }
                        }
                    } catch (error) {
                    }
                }

                if (nft_tokens.length <= constants.MAX_NFTOKEN_PAGE_OBJECTS_LIMIT) {
                    assert.strictEqual(JSON.stringify(non_fungible_tokens) == JSON.stringify(nft_tokens), true, "Non Fungible Token object count mismatch")
                }
            }
        }
    }
}


function verify_account_balance(actual_amount, expected_amount) {
    assert.equal(parseFloat(actual_amount).toFixed(6), parseFloat(expected_amount).toFixed(6), "Account balance is incorrect. \nExpected: " + expected_amount + "\nActual: " + actual_amount)
}

function verify_test_status(actual_status, expected_status) {
    assert.equal(actual_status, expected_status, "Test Status is incorrect. \nExpected: " + expected_status + "\nActual: " + actual_status)
}

function verify_test_error_message(actual_error, expected_error) {
    assert.match(actual_error, expected_error, "Incorrect error message received. \nExpected: " + expected_error + "\nActual: " + actual_error)
}


function verify_response_code(response, expected_code) {
    if (response != null && response != '') {
        assert.strictEqual(JSON.stringify(response.result).includes(expected_code), true, "Expected response code was not received. \nExpected Code = " + expected_code + ". \nResponse received: " + JSON.stringify(response.result))
    }
}


async function verify_not_creating_objects_type_account_objects(context, response, engine_result = ResponseCode.success) {
    if (response) {
        await verify_transaction_validity(context, response = response, tx_id = null, engine_result = engine_result)
        await verify_response_code(response, engine_result)

        let account_id
        if (response.result["Owner"]) {
            account_id = response.result["Owner"]
        } else {
            account_id = response.result["Account"]
        }
        if (account_id == null) {
            throw new Error("Account ID could not be retrieved.")
        }
        let transaction_type = response.result["TransactionType"]
        let account_objects_response = await get_account_objects_response(context, account_id)
        if (account_objects_response == null || account_objects_response.status != 'error') { // if(!account_objects_response) {
            return
        }
        if (account_objects_response != null && account_objects_response.status != 'error') {
            for (let account_object of account_objects_response.result["account_objects"]) {
                assert.strictEqual(JSON.stringify(account_object['LedgerEntryType']).includes(transaction_type), false, "Account object created for Transaction Type: " + transaction_type)
            }
        }
    }
}

async function verify_payment_account_objects(context, response, engine_result = ResponseCode.success) {
    await verify_not_creating_objects_type_account_objects(context, response, engine_result)
}

async function verify_account_set_account_objects(context, response, engine_result = ResponseCode.success) {
    await verify_not_creating_objects_type_account_objects(context, response, engine_result)
}

async function sign_and_submit(context, payload, wallet) {
    let signed_request = wallet.sign(payload).tx_blob;
    let response = await context.client.submitAndWait(signed_request);
    return response
}

async function sign_autofill_and_submit(context, payload, wallet) {
    let autofilled_payload = await context.client.autofill(payload)
    let response = await sign_and_submit(context, autofilled_payload, wallet)
    return response
}

async function get_ticket_sequence(context, account_address) {
    let account_objects = (await get_account_objects_response(context, account_address)).result["account_objects"]
    let ticket_sequences = []
    for (let account_object of account_objects) {
        if (account_object["LedgerEntryType"] == "Ticket") {
            ticket_sequences.push(account_object['TicketSequence'])
        }
    }
    return ticket_sequences
}


module.exports = {
    ResponseCode,
    get_account_balance,
    sleep,
    get_tx_response,
    verify_transaction_validity,
    get_nfts,
    get_account_nfts,
    get_nft_tokens,
    wait_for_ledger_to_advance_for_account_delete,
    get_ledger_current_index,
    advance_ledger_with_transactions,
    send_payment,
    get_account_objects_response,
    get_account_lines_response,
    get_tx_response,
    get_account_nfts_response,
    get_ledger_current_response,
    get_account_info,
    get_account_sequence,
    generate_issued_currency_amount,
    generate_path_step,
    sign_autofill_and_submit,
    verify_trustline_account_objects,
    verify_payment_account_objects,
    verify_offer_create_account_objects,
    verify_response_code,
    verify_offer_create_account_objects,
    verify_account_delete_account_objects,
    verify_ticket_create_account_objects,
    verify_nftoken_burn_account_objects,
    verify_nftoken_mint_account_objects,
    verify_account_balance,
    verify_response_code,
    verify_not_creating_objects_type_account_objects,
    verify_payment_account_objects,
    verify_account_set_account_objects,
    sign_and_submit,
    get_ticket_sequence,
    verify_test_status,
    verify_test_error_message,
}

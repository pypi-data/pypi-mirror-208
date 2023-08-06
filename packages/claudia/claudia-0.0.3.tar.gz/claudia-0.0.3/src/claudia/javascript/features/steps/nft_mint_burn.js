const {BeforeAll, AfterAll, Given, When, Then, Before, After} = require('@cucumber/cucumber')
const xrpl = require("xrpl");
const {AccountSetAsfFlags, convertStringToHex, NFTokenMintFlags} = require("xrpl");
const {} = require('../context.js');
let context = require('../context.js');
const assert = require('assert');
const ObjFactory = require("../lib/ObjFactory");
const {ObjType} = require("../lib/ObjFactory");
const constants = require("./constants");
const {
    sign_autofill_and_submit,
    verify_account_balance,
    verify_nftoken_mint_account_objects,
    verify_nftoken_burn_account_objects,
    verify_account_set_account_objects,
    verify_ticket_create_account_objects,
    verify_account_delete_account_objects,
    verify_payment_account_objects,
    ResponseCode,
    send_payment,
    get_account_sequence,
    get_ticket_sequence,
    get_account_balance,
    get_nft_tokens,
    wait_for_ledger_to_advance_for_account_delete, get_account_info,
    sign_and_submit
} = require("./common");
const crypto = require("crypto");


When('we mint NFT using same token taxon', {timeout: 180000}, async () => {
    try {
        let payload = ObjFactory.getObj(ObjType.NFTokenMint,
            {
                Account: context.sourceAddress, NFTokenTaxon: 0,
            })
        context.nft_mint_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)
        context.nft_mint_response_2 = await sign_autofill_and_submit(context, payload, context.sourceWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
        throw error
    }
});

Then('nft minting is successful', {timeout: 180000}, async () => {
    verify_account_balance(await get_account_balance(context, context.sourceAddress), parseFloat(context.sourceBalance) - xrpl.dropsToXrp(2 * context.minDrop))
    await verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)
    await verify_nftoken_mint_account_objects(context, context.nft_mint_response_2)
});


When('we mint NFT with low reserves', {timeout: 180000}, async () => {
    try {
        context.sourceBalance = await get_account_balance(context, context.sourceAddress)

        let payload = ObjFactory.getObj(ObjType.NFTokenMint,
            {
                Account: context.sourceAddress, NFTokenTaxon: 0,
            })
        context.nft_mint_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
        throw error
    }
});

Then('nft minting with low reserves is not successful', {timeout: 180000}, async () => {
    verify_account_balance(await get_account_balance(context, context.sourceAddress), parseFloat(context.sourceBalance) - (xrpl.dropsToXrp(context.minDrop)))
    await verify_nftoken_mint_account_objects(context, context.nft_mint_response_1, ResponseCode.insufficient_reserve)
});

When('we mint NFT with optional URI as a string', {timeout: 180000}, async () => {
    try {
        let payload = ObjFactory.getObj(ObjType.NFTokenMint,
            {
                Account: context.sourceAddress,
                NFTokenTaxon: 0,
                URI: "ipfs://bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi"
            })
        context.nft_mint_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
    }
});

Then('nft minting with optional URI as a string is not successful', {timeout: 180000}, async () => {
    assert.equal(context.testStatus, "failed", "Test Status is incorrect")
    assert.match(context.exception.toString(), /URI must be a hex value/, "Incorrect error message received.")
    verify_account_balance(await get_account_balance(context, context.sourceAddress), parseFloat(context.sourceBalance))
});

When('we mint NFT with optional URI as a hex string', {timeout: 180000}, async () => {
    try {
        let hex_uri = convertStringToHex("ipfs://bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi")
        let payload = ObjFactory.getObj(ObjType.NFTokenMint,
            {
                Account: context.sourceAddress, NFTokenTaxon: 0, URI: hex_uri
            })
        context.nft_mint_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
        throw error
    }
});

Then('nft minting with optional URI as a hex string is not successful', {timeout: 180000}, async () => {
    verify_account_balance(await get_account_balance(context, context.sourceAddress), parseFloat(context.sourceBalance) - xrpl.dropsToXrp(context.minDrop))
    await verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)
});

When('we mint NFT with invalid URI', {timeout: 180000}, async () => {
    try {
        let hex_uri = convertStringToHex("")
        let payload = ObjFactory.getObj(ObjType.NFTokenMint,
            {
                Account: context.sourceAddress, NFTokenTaxon: 0, URI: hex_uri
            })
        context.nft_mint_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
    }
});

Then('nft minting with invalid URI is not successful', {timeout: 180000}, async () => {
    assert.equal(context.testStatus, "failed", "Test Status is incorrect")
    assert.match(context.exception.toString(), /Preliminary result: temMALFORMED/, "Incorrect error message received.")
    verify_account_balance(await get_account_balance(context, context.sourceAddress), parseFloat(context.sourceBalance))
});

When('we mint NFT with optional URI with more than 265 characters', {timeout: 180000}, async () => {
    try {
        var crypto = require("crypto");
        var uri = "ipfs://" + crypto.randomBytes(257).toString()
        let hex_uri = convertStringToHex(uri)
        let payload = ObjFactory.getObj(ObjType.NFTokenMint,
            {
                Account: context.sourceAddress, NFTokenTaxon: 0, URI: hex_uri
            })
        context.nft_mint_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
    }
});

Then('nft minting with optional URI with more than 265 characters is not successful', {timeout: 180000}, async () => {
    assert.equal(context.testStatus, "failed", "Test Status is incorrect")
    assert.match(context.exception.toString(), /Preliminary result: temMALFORMED/, "Incorrect error message received.")
    verify_account_balance(await get_account_balance(context, context.sourceAddress), parseFloat(context.sourceBalance))
});

When('we mint NFT with optional {string} transfer fee', {timeout: 180000}, async (transfer_fee) => {
    try {
        let payload = ObjFactory.getObj(ObjType.NFTokenMint,
            {
                Account: context.sourceAddress, NFTokenTaxon: 0,
                TransferFee: transfer_fee, Flags: NFTokenMintFlags.tfTransferable
            })
        context.nft_mint_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
    }
});

Then('nft minting with optional negative transfer fee is not successful', {timeout: 180000}, async () => {
    assert.equal(context.testStatus, "failed", "Test Status is incorrect")
    assert.match(context.exception.toString(), /Can not construct UInt16 with given value/, "Incorrect error message received.")
    verify_account_balance(await get_account_balance(context, context.sourceAddress), parseFloat(context.sourceBalance))
});

Then('nft minting with optional zero transfer fee is successful', {timeout: 180000}, async () => {
    assert.equal(context.testStatus, "failed", "Test Status is incorrect")
    assert.match(context.exception.toString(), /Can not construct UInt16 with given value/, "Incorrect error message received.")
    verify_account_balance(await get_account_balance(context, context.sourceAddress), parseFloat(context.sourceBalance))
});

Then('nft minting with optional transfer fee in decimal is not successful', {timeout: 180000}, async () => {
    assert.equal(context.testStatus, "failed", "Test Status is incorrect")
    assert.match(context.exception.toString(), /Can not construct UInt16 with given value/, "Incorrect error message received.")
    verify_account_balance(await get_account_balance(context, context.sourceAddress), parseFloat(context.sourceBalance))
});

Then('nft minting with optional transfer fee more than 50000 is not successful', {timeout: 180000}, async () => {
    assert.equal(context.testStatus, "failed", "Test Status is incorrect")
    assert.match(context.exception.toString(), /Can not construct UInt16 with given value/, "Incorrect error message received.")
    verify_account_balance(await get_account_balance(context, context.sourceAddress), parseFloat(context.sourceBalance))
});

When('we mint NFT without tfTransferable flag', {timeout: 180000}, async () => {
    try {
        let payload = ObjFactory.getObj(ObjType.NFTokenMint,
            {
                Account: context.sourceAddress, NFTokenTaxon: 0, TransferFee: 50,
            })
        context.nft_mint_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
    }
});

Then('nft minting without tfTransferable flag is not successful', {timeout: 180000}, async () => {
    assert.equal(context.testStatus, "failed", "Test Status is incorrect")
    assert.match(context.exception.toString(), /Preliminary result: temMALFORMED/, "Incorrect error message received.")
    verify_account_balance(await get_account_balance(context, context.sourceAddress), parseFloat(context.sourceBalance))
});

When('we mint NFT with optional memos', {timeout: 180000}, async () => {
    try {
        let hex_uri = convertStringToHex("ipfs://bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylqabf3oclgtqy55fbzdi")
        let payload = ObjFactory.getObj(ObjType.NFTokenMint,
            {
                Account: context.sourceAddress, NFTokenTaxon: 0,
                Memos: [{
                    Memo: {
                        MemoType: '687474703A2F2F6578616D706C652E636F6D2F6D656D6F2F67656E65726963',
                        MemoData: '72656E74',
                    },
                }],
                URI: hex_uri
            })
        context.nft_mint_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
        throw error
    }
});

Then('nft minting with optional memos is successful', {timeout: 180000}, async () => {
    verify_account_balance(await get_account_balance(context, context.sourceAddress), parseFloat(context.sourceBalance) - xrpl.dropsToXrp(context.minDrop))
    await verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)
});

When('we mint NFT with bad seed', {timeout: 180000}, async () => {
    try {
        let payload = ObjFactory.getObj(ObjType.NFTokenMint,
            {
                Account: context.sourceAddress, NFTokenTaxon: 0,
            })
        context.nft_mint_response_1 = await sign_autofill_and_submit(context, payload, context.destinationWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
    }
});

Then('nft minting with bad seed is not successful', {timeout: 180000}, async () => {
    assert.equal(context.testStatus, "failed", "Test Status is incorrect")
    assert.match(context.exception.toString(), /Preliminary result: tefBAD_AUTH/, "Incorrect error message received.")
    verify_account_balance(await get_account_balance(context, context.sourceAddress), parseFloat(context.sourceBalance))
});

When('we mint NFT without nftoken_taxon', {timeout: 180000}, async () => {
    try {
        let payload = ObjFactory.getObj(ObjType.NFTokenMint,
            {
                Account: context.sourceAddress,
            })
        context.nft_mint_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
    }
});

Then('nft minting without nftoken_taxon is not successful', {timeout: 180000}, async () => {
    assert.equal(context.testStatus, "failed", "Test Status is incorrect")
    assert.match(context.exception.toString(), /Field 'NFTokenTaxon' is required but missing/, "Incorrect error message received.")
    verify_account_balance(await get_account_balance(context, context.sourceAddress), parseFloat(context.sourceBalance))
});

When('we mint NFT with negative nftoken_taxon', {timeout: 180000}, async () => {
    try {
        let payload = ObjFactory.getObj(ObjType.NFTokenMint,
            {
                Account: context.sourceAddress,
                NFTokenTaxon: -10,
            })
        context.nft_mint_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
    }
});

Then('nft minting with negative nftoken_taxon is not successful', {timeout: 180000}, async () => {
    assert.equal(context.testStatus, "failed", "Test Status is incorrect")
    assert.match(context.exception.toString(), /RangeError: "value" argument is out of bounds/, "Incorrect error message received.")
    verify_account_balance(await get_account_balance(context, context.sourceAddress), parseFloat(context.sourceBalance))
});

When('we mint NFT with too high nftoken_taxon', {timeout: 180000}, async () => {
    try {
        let payload = ObjFactory.getObj(ObjType.NFTokenMint,
            {
                Account: context.sourceAddress,
                NFTokenTaxon: 4294967296,
            })
        context.nft_mint_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
    }
});

Then('nft minting with too high nftoken_taxon is not successful', {timeout: 180000}, async () => {
    assert.equal(context.testStatus, "failed", "Test Status is incorrect")
    assert.match(context.exception.toString(), /RangeError: "value" argument is out of bounds/, "Incorrect error message received.")
    verify_account_balance(await get_account_balance(context, context.sourceAddress), parseFloat(context.sourceBalance))
});

When('we mint NFT without source account field', {timeout: 180000}, async () => {
    try {
        let payload = ObjFactory.getObj(ObjType.NFTokenMint,
            {
                NFTokenTaxon: 0,
            })
        context.nft_mint_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
    }
});

Then('nft minting without source account field is not successful', {timeout: 180000}, async () => {
    assert.equal(context.testStatus, "failed", "Test Status is incorrect")
    assert.match(context.exception.toString(), /Missing field 'account'./, "Incorrect error message received.")
    verify_account_balance(await get_account_balance(context, context.sourceAddress), parseFloat(context.sourceBalance))
});

When('we mint NFT with empty source account field', {timeout: 180000}, async () => {
    try {
        let payload = ObjFactory.getObj(ObjType.NFTokenMint,
            {
                Account: "",
                NFTokenTaxon: 0,
            })
        context.nft_mint_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
    }
});

Then('nft minting with empty source account field is not successful', {timeout: 180000}, async () => {
    assert.equal(context.testStatus, "failed", "Test Status is incorrect")
    assert.match(context.exception.toString(), /Missing field 'account'./, "Incorrect error message received.")
    verify_account_balance(await get_account_balance(context, context.sourceAddress), parseFloat(context.sourceBalance))
});

When('we mint NFT with same account as issuer', {timeout: 180000}, async () => {
    try {
        let payload = ObjFactory.getObj(ObjType.NFTokenMint,
            {
                Account: context.sourceAddress,
                Issuer: context.sourceAddress,
                NFTokenTaxon: 0,
            })
        context.nft_mint_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
    }
});

Then('nft minting with same account as issuer is not successful', {timeout: 180000}, async () => {
    assert.equal(context.testStatus, "failed", "Test Status is incorrect")
    assert.match(context.exception.toString(), /Preliminary result: temMALFORMED/, "Incorrect error message received.")
    verify_account_balance(await get_account_balance(context, context.sourceAddress), parseFloat(context.sourceBalance))
});

When('we mint NFT with invalid issuer', {timeout: 180000}, async () => {
    try {
        let payload = ObjFactory.getObj(ObjType.NFTokenMint,
            {
                Account: context.sourceAddress,
                Issuer: context.invalidAddress,
                NFTokenTaxon: 0,
            })
        context.nft_mint_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
    }
});

Then('nft minting with invalid issuer is not successful', {timeout: 180000}, async () => {
    assert.equal(context.testStatus, "failed", "Test Status is incorrect")
    assert.match(context.exception.toString(), /Non-base58 character/, "Incorrect error message received.")
    verify_account_balance(await get_account_balance(context, context.sourceAddress), parseFloat(context.sourceBalance))
});

When('we mint NFT with issuer having unauthorized user', {timeout: 180000}, async () => {
    try {
        let payload = ObjFactory.getObj(ObjType.AccountSet,
            {
                Account: context.sourceAddress,
                Sequence: await get_account_sequence(context, context.sourceAddress),
                Fee: "10",
                NFTokenMinter: context.destinationAddress,
            });
        context.account_set_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)

        payload = ObjFactory.getObj(ObjType.NFTokenMint,
            {
                Account: context.destinationAddress,
                Issuer: context.sourceAddress,
                NFTokenTaxon: 0,
            })
        context.nft_mint_response_1 = await sign_autofill_and_submit(context, payload, context.destinationWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
        throw error
    }
});

Then('nft minting with issuer having unauthorized user is not successful', {timeout: 180000}, async () => {
    verify_account_balance(await get_account_balance(context, context.sourceAddress), parseFloat(context.sourceBalance) - xrpl.dropsToXrp(context.minDrop))
    verify_account_balance(await get_account_balance(context, context.destinationAddress), parseFloat(context.destinationBalance) - xrpl.dropsToXrp(context.minDrop))
    await verify_nftoken_mint_account_objects(context, context.nft_mint_response_1, ResponseCode.no_permission)
    await verify_account_set_account_objects(context, context.account_set_response_1)

});

When('we mint NFT with issuer having authorized user', {timeout: 180000}, async () => {
    try {
        let payload = ObjFactory.getObj(ObjType.AccountSet,
            {
                Account: context.sourceAddress,
                Sequence: await get_account_sequence(context, context.sourceAddress),
                Fee: "10",
                SetFlag: AccountSetAsfFlags.asfAuthorizedNFTokenMinter,
                NFTokenMinter: context.destinationAddress,
            });
        context.account_set_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)

        payload = ObjFactory.getObj(ObjType.NFTokenMint,
            {
                Account: context.destinationAddress,
                Issuer: context.sourceAddress,
                NFTokenTaxon: 0,
            })
        context.nft_mint_response_1 = await sign_autofill_and_submit(context, payload, context.destinationWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
        throw error
    }
});

Then('nft minting with issuer having authorized user is successful', {timeout: 180000}, async () => {
    verify_account_balance(await get_account_balance(context, context.sourceAddress), parseFloat(context.sourceBalance) - xrpl.dropsToXrp(context.minDrop))
    verify_account_balance(await get_account_balance(context, context.destinationAddress), parseFloat(context.destinationBalance) - xrpl.dropsToXrp(context.minDrop))
    await verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)
    await verify_account_set_account_objects(context, context.account_set_response_1)
});

When('we mint NFT on ticket with authorized user', {timeout: 180000}, async () => {
    try {
        let payload = ObjFactory.getObj(ObjType.AccountSet,
            {
                Account: context.sourceAddress,
                Sequence: await get_account_sequence(context, context.sourceAddress),
                Fee: "10",
                SetFlag: AccountSetAsfFlags.asfAuthorizedNFTokenMinter,
                NFTokenMinter: context.destinationAddress,
            });
        context.account_set_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)

        payload = ObjFactory.getObj(ObjType.TicketCreate,
            {
                Account: context.destinationAddress,
                Sequence: await get_account_sequence(context, context.destinationAddress),
                TicketCount: 1,
            })
        context.tc_response_1 = await sign_autofill_and_submit(context, payload, context.destinationWallet)

        let ticket_sequence = (await get_ticket_sequence(context, context.destinationAddress))[0]
        payload = ObjFactory.getObj(ObjType.NFTokenMint,
            {
                Account: context.destinationAddress,
                Issuer: context.sourceAddress,
                NFTokenTaxon: 0,
                Sequence: 0,
                TicketSequence: ticket_sequence,
            })
        context.nft_mint_response_1 = await sign_autofill_and_submit(context, payload, context.destinationWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
        throw error
    }
});

Then('nft minting on ticket with authorized user is successful', {timeout: 180000}, async () => {
    verify_account_balance(await get_account_balance(context, context.sourceAddress), parseFloat(context.sourceBalance) - xrpl.dropsToXrp(context.minDrop))
    verify_account_balance(await get_account_balance(context, context.destinationAddress), parseFloat(context.destinationBalance) - (2 * xrpl.dropsToXrp(context.minDrop)))
    await verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)
    await verify_ticket_create_account_objects(context, context.tc_response_1)
    await verify_account_set_account_objects(context, context.account_set_response_1)
});

When('we mint NFT on ticket with issuer without user authorization', {timeout: 180000}, async () => {
    try {
        let payload = ObjFactory.getObj(ObjType.AccountSet,
            {
                Account: context.sourceAddress,
                SetFlag: AccountSetAsfFlags.asfAuthorizedNFTokenMinter,
                NFTokenMinter: context.destinationAddress,
            });
        context.account_set_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)

        payload = ObjFactory.getObj(ObjType.AccountSet,
            {
                Account: context.sourceAddress,
                ClearFlag: AccountSetAsfFlags.asfAuthorizedNFTokenMinter,
            });
        context.account_set_response_2 = await sign_autofill_and_submit(context, payload, context.sourceWallet)

        payload = ObjFactory.getObj(ObjType.NFTokenMint,
            {
                Account: context.destinationAddress,
                Issuer: context.sourceAddress,
                NFTokenTaxon: 0,
            })

        context.nft_mint_response_1 = await sign_autofill_and_submit(context, payload, context.destinationWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
        throw error
    }
});

Then('nft minting on ticket with issuer without user authorization is not successful', {timeout: 180000}, async () => {
    verify_account_balance(await get_account_balance(context, context.sourceAddress), parseFloat(context.sourceBalance) - (2 * xrpl.dropsToXrp(context.minDrop)))
    verify_account_balance(await get_account_balance(context, context.destinationAddress), parseFloat(context.destinationBalance) - (xrpl.dropsToXrp(context.minDrop)))
    await verify_nftoken_mint_account_objects(context, context.nft_mint_response_1, ResponseCode.no_permission)
    await verify_account_set_account_objects(context, context.account_set_response_1)
    await verify_account_set_account_objects(context, context.account_set_response_2)
});

When('we mint NFT with issuer and remove authorization', {timeout: 180000}, async () => {
    try {
        let payload = ObjFactory.getObj(ObjType.AccountSet,
            {
                Account: context.sourceAddress,
                SetFlag: AccountSetAsfFlags.asfAuthorizedNFTokenMinter,
                NFTokenMinter: context.destinationAddress,
            });
        context.account_set_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)

        payload = ObjFactory.getObj(ObjType.NFTokenMint,
            {
                Account: context.destinationAddress,
                Issuer: context.sourceAddress,
                NFTokenTaxon: 0,
            })
        context.nft_mint_response_1 = await sign_autofill_and_submit(context, payload, context.destinationWallet)

        payload = ObjFactory.getObj(ObjType.AccountSet,
            {
                Account: context.sourceAddress,
                ClearFlag: AccountSetAsfFlags.asfAuthorizedNFTokenMinter,
            });
        context.account_set_response_2 = await sign_autofill_and_submit(context, payload, context.sourceWallet)

        payload = ObjFactory.getObj(ObjType.NFTokenMint,
            {
                Account: context.destinationAddress,
                Issuer: context.sourceAddress,
                NFTokenTaxon: 0,
            })
        context.nft_mint_response_2 = await sign_autofill_and_submit(context, payload, context.destinationWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
        throw error
    }
});

Then('nft minting with issuer and removing authorization is successful', {timeout: 180000}, async () => {
    verify_account_balance(await get_account_balance(context, context.sourceAddress), parseFloat(context.sourceBalance) - (2 * xrpl.dropsToXrp(context.minDrop)))
    verify_account_balance(await get_account_balance(context, context.destinationAddress), parseFloat(context.destinationBalance) - (2 * xrpl.dropsToXrp(context.minDrop)))
    await verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)
    await verify_nftoken_mint_account_objects(context, context.nft_mint_response_2, ResponseCode.no_permission)
    await verify_account_set_account_objects(context, context.account_set_response_1)
    await verify_account_set_account_objects(context, context.account_set_response_2)
});

When('we change authorized user and mint NFT', {timeout: 180000}, async () => {
    try {
        let payload = ObjFactory.getObj(ObjType.AccountSet,
            {
                Account: context.aliceAddress,
                SetFlag: AccountSetAsfFlags.asfAuthorizedNFTokenMinter,
                NFTokenMinter: context.bobAddress,
            });
        context.account_set_response_1 = await sign_autofill_and_submit(context, payload, context.aliceWallet)

        payload = ObjFactory.getObj(ObjType.AccountSet,
            {
                Account: context.aliceAddress,
                SetFlag: AccountSetAsfFlags.asfAuthorizedNFTokenMinter,
                NFTokenMinter: context.carolAddress,
            });
        context.account_set_response_2 = await sign_autofill_and_submit(context, payload, context.aliceWallet)


        payload = ObjFactory.getObj(ObjType.NFTokenMint,
            {
                Account: context.bobAddress,
                Issuer: context.aliceAddress,
                NFTokenTaxon: 0,
            })
        context.nft_mint_response_1 = await sign_autofill_and_submit(context, payload, context.bobWallet)

        payload = ObjFactory.getObj(ObjType.NFTokenMint,
            {
                Account: context.carolAddress,
                Issuer: context.aliceAddress,
                NFTokenTaxon: 0,
            })
        context.nft_mint_response_2 = await sign_autofill_and_submit(context, payload, context.carolWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
        throw error
    }
});

Then('NFT minting after changing authorized user is successful', {timeout: 180000}, async () => {
    verify_account_balance(await get_account_balance(context, context.aliceAddress), parseFloat(context.aliceBalance) - (2 * xrpl.dropsToXrp(context.minDrop)))
    verify_account_balance(await get_account_balance(context, context.bobAddress), parseFloat(context.bobBalance) - (xrpl.dropsToXrp(context.minDrop)))
    verify_account_balance(await get_account_balance(context, context.carolAddress), parseFloat(context.carolBalance) - (xrpl.dropsToXrp(context.minDrop)))
    await verify_nftoken_mint_account_objects(context, context.nft_mint_response_1, ResponseCode.no_permission)
    await verify_nftoken_mint_account_objects(context, context.nft_mint_response_2)
    await verify_account_set_account_objects(context, context.account_set_response_1)
    await verify_account_set_account_objects(context, context.account_set_response_2)
});

When('we mint NFT using authorization chain of authorized users', {timeout: 180000}, async () => {
    try {
        let payload = ObjFactory.getObj(ObjType.AccountSet,
            {
                Account: context.aliceAddress,
                SetFlag: AccountSetAsfFlags.asfAuthorizedNFTokenMinter,
                NFTokenMinter: context.bobAddress,
            });
        context.account_set_response_1 = await sign_autofill_and_submit(context, payload, context.aliceWallet)

        payload = ObjFactory.getObj(ObjType.AccountSet,
            {
                Account: context.bobAddress,
                SetFlag: AccountSetAsfFlags.asfAuthorizedNFTokenMinter,
                NFTokenMinter: context.carolAddress,
            });
        context.account_set_response_2 = await sign_autofill_and_submit(context, payload, context.bobWallet)


        payload = ObjFactory.getObj(ObjType.NFTokenMint,
            {
                Account: context.bobAddress,
                Issuer: context.aliceAddress,
                NFTokenTaxon: 0,
            })
        context.nft_mint_response_1 = await sign_autofill_and_submit(context, payload, context.bobWallet)

        payload = ObjFactory.getObj(ObjType.NFTokenMint,
            {
                Account: context.carolAddress,
                Issuer: context.aliceAddress,
                NFTokenTaxon: 0,
            })
        context.nft_mint_response_2 = await sign_autofill_and_submit(context, payload, context.carolWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
        throw error
    }
});

Then('NFT minting using authorization chain of authorized users is not successful', {timeout: 180000}, async () => {
    verify_account_balance(await get_account_balance(context, context.aliceAddress), parseFloat(context.aliceBalance) - (xrpl.dropsToXrp(context.minDrop)))
    verify_account_balance(await get_account_balance(context, context.bobAddress), parseFloat(context.bobBalance) - (2 * xrpl.dropsToXrp(context.minDrop)))
    verify_account_balance(await get_account_balance(context, context.carolAddress), parseFloat(context.carolBalance) - (xrpl.dropsToXrp(context.minDrop)))
    await verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)
    await verify_nftoken_mint_account_objects(context, context.nft_mint_response_2, ResponseCode.no_permission)
    await verify_account_set_account_objects(context, context.account_set_response_1)
    await verify_account_set_account_objects(context, context.account_set_response_2)
});

When('we mint NFT using ticket', {timeout: 180000}, async () => {
    try {
        let payload = ObjFactory.getObj(ObjType.TicketCreate,
            {
                Account: context.sourceAddress,
                Sequence: await get_account_sequence(context, context.sourceAddress),
                TicketCount: 1,
            })
        context.tc_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)

        let ticket_sequence = (await get_ticket_sequence(context, context.sourceAddress))[0]
        payload = ObjFactory.getObj(ObjType.NFTokenMint,
            {
                Account: context.sourceAddress,
                NFTokenTaxon: 0,
                Sequence: 0,
                TicketSequence: ticket_sequence
            })
        context.nft_mint_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
        throw error
    }
});

Then('NFT minting using ticket is successful', {timeout: 180000}, async () => {
    verify_account_balance(await get_account_balance(context, context.sourceAddress), parseFloat(context.sourceBalance) - (2 * xrpl.dropsToXrp(context.minDrop)))
    await verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)
    await verify_ticket_create_account_objects(context, context.tc_response_1)
});


When('we mint NFT and try to delete account owner', {timeout: 180000}, async () => {
    try {
        let payload = ObjFactory.getObj(ObjType.NFTokenMint,
            {
                Account: context.sourceAddress,
                NFTokenTaxon: 0,
            })
        context.nft_mint_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)

        payload = ObjFactory.getObj(ObjType.AccountDelete,
            {
                Account: context.sourceAddress,
                Destination: context.destinationAddress,
                Fee: constants.DEFAULT_DELETE_ACCOUNT_FEE,
                Sequence: await get_account_sequence(context, context.sourceAddress),
            });
        context.ad_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
    }
});


Then('deleting account owner after NFT minting is not successful', {timeout: 180000}, async () => {
    assert.equal(context.testStatus, "failed", "Test Status is incorrect")
    assert.match(context.exception.toString(), /Preliminary result: tecHAS_OBLIGATIONS./, "Incorrect error message received.")
    verify_account_balance(await get_account_balance(context, context.sourceAddress), parseFloat(context.sourceBalance) - (xrpl.dropsToXrp(context.minDrop)))
    verify_account_balance(await get_account_balance(context, context.destinationAddress), parseFloat(context.destinationBalance))
    await verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)
});

When('we mint NFT on ticket and try to delete account owner', {timeout: 180000}, async () => {
    try {
        let payload = ObjFactory.getObj(ObjType.TicketCreate,
            {
                Account: context.sourceAddress,
                Sequence: await get_account_sequence(context, context.sourceAddress),
                TicketCount: 1,
            })
        context.tc_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)

        let ticket_sequence = (await get_ticket_sequence(context, context.sourceAddress))[0]
        payload = ObjFactory.getObj(ObjType.NFTokenMint,
            {
                Account: context.sourceAddress,
                NFTokenTaxon: 0,
                Sequence: 0,
                TicketSequence: ticket_sequence
            })
        context.nft_mint_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)

        payload = ObjFactory.getObj(ObjType.AccountDelete,
            {
                Account: context.sourceAddress,
                Destination: context.destinationAddress,
                Fee: constants.DEFAULT_DELETE_ACCOUNT_FEE,
                Sequence: await get_account_sequence(context, context.sourceAddress),
            });
        context.ad_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
    }
});


Then('deleting account owner after NFT minting on ticket is not successful', {timeout: 180000}, async () => {
    assert.equal(context.testStatus, "failed", "Test Status is incorrect")
    assert.match(context.exception.toString(), /Preliminary result: tecHAS_OBLIGATIONS./, "Incorrect error message received.")
    verify_account_balance(await get_account_balance(context, context.sourceAddress), parseFloat(context.sourceBalance) - (2 * xrpl.dropsToXrp(context.minDrop)))
    verify_account_balance(await get_account_balance(context, context.destinationAddress), parseFloat(context.destinationBalance))
    await verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)
});

When('we mint NFT with issuer and then remove authorization and delete account owner', {timeout: 180000}, async () => {
    try {
        let payload = ObjFactory.getObj(ObjType.AccountSet,
            {
                Account: context.sourceAddress,
                SetFlag: AccountSetAsfFlags.asfAuthorizedNFTokenMinter,
                NFTokenMinter: context.destinationAddress,
            });
        context.account_set_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)

        payload = ObjFactory.getObj(ObjType.NFTokenMint,
            {
                Account: context.destinationAddress,
                Issuer: context.sourceAddress,
                NFTokenTaxon: 0,
            })
        context.nft_mint_response_1 = await sign_autofill_and_submit(context, payload, context.destinationWallet)


        payload = ObjFactory.getObj(ObjType.AccountSet,
            {
                Account: context.sourceAddress,
                ClearFlag: AccountSetAsfFlags.asfAuthorizedNFTokenMinter,
            });
        context.account_set_response_2 = await sign_autofill_and_submit(context, payload, context.sourceWallet)


        payload = ObjFactory.getObj(ObjType.AccountDelete,
            {
                Account: context.destinationAddress,
                Destination: context.sourceAddress,
                Fee: constants.DEFAULT_DELETE_ACCOUNT_FEE,
                Sequence: await get_account_sequence(context, context.destinationAddress),
            });
        context.ad_response_1 = await sign_autofill_and_submit(context, payload, context.destinationWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
    }
});


Then('removing authorization and deleting account owner after NFT minting is not successful', {timeout: 180000}, async () => {
    assert.equal(context.testStatus, "failed", "Test Status is incorrect")
    assert.match(context.exception.toString(), /Preliminary result: tecHAS_OBLIGATIONS./, "Incorrect error message received.")
    verify_account_balance(await get_account_balance(context, context.sourceAddress), parseFloat(context.sourceBalance) - (2 * xrpl.dropsToXrp(context.minDrop)))
    verify_account_balance(await get_account_balance(context, context.destinationAddress), parseFloat(context.destinationBalance) - (xrpl.dropsToXrp(context.minDrop)))
    await verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)
    await verify_account_set_account_objects(context, context.account_set_response_1)
    await verify_account_set_account_objects(context, context.account_set_response_2)
});

When('we mint NFT with issuer and then remove authorization and delete issuer', {timeout: 180000}, async () => {
    try {
        let payload = ObjFactory.getObj(ObjType.AccountSet,
            {
                Account: context.sourceAddress,
                SetFlag: AccountSetAsfFlags.asfAuthorizedNFTokenMinter,
                NFTokenMinter: context.destinationAddress,
            });
        context.account_set_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)

        payload = ObjFactory.getObj(ObjType.NFTokenMint,
            {
                Account: context.destinationAddress,
                Issuer: context.sourceAddress,
                NFTokenTaxon: 0,
                // Sequence: 0,
                // TicketSequence: ticket_sequence
            })
        context.nft_mint_response_1 = await sign_autofill_and_submit(context, payload, context.destinationWallet)


        payload = ObjFactory.getObj(ObjType.AccountSet,
            {
                Account: context.sourceAddress,
                ClearFlag: AccountSetAsfFlags.asfAuthorizedNFTokenMinter,
            });
        context.account_set_response_2 = await sign_autofill_and_submit(context, payload, context.sourceWallet)


        payload = ObjFactory.getObj(ObjType.AccountDelete,
            {
                Account: context.sourceAddress,
                Destination: context.destinationAddress,
                Fee: constants.DEFAULT_DELETE_ACCOUNT_FEE,
                Sequence: await get_account_sequence(context, context.sourceAddress),
            });
        context.ad_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
        // throw error
    }
});


Then('removing authorization and deleting issuer after NFT minting is not successful', {timeout: 180000}, async () => {
    assert.equal(context.testStatus, "failed", "Test Status is incorrect")
    assert.match(context.exception.toString(), /Preliminary result: tecHAS_OBLIGATIONS./, "Incorrect error message received.")
    verify_account_balance(await get_account_balance(context, context.sourceAddress), parseFloat(context.sourceBalance) - (2 * xrpl.dropsToXrp(context.minDrop)))
    verify_account_balance(await get_account_balance(context, context.destinationAddress), parseFloat(context.destinationBalance) - (xrpl.dropsToXrp(context.minDrop)))
    await verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)
    await verify_account_set_account_objects(context, context.account_set_response_1)
    await verify_account_set_account_objects(context, context.account_set_response_2)
});

When('we burn NFT as owner', {timeout: 180000}, async () => {
    try {
        let payload = ObjFactory.getObj(ObjType.NFTokenMint,
            {
                Account: context.sourceAddress,
                NFTokenTaxon: 0,
            })
        context.nft_mint_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)


        payload = ObjFactory.getObj(ObjType.NFTokenBurn,
            {
                Account: context.sourceAddress,
                NFTokenID: (await get_nft_tokens(context, context.sourceAddress)).pop(),
            });
        context.nft_burn_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)

    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
    }
});

Then('burning NFT as owner is successful', {timeout: 180000}, async () => {
    verify_account_balance(await get_account_balance(context, context.sourceAddress), parseFloat(context.sourceBalance) - (2 * xrpl.dropsToXrp(context.minDrop)))
    await verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)
    await verify_nftoken_burn_account_objects(context, context.nft_burn_response_1)
});

When('we burn NFT with low reserves', {timeout: 180000}, async () => {
    try {
        let payload = ObjFactory.getObj(ObjType.NFTokenMint,
            {
                Account: context.sourceAddress,
                NFTokenTaxon: 0,
            })
        context.nft_mint_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)

        context.py_response_1 = await send_payment(context, context.sourceWallet, context.destinationWallet, (parseInt((await get_account_balance(context, context.sourceAddress)) - int(constants.BASE_RESERVE) -
            int(constants.OWNER_RESERVE))).toString())

        payload = ObjFactory.getObj(ObjType.NFTokenBurn,
            {
                Account: context.sourceAddress,
                NFTokenID: (await get_nft_tokens(context, context.sourceAddress)).pop(),
            });
        context.nft_burn_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
    }
});

Then('burning NFT with low reserves is not successful', {timeout: 180000}, async () => {
    verify_account_balance(await get_account_balance(context, context.sourceAddress), parseFloat(context.sourceBalance) - (xrpl.dropsToXrp(context.minDrop)))
    await verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)
    await verify_payment_account_objects(context, context.py_response_1)
    await verify_nftoken_burn_account_objects(context, context.nft_burn_response_1)
});

When('we burn NFT with NFT ID mismatch', {timeout: 180000}, async () => {
    try {
        let payload = ObjFactory.getObj(ObjType.NFTokenBurn,
            {
                Account: context.sourceAddress,
                Fee: "10",
                NFTokenID: "0008000044CAF362635003E9D565979EE87A1668A1FFE7BB2DCBAB9D00000002",
            });
        context.nft_burn_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
        throw error
    }
});

Then('burning NFT with NFT ID mismatch is not successful', {timeout: 180000}, async () => {
    verify_account_balance(await get_account_balance(context, context.sourceAddress), parseFloat(context.sourceBalance) - (xrpl.dropsToXrp(context.minDrop)))
    await verify_nftoken_burn_account_objects(context, context.nft_burn_response_1, ResponseCode.no_entry)
});

When('we burn NFT as different user', {timeout: 180000}, async () => {
    try {
        let payload = ObjFactory.getObj(ObjType.NFTokenMint,
            {
                Account: context.sourceAddress,
                NFTokenTaxon: 0,
            })
        context.nft_mint_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)

        payload = ObjFactory.getObj(ObjType.NFTokenBurn,
            {
                Account: context.destinationAddress,
                Fee: "10",
                NFTokenID: (await get_nft_tokens(context, context.sourceAddress)).pop(),
            });
        context.nft_burn_response_1 = await sign_autofill_and_submit(context, payload, context.destinationWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
        throw error
    }
});

Then('burning NFT as different user is not successful', {timeout: 180000}, async () => {
    verify_account_balance(await get_account_balance(context, context.sourceAddress), parseFloat(context.sourceBalance) - (xrpl.dropsToXrp(context.minDrop)))
    verify_account_balance(await get_account_balance(context, context.destinationAddress), parseFloat(context.destinationBalance) - xrpl.dropsToXrp(context.minDrop))
    await verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)
    await verify_nftoken_burn_account_objects(context, context.nft_burn_response_1, ResponseCode.no_entry)
});

When('we mint NFT with issuer burn as owner', {timeout: 180000}, async () => {
    try {
        let payload = ObjFactory.getObj(ObjType.AccountSet,
            {
                Account: context.sourceAddress,
                SetFlag: AccountSetAsfFlags.asfAuthorizedNFTokenMinter,
                NFTokenMinter: context.destinationAddress,
            });
        context.account_set_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)

        payload = ObjFactory.getObj(ObjType.NFTokenMint,
            {
                Account: context.destinationAddress,
                Issuer: context.sourceAddress,
                NFTokenTaxon: 0,
            })
        context.nft_mint_response_1 = await sign_autofill_and_submit(context, payload, context.destinationWallet)


        payload = ObjFactory.getObj(ObjType.NFTokenBurn,
            {
                Account: context.destinationAddress,
                NFTokenID: (await get_nft_tokens(context, context.destinationAddress)).pop(),
            });
        context.nft_burn_response_1 = await sign_autofill_and_submit(context, payload, context.destinationWallet)

    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
        throw error
    }
});

Then('burning NFT with issuer burn as owner is successful', {timeout: 180000}, async () => {
    verify_account_balance(await get_account_balance(context, context.sourceAddress), parseFloat(context.sourceBalance) - (xrpl.dropsToXrp(context.minDrop)))
    verify_account_balance(await get_account_balance(context, context.destinationAddress), parseFloat(context.destinationBalance) - (2 * xrpl.dropsToXrp(context.minDrop)))

    await verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)
    await verify_account_set_account_objects(context, context.account_set_response_1)
    await verify_nftoken_burn_account_objects(context, context.nft_burn_response_1)
});

When('we mint NFT with issuer burn as issuer without tfBurnable', {timeout: 180000}, async () => {
    try {
        let payload = ObjFactory.getObj(ObjType.AccountSet,
            {
                Account: context.sourceAddress,
                SetFlag: AccountSetAsfFlags.asfAuthorizedNFTokenMinter,
                NFTokenMinter: context.destinationAddress,
            });
        context.account_set_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)

        payload = ObjFactory.getObj(ObjType.NFTokenMint,
            {
                Account: context.destinationAddress,
                Issuer: context.sourceAddress,
                NFTokenTaxon: 0,
            })
        context.nft_mint_response_1 = await sign_autofill_and_submit(context, payload, context.destinationWallet)


        payload = ObjFactory.getObj(ObjType.NFTokenBurn,
            {
                Account: context.sourceAddress,
                Owner: context.destinationAddress,
                NFTokenID: (await get_nft_tokens(context, context.destinationAddress)).pop(),
            });
        context.nft_burn_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)

    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
        throw error
    }
});

Then('burning NFT with issuer burn as issuer without tfBurnable is not successful', {timeout: 180000}, async () => {
    verify_account_balance(await get_account_balance(context, context.sourceAddress), parseFloat(context.sourceBalance) - (2 * xrpl.dropsToXrp(context.minDrop)))
    verify_account_balance(await get_account_balance(context, context.destinationAddress), parseFloat(context.destinationBalance) - (xrpl.dropsToXrp(context.minDrop)))

    await verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)
    await verify_account_set_account_objects(context, context.account_set_response_1)
    await verify_nftoken_burn_account_objects(context, context.nft_burn_response_1, ResponseCode.no_permission)
});

When('we mint NFT with issuer burn as issuer with tfBurnable', {timeout: 180000}, async () => {
    try {
        let payload = ObjFactory.getObj(ObjType.AccountSet,
            {
                Account: context.sourceAddress,
                SetFlag: AccountSetAsfFlags.asfAuthorizedNFTokenMinter,
                NFTokenMinter: context.destinationAddress,
            });
        context.account_set_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)

        payload = ObjFactory.getObj(ObjType.NFTokenMint,
            {
                Account: context.destinationAddress,
                Issuer: context.sourceAddress,
                NFTokenTaxon: 0,
                Flags: NFTokenMintFlags.tfBurnable
            })
        context.nft_mint_response_1 = await sign_autofill_and_submit(context, payload, context.destinationWallet)


        payload = ObjFactory.getObj(ObjType.NFTokenBurn,
            {
                Account: context.sourceAddress,
                Owner: context.destinationAddress,
                NFTokenID: (await get_nft_tokens(context, context.destinationAddress)).pop(),
            });
        context.nft_burn_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)

    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
        throw error
    }
});

Then('burning NFT with issuer burn as issuer with tfBurnable is successful', {timeout: 180000}, async () => {
    verify_account_balance(await get_account_balance(context, context.sourceAddress), parseFloat(context.sourceBalance) - (2 * xrpl.dropsToXrp(context.minDrop)))
    verify_account_balance(await get_account_balance(context, context.destinationAddress), parseFloat(context.destinationBalance) - (xrpl.dropsToXrp(context.minDrop)))

    await verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)
    await verify_account_set_account_objects(context, context.account_set_response_1)
    await verify_nftoken_burn_account_objects(context, context.nft_burn_response_1)
});

When('we mint NFT with issuer burn as issuer without owner field', {timeout: 180000}, async () => {
    try {
        let payload = ObjFactory.getObj(ObjType.AccountSet,
            {
                Account: context.sourceAddress,
                SetFlag: AccountSetAsfFlags.asfAuthorizedNFTokenMinter,
                NFTokenMinter: context.destinationAddress,
            });
        context.account_set_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)

        payload = ObjFactory.getObj(ObjType.NFTokenMint,
            {
                Account: context.destinationAddress,
                Issuer: context.sourceAddress,
                NFTokenTaxon: 0,
                Flags: NFTokenMintFlags.tfBurnable
            })
        context.nft_mint_response_1 = await sign_autofill_and_submit(context, payload, context.destinationWallet)


        payload = ObjFactory.getObj(ObjType.NFTokenBurn,
            {
                Account: context.sourceAddress,
                Fee: "10",
                NFTokenID: (await get_nft_tokens(context, context.destinationAddress)).pop(),
            });
        context.nft_burn_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)

    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
        throw error
    }
});

Then('burning NFT with issuer burn as issuer without owner field not successful', {timeout: 180000}, async () => {
    verify_account_balance(await get_account_balance(context, context.sourceAddress), parseFloat(context.sourceBalance) - (2 * xrpl.dropsToXrp(context.minDrop)))
    verify_account_balance(await get_account_balance(context, context.destinationAddress), parseFloat(context.destinationBalance) - (xrpl.dropsToXrp(context.minDrop)))

    await verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)
    await verify_account_set_account_objects(context, context.account_set_response_1)
    await verify_nftoken_burn_account_objects(context, context.nft_burn_response_1, ResponseCode.no_entry)
});


When('we burn NFT and remint', {timeout: 180000}, async () => {
    try {
        let payload = ObjFactory.getObj(ObjType.NFTokenMint,
            {
                Account: context.sourceAddress,
                NFTokenTaxon: 0,
            })
        context.nft_mint_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)


        payload = ObjFactory.getObj(ObjType.NFTokenBurn,
            {
                Account: context.sourceAddress,
                NFTokenID: (await get_nft_tokens(context, context.sourceAddress)).pop(),
            });
        context.nft_burn_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)

        payload = ObjFactory.getObj(ObjType.NFTokenMint,
            {
                Account: context.sourceAddress,
                NFTokenTaxon: 0,
            })
        context.nft_mint_response_2 = await sign_autofill_and_submit(context, payload, context.sourceWallet)


    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
        throw error
    }
});

Then('burning NFT and reminting is successful', {timeout: 180000}, async () => {
    verify_account_balance(await get_account_balance(context, context.sourceAddress), parseFloat(context.sourceBalance) - (3 * xrpl.dropsToXrp(context.minDrop)))
    await verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)
    await verify_nftoken_mint_account_objects(context, context.nft_mint_response_2)
    await verify_nftoken_burn_account_objects(context, context.nft_burn_response_1)
});

When('we burn NFT and delete owner', {timeout: 180000000}, async () => {
    try {
        let payload = ObjFactory.getObj(ObjType.NFTokenMint,
            {
                Account: context.sourceAddress,
                NFTokenTaxon: 0,
            })

        context.nft_mint_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)

        payload = ObjFactory.getObj(ObjType.NFTokenBurn,
            {
                Account: context.sourceAddress,
                NFTokenID: (await get_nft_tokens(context, context.sourceAddress)).pop(),
            });
        context.nft_burn_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)

        await wait_for_ledger_to_advance_for_account_delete(context, context.sourceAddress)

        payload = ObjFactory.getObj(ObjType.AccountDelete,
            {
                Account: context.sourceAddress,
                Destination: context.destinationAddress,
                Fee: constants.DEFAULT_DELETE_ACCOUNT_FEE,
                Sequence: await get_account_sequence(context, context.sourceAddress),
            });
        context.ad_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
        throw error
    }
});

Then('burning NFT and deleting owner is successful', {timeout: 180000}, async () => {
    console.log("context.nft_mint_response_1")
    console.log(context.nft_mint_response_1)
    await verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)

    console.log("context.nft_burn_response_1")
    console.log(context.nft_burn_response_1)
    await verify_nftoken_burn_account_objects(context, context.nft_burn_response_1)

    console.log("context.ad_response_1")
    console.log(context.ad_response_1)
    await verify_account_delete_account_objects(context, context.ad_response_1)
});

When('we mint NFT with issuer burn as owner and delete owner', {timeout: 180000000}, async () => {
    try {
        let payload = ObjFactory.getObj(ObjType.AccountSet,
            {
                Account: context.sourceAddress,
                SetFlag: AccountSetAsfFlags.asfAuthorizedNFTokenMinter,
                NFTokenMinter: context.destinationAddress,
            });
        context.account_set_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)

        payload = ObjFactory.getObj(ObjType.NFTokenMint,
            {
                Account: context.destinationAddress,
                Issuer: context.sourceAddress,
                NFTokenTaxon: 0,
            })
        context.nft_mint_response_1 = await sign_autofill_and_submit(context, payload, context.destinationWallet)

        payload = ObjFactory.getObj(ObjType.NFTokenBurn,
            {
                Account: context.destinationAddress,
                NFTokenID: (await get_nft_tokens(context, context.destinationAddress)).pop(),
            });
        context.nft_burn_response_1 = await sign_autofill_and_submit(context, payload, context.destinationWallet)

        await wait_for_ledger_to_advance_for_account_delete(context, context.destinationAddress)

        payload = ObjFactory.getObj(ObjType.AccountDelete,
            {
                Account: context.destinationAddress,
                Destination: context.sourceAddress,
                Fee: constants.DEFAULT_DELETE_ACCOUNT_FEE,
                Sequence: await get_account_sequence(context, context.destinationAddress),
            });
        context.ad_response_1 = await sign_autofill_and_submit(context, payload, context.destinationWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
        throw error
    }
});

Then('minting NFT with issuer burn as owner and deleting owner is successful', {timeout: 180000}, async () => {
    await verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)
    await verify_nftoken_burn_account_objects(context, context.nft_burn_response_1)
    await verify_account_delete_account_objects(context, context.ad_response_1)
    await verify_account_set_account_objects(context, context.account_set_response_1)
});

When('we burn NFT as owner and delete issuer', {timeout: 180000000}, async () => {
    try {
        let payload = ObjFactory.getObj(ObjType.AccountSet,
            {
                Account: context.sourceAddress,
                SetFlag: AccountSetAsfFlags.asfAuthorizedNFTokenMinter,
                NFTokenMinter: context.destinationAddress,
            });
        context.account_set_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)

        payload = ObjFactory.getObj(ObjType.NFTokenMint,
            {
                Account: context.destinationAddress,
                Issuer: context.sourceAddress,
                NFTokenTaxon: 0,
            })
        context.nft_mint_response_1 = await sign_autofill_and_submit(context, payload, context.destinationWallet)

        payload = ObjFactory.getObj(ObjType.NFTokenBurn,
            {
                Account: context.destinationAddress,
                NFTokenID: (await get_nft_tokens(context, context.destinationAddress)).pop(),
            });
        context.nft_burn_response_1 = await sign_autofill_and_submit(context, payload, context.destinationWallet)

        await wait_for_ledger_to_advance_for_account_delete(context, context.destinationAddress)

        payload = ObjFactory.getObj(ObjType.AccountDelete,
            {
                Account: context.sourceAddress,
                Destination: context.destinationAddress,
                Fee: constants.DEFAULT_DELETE_ACCOUNT_FEE,
                Sequence: await get_account_sequence(context, context.sourceAddress),
            });
        context.ad_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
        throw error
    }
});

Then('burning NFT as owner and deleting issuer is successful', {timeout: 180000}, async () => {
    await verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)
    await verify_nftoken_burn_account_objects(context, context.nft_burn_response_1)
    await verify_account_delete_account_objects(context, context.ad_response_1)
    await verify_account_set_account_objects(context, context.account_set_response_1)
});

When('we burn NFT as issuer and delete owner', {timeout: 180000000}, async () => {
    try {
        let payload = ObjFactory.getObj(ObjType.AccountSet,
            {
                Account: context.sourceAddress,
                SetFlag: AccountSetAsfFlags.asfAuthorizedNFTokenMinter,
                NFTokenMinter: context.destinationAddress,
            });
        context.account_set_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)

        payload = ObjFactory.getObj(ObjType.NFTokenMint,
            {
                Account: context.destinationAddress,
                Issuer: context.sourceAddress,
                NFTokenTaxon: 0,
                Flags: NFTokenMintFlags.tfBurnable
            })
        context.nft_mint_response_1 = await sign_autofill_and_submit(context, payload, context.destinationWallet)

        payload = ObjFactory.getObj(ObjType.NFTokenBurn,
            {
                Account: context.sourceAddress,
                Owner: context.destinationAddress,
                NFTokenID: (await get_nft_tokens(context, context.destinationAddress)).pop(),
            });
        context.nft_burn_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)

        await wait_for_ledger_to_advance_for_account_delete(context, context.sourceAddress)

        payload = ObjFactory.getObj(ObjType.AccountDelete,
            {
                Account: context.destinationAddress,
                Destination: context.sourceAddress,
                Fee: constants.DEFAULT_DELETE_ACCOUNT_FEE,
                Sequence: await get_account_sequence(context, context.destinationAddress),
            });
        context.ad_response_1 = await sign_autofill_and_submit(context, payload, context.destinationWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
        throw error
    }
});

Then('burning NFT as issuer and deleting owner is successful', {timeout: 180000}, async () => {
    await verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)
    await verify_nftoken_burn_account_objects(context, context.nft_burn_response_1)
    await verify_account_delete_account_objects(context, context.ad_response_1)
    await verify_account_set_account_objects(context, context.account_set_response_1)
});

When('we burn NFT as issuer and delete issuer', {timeout: 180000000}, async () => {
    try {
        let payload = ObjFactory.getObj(ObjType.AccountSet,
            {
                Account: context.sourceAddress,
                SetFlag: AccountSetAsfFlags.asfAuthorizedNFTokenMinter,
                NFTokenMinter: context.destinationAddress,
            });
        context.account_set_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)

        payload = ObjFactory.getObj(ObjType.NFTokenMint,
            {
                Account: context.destinationAddress,
                Issuer: context.sourceAddress,
                NFTokenTaxon: 0,
                Flags: NFTokenMintFlags.tfBurnable
            })
        context.nft_mint_response_1 = await sign_autofill_and_submit(context, payload, context.destinationWallet)

        payload = ObjFactory.getObj(ObjType.NFTokenBurn,
            {
                Account: context.sourceAddress,
                Owner: context.destinationAddress,
                NFTokenID: (await get_nft_tokens(context, context.destinationAddress)).pop(),
            });
        context.nft_burn_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)

        await wait_for_ledger_to_advance_for_account_delete(context, context.sourceAddress)

        payload = ObjFactory.getObj(ObjType.AccountDelete,
            {
                Account: context.sourceAddress,
                Destination: context.destinationAddress,
                Fee: constants.DEFAULT_DELETE_ACCOUNT_FEE,
                Sequence: await get_account_sequence(context, context.sourceAddress),
            });
        context.ad_response_1 = await sign_autofill_and_submit(context, payload, context.sourceWallet)
    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
        throw error
    }
});

Then('burning NFT as issuer and deleting issuer is successful', {timeout: 180000}, async () => {
    await verify_nftoken_mint_account_objects(context, context.nft_mint_response_1)
    await verify_nftoken_burn_account_objects(context, context.nft_burn_response_1)
    await verify_account_delete_account_objects(context, context.ad_response_1)
    await verify_account_set_account_objects(context, context.account_set_response_1)
});


When('we mint more than 32 NFT objects', {timeout: 180000000}, async () => {
    try {
        let payload = ObjFactory.getObj(ObjType.NFTokenMint,
            {
                Account: context.sourceAddress,
                NFTokenTaxon: 0,
            })

        let max_nftokens = 35
        context.responses = []
        let response
        for (let count = 0; count < max_nftokens; count++) {
            response = await sign_autofill_and_submit(context, payload, context.sourceWallet)
            context.responses.push(response)
        }

    } catch (error) {
        context.exception = error
        context.testStatus = "failed"
        throw error
    }
});

Then('minting more than 32 NFT objects is successful', {timeout: 180000}, async () => {

    for (const response of context.responses) {
        await verify_nftoken_mint_account_objects(context, response)
    }
});

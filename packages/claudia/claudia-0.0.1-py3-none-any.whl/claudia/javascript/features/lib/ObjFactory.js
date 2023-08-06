module.exports = {
    getObj(type, args = {}) {
        if (type == this.ObjType.Payment) {
            args.TransactionType = "Payment"
        } else if (type == this.ObjType.TrustSet) {
            args.TransactionType = "TrustSet"
        } else if (type == this.ObjType.AccountSet) {
            args.TransactionType = "AccountSet"
        } else if (type == this.ObjType.OfferCreate) {
            args.TransactionType = "OfferCreate"
        } else if (type == this.ObjType.Fee) {
            args.command = 'fee'
        } else if (type == this.ObjType.AccountInfo) {
            args.command = 'account_info'
        } else if (type == this.ObjType.NFTokenMint) {
            args.TransactionType = "NFTokenMint"
        } else if (type == this.ObjType.NFTokenBurn) {
            args.TransactionType = "NFTokenBurn"
        } else if (type == this.ObjType.TicketCreate) {
            args.TransactionType = "TicketCreate"
        } else if (type == this.ObjType.AccountDelete) {
            args.TransactionType = "AccountDelete"
        } else if (type == this.ObjType.AccountObjects) {
            args.command = "account_objects"
        } else if (type == this.ObjType.AccountLines) {
            args.command = "account_lines"
        } else if (type == this.ObjType.Tx) {
            args.command = "tx"
        } else if (type == this.ObjType.AccountNFTs) {
            args.command = "account_nfts"
        } else if (type == this.ObjType.LedgerCurrent) {
            args.command = "ledger_current"
        }
        return args;
    },
    ObjType: {
        Payment: "payment",
        TrustSet: "trustset",
        AccountLines: "account_lines",
        AccountInfo: "account_info",
        AccountObjects: "account_objects",
        AccountSet: "accountset",
        OfferCreate: "offercreate",
        NFTokenMint: "nf_token_mint",
        NFTokenBurn: "nf_token_burn",
        TicketCreate: "ticket_create",
        AccountDelete: "account_delete",
        Fee: "fee_request",
        Tx: "tx",
        AccountNFTs: "account_nfts",
        LedgerCurrent: "ledger_current"
    }
};
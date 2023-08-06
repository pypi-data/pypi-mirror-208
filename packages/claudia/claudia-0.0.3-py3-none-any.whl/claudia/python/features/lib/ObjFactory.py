from enum import Enum

from xrpl.models import Payment, TrustSet, AccountLines, AccountObjects, OfferCreate, NFTokenMint, NFTokenBurn, \
    TicketCreate, AccountDelete, AccountNFTs, Tx, Memo, LedgerCurrent

from features.exceptions.InvalidInputException import InvalidInputException


class ObjFactory(object):
    @staticmethod
    def getObj(obj_type, **kwargs):
        payload = {}
        if obj_type == ObjType.payment:
            if "account" in kwargs:
                payload["account"] = kwargs["account"]

            if "destination" in kwargs:
                payload["destination"] = kwargs["destination"]

            if "amount" in kwargs:
                payload["amount"] = kwargs["amount"]

            if "invoice_id" in kwargs:
                payload["invoice_id"] = kwargs["invoice_id"]

            if "destination_tag" in kwargs:
                payload["destination_tag"] = kwargs["destination_tag"]
            if "flags" in kwargs:
                payload["flags"] = kwargs["flags"]
            if "paths" in kwargs:
                payload["paths"] = kwargs["paths"]
            if "send_max" in kwargs:
                payload["send_max"] = kwargs["send_max"]
            obj = Payment(**payload)
        elif obj_type == ObjType.trust_set:
            if "account" in kwargs:
                payload["account"] = kwargs["account"]
            if "limit_amount" in kwargs:
                payload["limit_amount"] = kwargs["limit_amount"]
            obj = TrustSet(**payload)
        elif obj_type == ObjType.tx:
            if "transaction" in kwargs:
                payload["transaction"] = kwargs["transaction"]
            if "binary" in kwargs:
                payload["binary"] = kwargs["binary"]
            obj = Tx(**payload)
        elif obj_type == ObjType.account_object:
            if "account" in kwargs:
                payload["account"] = kwargs["account"]
            else:
                raise KeyError("'account' is a required field to get Account Lines")
            if "peer" in kwargs:
                payload["peer"] = kwargs["peer"]
            if "ledger_hash" in kwargs:
                payload["ledger_hash"] = kwargs["ledger_hash"]
            if "ledger_index" in kwargs:
                payload["ledger_index"] = kwargs["ledger_index"]
            if "type" in kwargs:
                payload["type"] = kwargs["type"]
            if "deletion_blockers_only" in kwargs:
                payload["deletion_blockers_only"] = bool(kwargs["deletion_blockers_only"])
            if "limit" in kwargs:
                payload["limit"] = kwargs["limit"]
            if "marker" in kwargs:
                payload["marker"] = kwargs["marker"]
            obj = AccountObjects(**payload)
        elif obj_type == ObjType.ledger_current:
            obj = LedgerCurrent()
        elif obj_type == ObjType.account_lines:
            if "account" in kwargs:
                payload["account"] = kwargs["account"]
            else:
                raise KeyError("'account' is a required field to get Account Lines")
            if "peer" in kwargs:
                payload["peer"] = kwargs["peer"]
            if "limit" in kwargs:
                payload["limit"] = kwargs["limit"]
            if "marker" in kwargs:
                payload["marker"] = kwargs["marker"]
            if "ledger_index" in kwargs:
                payload["ledger_index"] = kwargs["ledger_index"]
            if "ledger_hash" in kwargs:
                payload["ledger_hash"] = kwargs["ledger_hash"]
            obj = AccountLines(**payload)
        elif obj_type == ObjType.account_nfts:
            if "account" in kwargs:
                payload["account"] = kwargs["account"]
            else:
                raise KeyError("'account' is a required field to get Account NFTs")
            if "ledger_hash" in kwargs:
                payload["ledger_hash"] = kwargs["ledger_hash"]
            if "limit" in kwargs:
                payload["limit"] = kwargs["limit"]
            if "marker" in kwargs:
                payload["marker"] = kwargs["marker"]
            obj = AccountNFTs(**payload)
        elif obj_type == ObjType.offer_create:
            if "account" in kwargs:
                payload["account"] = kwargs["account"]
            if "taker_pays" in kwargs:
                payload["taker_pays"] = kwargs["taker_pays"]
            if "taker_gets" in kwargs:
                payload["taker_gets"] = kwargs["taker_gets"]
            obj = OfferCreate(**payload)
        elif obj_type == ObjType.nft_token_mint:
            if "account" in kwargs:
                payload["account"] = kwargs["account"]
            if "issuer" in kwargs:
                payload["issuer"] = kwargs["issuer"]
            if "uri" in kwargs:
                payload["uri"] = kwargs["uri"]
            if "nftoken_taxon" in kwargs:
                payload["nftoken_taxon"] = kwargs["nftoken_taxon"]
            if "transfer_fee" in kwargs:
                payload["transfer_fee"] = kwargs["transfer_fee"]
            if "flags" in kwargs:
                payload["flags"] = kwargs["flags"]
            if "memos" in kwargs:
                payload["memos"] = kwargs["memos"]
            if "ticket_sequence" in kwargs:
                payload["ticket_sequence"] = kwargs["ticket_sequence"]
            if "sequence" in kwargs:
                payload["sequence"] = kwargs["sequence"]
            obj = NFTokenMint(**payload)
        elif obj_type == ObjType.nft_token_burn:
            if "account" in kwargs:
                payload["account"] = kwargs["account"]
            if "fee" in kwargs:
                payload["fee"] = kwargs["fee"]
            if "owner" in kwargs:
                payload["owner"] = kwargs["owner"]
            if "nftoken_id" in kwargs:
                payload["nftoken_id"] = kwargs["nftoken_id"]
            obj = NFTokenBurn(**payload)
        elif obj_type == ObjType.ticket_create:
            if "account" in kwargs:
                payload["account"] = kwargs["account"]
            if "sequence" in kwargs:
                payload["sequence"] = kwargs["sequence"]
            if "ticket_count" in kwargs:
                payload["ticket_count"] = kwargs["ticket_count"]
            obj = TicketCreate(**payload)
        elif obj_type == ObjType.memo:
            if "memo_data" in kwargs:
                payload["memo_data"] = kwargs["memo_data"]
            if "memo_format" in kwargs:
                payload["memo_format"] = kwargs["memo_format"]
            if "memo_type" in kwargs:
                payload["memo_type"] = kwargs["memo_type"]
            obj = Memo(**payload)
        elif obj_type == ObjType.account_delete:
            if "account" in kwargs:
                payload["account"] = kwargs["account"]
            if "destination" in kwargs:
                payload["destination"] = kwargs["destination"]
            if "fee" in kwargs:
                payload["fee"] = kwargs["fee"]
            if "sequence" in kwargs:
                payload["sequence"] = kwargs["sequence"]
            obj = AccountDelete(**payload)
        else:
            raise InvalidInputException("'{}' is not a valid objectType.".format(obj_type))
        return obj


class ObjType(str, Enum):
    payment = "payment"
    trust_set = "trust_set"
    account_lines = "account_lines"
    account_object = "account_object"
    offer_create = "offer_create"
    nft_token_mint = "nft_token_mint"
    nft_token_burn = "nft_token_burn"
    ticket_create = "ticket_create"
    account_delete = "account_delete"
    tx = "tx"
    account_nfts = "account_nfts"
    memo = "memo"
    ledger_current = "ledger_current"

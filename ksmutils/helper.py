"""
Helper functions - all functions in this file are pure with no side effects
"""
from hashlib import blake2b

import sr25519
import xxhash
from scalecodec.base import ScaleDecoder
from scalecodec.utils.ss58 import ss58_decode


def xx128(word):
    a = bytearray(xxhash.xxh64(word, seed=0).digest())
    b = bytearray(xxhash.xxh64(word, seed=1).digest())
    a.reverse()
    b.reverse()
    return f"{a.hex()}{b.hex()}"


def account_id_prefix(account_id):
    storage_key = bytearray(xxhash.xxh64(bytes.fromhex(account_id), seed=0).digest())
    storage_key.reverse()
    return storage_key.hex()


def get_prefix(escrow_address):
    module_prefix = xx128("Utility") + xx128("Multisigs")
    account_id = ss58_decode(escrow_address, 2)
    return module_prefix + account_id_prefix(account_id) + account_id


def hash_call(call):
    call = bytes.fromhex(str(call.data)[2:])
    return f"0x{blake2b(call, digest_size=32).digest().hex()}"


def transfer_signature_payload(
    metadata, address, value, nonce, genesis_hash, spec_version
):
    """
    Turn parameters gathered through side effects into unsigned transfer string
    """
    call = ScaleDecoder.get_decoder_class("Call", metadata=metadata)
    call.encode(
        {
            "call_module": "Balances",
            "call_function": "transfer",
            "call_args": {"dest": address, "value": value},
        }
    )
    signature_payload = ScaleDecoder.get_decoder_class("ExtrinsicPayloadValue")
    signature_payload.encode(
        {
            "call": str(call.data),
            "era": "00",
            "nonce": nonce,
            "tip": 0,
            "specVersion": spec_version,
            "genesisHash": genesis_hash,
            "blockHash": genesis_hash,
        }
    )
    return str(signature_payload.data)


def approve_as_multi_signature_payload(
    metadata,
    spec_version,
    genesis_hash,
    nonce,
    to_address,
    amount,
    other_signatories,
    threshold=2,
    tip=0,
):
    """
    Turn parameters gathered through side effects into unsigned approve_as_multi string
    """
    transfer = ScaleDecoder.get_decoder_class("Call", metadata=metadata)
    approve_as_multi = ScaleDecoder.get_decoder_class("Call", metadata=metadata)
    transfer.encode(
        {
            "call_module": "Balances",
            "call_function": "transfer",
            "call_args": {"dest": to_address, "value": amount},
        }
    )
    approve_as_multi.encode(
        {
            "call_module": "Utility",
            "call_function": "approve_as_multi",
            "call_args": {
                "call_hash": hash_call(transfer),
                "maybe_timepoint": None,
                "other_signatories": sorted(other_signatories),
                "threshold": threshold,
            },
        }
    )
    signature_payload = ScaleDecoder.get_decoder_class("ExtrinsicPayloadValue")
    signature_payload.encode(
        {
            "call": str(approve_as_multi.data),
            "era": "00",
            "nonce": nonce,
            "tip": tip,
            "specVersion": spec_version,
            "genesisHash": genesis_hash,
            "blockHash": genesis_hash,
        }
    )

    return str(signature_payload.data)


def as_multi_signature_payload(
    metadata,
    spec_version,
    genesis_hash,
    nonce,
    to_address,
    amount,
    other_signatories,
    timepoint,
    threshold=2,
    tip=0,
):
    """
    Turn parameters gathered through side effects into unsigned as_multi string
    """
    transfer = ScaleDecoder.get_decoder_class("Call", metadata=metadata)
    as_multi = ScaleDecoder.get_decoder_class("Call", metadata=metadata)
    transfer.encode(
        {
            "call_module": "Balances",
            "call_function": "transfer",
            "call_args": {"dest": to_address, "value": amount},
        }
    )
    as_multi.encode(
        {
            "call_module": "Utility",
            "call_function": "as_multi",
            "call_args": {
                "call": transfer.serialize(),
                "maybe_timepoint": {"height": timepoint[0], "index": timepoint[1]},
                "other_signatories": sorted(other_signatories),
                "threshold": threshold,
            },
        }
    )
    signature_payload = ScaleDecoder.get_decoder_class("ExtrinsicPayloadValue")
    signature_payload.encode(
        {
            "call": str(as_multi.data),
            "era": "00",
            "nonce": nonce,
            "tip": tip,
            "specVersion": spec_version,
            "genesisHash": genesis_hash,
            "blockHash": genesis_hash,
        }
    )

    return str(signature_payload.data)


def _extrinsic_construction(
    metadata,
    account_id,
    signature,
    call_function,
    call_module,
    call_arguments,
    nonce,
    tip=0,
):
    """
    Turn parameters gathered through side effects into extrinsic object
    """
    extrinsic = ScaleDecoder.get_decoder_class("Extrinsic", metadata=metadata)
    extrinsic.encode(
        {
            "account_id": account_id,
            "signature_version": 1,
            "signature": signature,
            "call_function": call_function,
            "call_module": call_module,
            "call_args": call_arguments,
            "nonce": nonce,
            "era": "00",
            "tip": tip,
        }
    )
    return str(extrinsic.data)


def unsigned_transfer_construction(
    metadata, account_id, signature, nonce, to_address, amount, tip=0
):
    """
    Turn parameters gathered through side effects into a transfer extrinsic object
    """
    call_function = "transfer"
    call_module = "Balances"
    call_arguments = {"dest": to_address, "value": amount}
    return _extrinsic_construction(
        metadata,
        account_id,
        signature,
        call_function,
        call_module,
        call_arguments,
        nonce,
        tip,
    )


def unsigned_approve_as_multi_construction(
    metadata,
    account_id,
    signature,
    nonce,
    to_address,
    amount,
    other_signatories,
    threshold=2,
    tip=0,
):
    """
    Turn parameters gathered through side effects into an approve_as_multi extrinsic object
    """
    call_function = "approve_as_multi"
    call_module = "Utility"
    transfer = ScaleDecoder.get_decoder_class("Call", metadata=metadata)
    transfer.encode(
        {
            "call_module": "Balances",
            "call_function": "transfer",
            "call_args": {"dest": to_address, "value": amount},
        }
    )

    call_arguments = {
        "call_hash": hash_call(transfer),
        "maybe_timepoint": None,
        "other_signatories": sorted(other_signatories),
        "threshold": threshold,
    }
    return _extrinsic_construction(
        metadata,
        account_id,
        signature,
        call_function,
        call_module,
        call_arguments,
        nonce,
        tip,
    )


def unsigned_as_multi_construction(
    metadata,
    account_id,
    signature,
    nonce,
    to_address,
    amount,
    timepoint,
    other_signatories,
    threshold=2,
    tip=0,
):
    """
    Turn parameters gathered through side effects into an as_multi extrinsic object
    """
    call_function = "as_multi"
    call_module = "Utility"
    transfer = ScaleDecoder.get_decoder_class("Call", metadata=metadata)
    transfer.encode(
        {
            "call_module": "Balances",
            "call_function": "transfer",
            "call_args": {"dest": to_address, "value": amount},
        }
    )
    call_arguments = {
        "call": transfer.serialize(),
        "maybe_timepoint": {"height": timepoint[0], "index": timepoint[1]},
        "other_signatories": sorted(other_signatories),
        "threshold": threshold,
    }
    return _extrinsic_construction(
        metadata,
        account_id,
        signature,
        call_function,
        call_module,
        call_arguments,
        nonce,
        tip,
    )


def sign_payload(keypair, payload):
    """
    Sign payload with keypair and return a signed hex string
    """
    if payload[0:2] == "0x":
        payload = payload[2:]
    signature = sr25519.sign(keypair, bytes.fromhex(payload))
    return signature.hex()

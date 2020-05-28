"""
Helper functions - all functions in this file are pure with no side effects
"""
from hashlib import blake2b

import sr25519
from scalecodec.base import ScaleDecoder


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
    TODO: Either validate that 0x is not prefixed or handle both in this function
    TODO: We should also validate if keypair is correct
    """
    signature = sr25519.sign(keypair, bytes.fromhex(payload),)

    return f"0x{signature.hex()}"

"""
Helper functions - all functions in this file are pure with no side effects
"""
from hashlib import blake2b
from typing import Union

import scalecodec
import sr25519
import xxhash
from scalecodec.base import RuntimeConfigurationObject
from scalecodec.base import ScaleDecoder
from scalecodec.metadata import MetadataDecoder
from scalecodec.utils.ss58 import ss58_decode
from scalecodec.utils.ss58 import ss58_encode


def xx128(word: str) -> str:
    """
    Returns a xxh128 hash on provided word
    """
    a = bytearray(xxhash.xxh64(word, seed=0).digest())
    b = bytearray(xxhash.xxh64(word, seed=1).digest())
    a.reverse()
    b.reverse()
    return f"{a.hex()}{b.hex()}"


def get_prefix(escrow_address: str, address_type: int = 2) -> str:
    """
    Returns prefix containing the account ID of the address provided
    """
    module_prefix = xx128("Multisig") + xx128("Multisigs")
    account_id = ss58_decode(escrow_address, address_type)
    storage_key = bytearray(xxhash.xxh64(bytes.fromhex(account_id), seed=0).digest())
    storage_key.reverse()
    return f"{module_prefix}{storage_key.hex()}{account_id}"


def hash_call(call: "scalecodec.types.Call") -> str:
    """
    Returns a hashed call
    """
    call = bytes.fromhex(str(call.data)[2:])
    return f"0x{blake2b(call, digest_size=32).digest().hex()}"


def transfer_signature_payload(
    metadata: "MetadataDecoder",
    address: str,
    value: int,
    nonce: int,
    genesis_hash: str,
    spec_version: int,
    transaction_version: int = 3,
    runtime_config: "RuntimeConfigurationObject" = None,
) -> str:
    """
    Turn parameters gathered through side effects into unsigned transfer string
    """
    call = ScaleDecoder.get_decoder_class(
        "Call", metadata=metadata, runtime_config=runtime_config
    )
    call.encode(
        {
            "call_module": "Balances",
            "call_function": "transfer",
            "call_args": {"dest": address, "value": value},
        }
    )
    signature_payload = ScaleDecoder.get_decoder_class(
        "ExtrinsicPayloadValue", runtime_config=runtime_config
    )
    signature_payload.encode(
        {
            "call": str(call.data),
            "era": "00",
            "nonce": nonce,
            "tip": 0,
            "specVersion": spec_version,
            "transactionVersion": transaction_version,
            "genesisHash": genesis_hash,
            "blockHash": genesis_hash,
        }
    )
    return str(signature_payload.data)


def as_multi_signature_payload(
    metadata: "MetadataDecoder",
    spec_version: int,
    genesis_hash: str,
    nonce: int,
    to_address: str,
    amount: int,
    other_signatories: list,
    address_type: int,
    timepoint: Union[tuple, bool],
    threshold: int = 2,
    tip: int = 0,
    transaction_version: int = 3,
    max_weight: int = 0,
    store_call: bool = False,
    runtime_config: "RuntimeConfigurationObject" = None,
) -> str:
    """
    Turn parameters gathered through side effects into unsigned as_multi string
    """
    as_multi = ScaleDecoder.get_decoder_class(
        "Call", metadata=metadata, runtime_config=runtime_config
    )
    transfer = ScaleDecoder.get_decoder_class(
        "OpaqueCall", metadata=metadata, runtime_config=runtime_config
    )
    transfer.encode(
        {
            "call_module": "Balances",
            "call_function": "transfer",
            "call_args": {"dest": to_address, "value": amount},
        }
    )
    maybe_timepoint = (
        {"height": timepoint[0], "index": timepoint[1]} if timepoint else None
    )
    # Be aware that the public keys are compared byte-for-byte and
    # sorted ascending before being inserted in the payload that is hashed.

    other_signatories = order_addresses(other_signatories, address_type)
    as_multi.encode(
        {
            "call_module": "Multisig",
            "call_function": "as_multi",
            "call_args": {
                "call": transfer.value,
                "maybe_timepoint": maybe_timepoint,
                "other_signatories": other_signatories,
                "threshold": threshold,
                "store_call": store_call,
                "max_weight": max_weight,
            },
        }
    )
    signature_payload = ScaleDecoder.get_decoder_class(
        "ExtrinsicPayloadValue", runtime_config=runtime_config
    )
    signature_payload.encode(
        {
            "call": str(as_multi.data),
            "era": "00",
            "nonce": nonce,
            "tip": tip,
            "specVersion": spec_version,
            "transactionVersion": transaction_version,
            "genesisHash": genesis_hash,
            "blockHash": genesis_hash,
        }
    )

    return str(signature_payload.data)


def _extrinsic_construction(
    metadata: "MetadataDecoder",
    account_id: str,
    signature: str,
    call_function: str,
    call_module: str,
    call_arguments: dict,
    nonce: int,
    tip: int = 0,
    runtime_config: "RuntimeConfigurationObject" = None,
) -> str:
    """
    Turn parameters gathered through side effects into extrinsic object
    """
    extrinsic = ScaleDecoder.get_decoder_class(
        "Extrinsic", metadata=metadata, runtime_config=runtime_config
    )
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
    print("Extrinsic", str(extrinsic.data))
    return str(extrinsic.data)


def unsigned_transfer_construction(
    metadata: "MetadataDecoder",
    account_id: str,
    signature: str,
    nonce: int,
    to_address: str,
    amount: int,
    tip: int = 0,
    runtime_config: "RuntimeConfigurationObject" = None,
) -> str:
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
        runtime_config,
    )


def unsigned_as_multi_construction(
    metadata: "MetadataDecoder",
    account_id: str,
    signature: str,
    nonce: int,
    to_address: str,
    amount: int,
    timepoint: Union[tuple, bool],
    other_signatories: list,
    max_weight: int = 0,
    store_call: bool = False,
    threshold: int = 2,
    tip: int = 0,
    adddress_type: int = 0,
    runtime_config: "RuntimeConfigurationObject" = None,
) -> str:
    """
    Turn parameters gathered through side effects into an as_multi extrinsic object
    """
    call_function = "as_multi"

    call_module = "Multisig"
    transfer = ScaleDecoder.get_decoder_class(
        "OpaqueCall", metadata=metadata, runtime_config=runtime_config
    )
    transfer.encode(
        {
            "call_module": "Balances",
            "call_function": "transfer",
            "call_args": {"dest": to_address, "value": amount},
        }
    )
    maybe_timepoint = (
        {"height": timepoint[0], "index": timepoint[1]} if timepoint else None
    )
    # Be aware that the public keys are compared byte-for-byte and
    # sorted ascending before being inserted in the payload that is hashed.
    other_signatories = order_addresses(other_signatories, adddress_type)
    call_arguments = {
        "call": transfer.value,
        "maybe_timepoint": maybe_timepoint,
        "other_signatories": other_signatories,
        "threshold": threshold,
        "store_call": store_call,
        "max_weight": max_weight,
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
        runtime_config,
    )


def sign_payload(keypair: tuple, payload: str) -> str:
    """
    Sign payload with keypair and return a signed hex string
    """
    if payload[0:2] == "0x":
        payload = payload[2:]
    signature = sr25519.sign(keypair, bytes.fromhex(payload))
    return signature.hex()


def hex_to_bytes(hex) -> bytes:
    """
    Generic hex to bytes conversion
    """
    if hex[0:2] == "0x":
        hex = hex[2:]
    return bytes.fromhex(hex)


def order_addresses(addresses: list, address_type: int = 0):
    bytearray_public_keys = []
    ordered_addresses = []
    # Convert address to public keys and then to byte array
    for address in addresses:
        public_key = ss58_decode(address, address_type)
        public_key_bytearray = bytearray()
        public_key_bytearray.extend(map(ord, public_key))
        bytearray_public_keys.append(public_key_bytearray)
    sorted_bytearray = sorted(bytearray_public_keys)
    # Convert back to addresses
    for byte_array in sorted_bytearray:
        ordered_addresses.append(ss58_encode(byte_array.decode(), address_type))
    return ordered_addresses

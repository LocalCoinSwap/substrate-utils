"""
Helper functions
"""
from scalecodec.base import ScaleDecoder


def unsigned_transfer(metadata, address, value, nonce, genesis_hash, spec_version):
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

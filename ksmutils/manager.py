import logging

from scalecodec.utils.ss58 import ss58_decode

from . import helper
from .core import Kusama

logger = logging.getLogger(__name__)


class TradeManager(Kusama):
    def escrow_broadcast(
        self, signed_payload, from_address, escrow_address, trade_value
    ):
        # We might have to make `nonce` a parameter
        nonce = self.get_nonce(from_address)
        from_public_key = ss58_decode(from_address)
        from_account_id = f"0x{from_public_key}"

        extrinsic_data = helper.unsigned_transfer_construction(
            self.metadata,
            from_account_id,
            signed_payload,
            nonce,
            escrow_address,
            trade_value,
        )

        result = self.network.node_rpc_call(
            "author_submitAndWatchExtrinsic", [extrinsic_data], watch=True
        )
        return result

    def publish(self):
        pass

    def status(self):
        pass

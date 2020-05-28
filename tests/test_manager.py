import sr25519
from scalecodec.utils.ss58 import ss58_encode

from ksmutils import helper
from ksmutils.manager import TradeManager


class TestBroadcastMethods:
    def test_escrow_broadcast_success(self, network, mocker):
        """
        This test is more of an example of how to broadcast successful escrow txn
        """

        arbitrator_hexseed = (
            "5c65b9f9f75f95d70b84577ab07e22f7400d394ca3c8bcb227fb6d42920d9b50"
        )
        seller_hexseed = (
            "5c65b9f9f75f95d70b84577ab07e22f7400d394ca3c8bcb227fb6d42920d9b50"
        )
        seller_keypair = sr25519.pair_from_seed(bytes.fromhex(seller_hexseed))
        escrow_address = "Gsrwsm9BKvfoBLQNw9xWqdDcAFDuvB3Y98uJq6v5eKUPFmy"
        seller_address = ss58_encode(seller_keypair[0], 2)

        trade_value = 10000000000
        fee_value = trade_value * 0.01

        trade_manager = TradeManager(arbitrator_key=arbitrator_hexseed)
        trade_manager.connect(network=network)

        mocker.patch("ksmutils.core.Kusama.get_nonce", return_value=46)

        mocker.patch("ksmutils.network.Network.node_rpc_call")

        escrow_payload, fee_payload = trade_manager.escrow_payloads(
            seller_address, escrow_address, trade_value, fee_value,
        )

        # Only for testing
        signed_payload = helper.sign_payload(seller_keypair, escrow_payload[2:])

        trade_manager.escrow_broadcast(
            signed_payload, seller_address, escrow_address, trade_value
        )

import copy

import pytest

from . import mocked_returns
from ksmutils import Kusama


class TestVersionEndpoint:
    def test_version_check(self, kusama):
        pass


class TestNoNetwork:
    def test_connect_no_network(self, mocker):
        mocker.patch("ksmutils.network.Network.__init__", return_value=None)
        mocker.patch("ksmutils.core.Kusama.check_version", return_value=1062)
        mocker.patch("ksmutils.core.Kusama.get_metadata")
        mocker.patch("ksmutils.core.Kusama.get_spec_version")
        mocker.patch("ksmutils.core.Kusama.get_genesis_hash")
        kusama = Kusama()
        kusama.connect()


class TestGetMethods:
    def test_diagnose(self, kusama):
        escrow_address = "HFXXfXavDuKhLLBhFQTat2aaRQ5CMMw9mwswHzWi76m6iLt"
        result = kusama.diagnose(escrow_address)
        assert result

    def test_bad_address_diagnose(self, kusama):
        escrow_address = "EifTqgEMBpjRD3WnV9jmdN3ArMj1JGKXAKw2eeHCSLw1Bkg"
        result = kusama.diagnose(escrow_address)
        assert result["status"] == "error getting unfinished escrows"

    def test_get_balance(self, kusama):
        result = kusama.get_balance("HsgNgA5sgjuKxGUeaZPJE8rRn9RuixjvnPkVLFUYLEpj15G")

        assert result == 22000000000

    def test_get_nonce(self, kusama):
        result = kusama.get_nonce("HsgNgA5sgjuKxGUeaZPJE8rRn9RuixjvnPkVLFUYLEpj15G")

        assert result == 0

    def test_get_escrow_address(self, kusama):
        buyer_address = "DwRh5ShcnuPzgyhW6J6m4mw1y63hUy1ctR3RSWRSgLg1HQ5"
        seller_address = "CrjrfWVeFM7CFc3fvhwA7etuTdGirnSqBBNBzTiyTcRrPsP"

        result = kusama.get_escrow_address(buyer_address, seller_address)

        assert result == "Fgh5GQ1guNxvurv71cmHm8H5Eo8Ywrdz1mZemffAP2UrrH2"

    def test_get_block(self, kusama, mocker):
        block_hash = (
            "0xa8495cdf2eaf0025966e96b06fba92f647e1e316f2abc698186ecf67919dc52b"
        )

        mocker.patch(
            "ksmutils.network.Network.node_rpc_call",
            return_value=mocked_returns.node_rpc_call_return_2,
        )

        result = kusama.get_block(block_hash)

        expected_number = 2493157
        assert result.get("block").get("header").get("number") == expected_number

    def test_get_events(self, kusama, mocker):
        block_hash = (
            "0xa8495cdf2eaf0025966e96b06fba92f647e1e316f2abc698186ecf67919dc52b"
        )

        mocker.patch(
            "ksmutils.network.Network.node_rpc_call",
            return_value=mocked_returns.node_rpc_call_return_1,
        )

        result = kusama.get_events(block_hash)

        assert len(result) > 0

    def test_get_extrinsic_events(self, kusama, mocker):
        block_hash = (
            "0xa8495cdf2eaf0025966e96b06fba92f647e1e316f2abc698186ecf67919dc52b"
        )
        extrinsic_index = 3

        mocker.patch(
            "ksmutils.core.Kusama.get_events",
            return_value=mocked_returns.get_events_return_1,
        )

        result = kusama.get_extrinsic_events(block_hash, extrinsic_index)
        assert len(result) > 0

        for event in result:
            assert event["extrinsic_idx"] == extrinsic_index

    def test_get_extrinsic_timepoint(self, kusama, mocker):
        node_response = {
            0: {"jsonrpc": "2.0", "result": 723219, "id": 1},
            1: {
                "jsonrpc": "2.0",
                "method": "author_extrinsicUpdate",
                "params": {
                    "result": {
                        "finalized": "0xa8495cdf2eaf0025966e96b06fba92f647e1e316f2abc698186ecf67919dc52b"
                    },
                    "subscription": 723219,
                },
            },
        }

        extrinsic_data = (
            "0x35028444ac0e6cb2c7e9adfcc86919959ff044cd6f6aefcc99152592a4fe8e6d22ce7"
            "701d86d7a5e2fdecb5a927a2e38beb91ec2d7ac97680d8271638676684c3d1f0e5fec54"
            "215035204e2e0d6323e029cee37938c5984bdca37d1c1fa7890cdecd7a8200b0000400b"
            "e51e7d8eb439683272967dfce076362514e8519a51164e73f21272d157b446e0700e40b5402"
        )

        get_block_return_value = copy.deepcopy(mocked_returns.get_block_mock_1)

        mocker.patch(
            "ksmutils.core.Kusama.get_block", return_value=get_block_return_value
        )

        expected_result = (2493157, 3)
        result = kusama.get_extrinsic_timepoint(node_response, extrinsic_data)
        assert result == expected_result

    def test_get_extrinsic_timepoint_exception_1(self, kusama):
        with pytest.raises(Exception) as excinfo:
            kusama.get_extrinsic_timepoint({}, "")
        assert "node_response is empty" in str(excinfo.value)

    def test_get_extrinsic_timepoint_exception_2(self, kusama):
        node_response = {0: {"jsonrpc": "2.0", "result": 723219, "id": 1}}

        with pytest.raises(Exception) as excinfo:
            kusama.get_extrinsic_timepoint(node_response, "")
        assert "Last item in the node_response is not finalized hash" in str(
            excinfo.value
        )

    def test__get_extrinsix_index(self, kusama):
        assert kusama._get_extrinsic_index([], "") == -1

    def test_get_pending_extrinsics(self, kusama, mocker):
        pending_extrinsics = {
            "jsonrpc": "2.0",
            "result": [
                "0x35028444ac0e6cb2c7e9adfcc86919959ff044cd6f6aefcc99152592a4fe8e6d22ce770128866403321ec45a22384a671a8fdb2c22e6fc7920f0585a15e9e5de122e3d0c904069fb7f3116fe5c70813b772d3e26c84e69c6e771aa5163a4c4f23602928f00d8000400be51e7d8eb439683272967dfce076362514e8519a51164e73f21272d157b446e0700e40b5402"
            ],
            "id": 1,
        }

        mocker.patch(
            "ksmutils.network.Network.node_rpc_call", return_value=pending_extrinsics,
        )

        result = kusama.get_pending_extrinsics()
        assert len(result) > 0

    def test_escrow_payloads(self, kusama, mocker):
        seller_address = "D2bHQwFcQj11SvtkjULEdKhK4WAeP6MThXgosMHjW9DrmbE"
        escrow_address = "CofvaLbP3m8PLeNRQmLVPWmTT7jGgAXTwyT69k2wkfPxJ9V"
        trade_value = 9900000000
        fee_value = 100000000
        mocker.patch("ksmutils.core.Kusama.get_nonce", return_value=46)
        result = kusama.escrow_payloads(
            seller_address, escrow_address, trade_value, fee_value
        )
        assert len(result) == 3


class TestNonceManager:
    def test_get_mempool_nonce(self, kusama, mocker):
        mocker.patch(
            "ksmutils.core.Kusama.get_pending_extrinsics",
            return_value=mocked_returns.pending_extrinsics_1,
        )

        nonce = kusama.get_mempool_nonce(
            "E8MtJbGYirK5gw2syuB1G843rhQ454NwTVQXYYvvPtdQqQh"
        )
        assert nonce == 54

        nonce = kusama.get_mempool_nonce(kusama.arbitrator_address)
        assert nonce == -1

    def test_arbitrator_nonce(self, kusama, mocker):
        mocker.patch("ksmutils.core.NonceManager.get_mempool_nonce", return_value=-1)

        mocker.patch("ksmutils.core.Kusama.get_nonce", return_value=2)
        result = kusama.arbitrator_nonce()

        assert result == 2

        mocker.patch("ksmutils.core.NonceManager.get_mempool_nonce", return_value=3)

        result = kusama.arbitrator_nonce()
        assert result == 3


class TestWrapperMethods:
    # These tests aren't really necessary because they just call another
    # function which are already testd,
    # a better way would be to test if that other function
    # gets called ONCE, can't figure out how to do this without unittest
    def test_broadcast(self, kusama, mocker):
        mocker.patch("ksmutils.network.Network.node_rpc_call")

        mocker.patch("ksmutils.core.Kusama.get_extrinsic_hash", return_value="a")
        mocker.patch("ksmutils.core.Kusama.get_block_hash")
        mocker.patch(
            "ksmutils.core.Kusama.get_extrinsic_timepoint", return_value=(1, 2)
        )
        mocker.patch("ksmutils.core.Kusama.get_extrinsic_events", return_value=[])
        mocker.patch("ksmutils.core.Kusama.is_transaction_success", return_value=True)

        result = kusama.broadcast("t", "tx")
        assert result == ("a", (1, 2), True)

    def test_publish(self, kusama, mocker):
        arbitrator_key = (
            "b5643fe4084cae15ffbbc5c1cbe734bec5da9c351f4aa4d44f2897efeb8375c8"
        )
        kusama.setup_arbitrator(arbitrator_key)

        mocker.patch("ksmutils.core.Kusama.broadcast", return_value=True)
        mocker.patch("ksmutils.helper.unsigned_transfer_construction")
        mocker.patch("ksmutils.helper.unsigned_transfer_construction")
        mocker.patch("ksmutils.helper.unsigned_approve_as_multi_construction")
        mocker.patch("ksmutils.helper.unsigned_as_multi_construction")

        assert kusama.publish("transfer", [True])
        assert kusama.publish("fee_transfer", [1, 2, 3, 4])
        assert kusama.publish("approve_as_multi", [1, 2, 3, 4])
        assert kusama.publish("as_multi", [1, 2, 3, 4])

    def test_is_transaction_success(self, kusama):
        assert kusama.is_transaction_success("transfer", [{"event_id": "Transfer"}])

    def test_transfer_payload(self, kusama, mocker):
        mocker.patch("ksmutils.core.Kusama.get_nonce", return_value=4)
        mocker.patch("ksmutils.helper.transfer_signature_payload", return_value=None)

        assert kusama.transfer_payload("", "", 0) is None

    def test_approve_as_multi_payload(self, kusama, mocker):
        mocker.patch("ksmutils.core.Kusama.get_nonce", return_value=4)
        mocker.patch(
            "ksmutils.helper.approve_as_multi_signature_payload", return_value=None
        )

        assert kusama.approve_as_multi_payload("", "", 0, []) == (None, 4)

    def test_as_multi_payload(self, kusama, mocker):
        mocker.patch("ksmutils.core.Kusama.get_nonce", return_value=4)
        mocker.patch("ksmutils.helper.as_multi_signature_payload", return_value=None)

        assert kusama.as_multi_payload("", "", 0, []) == (None, 4)

    def test_release_escrow(self, kusama, mocker):
        mocker.patch("ksmutils.core.Kusama.arbitrator_nonce", return_value=4)
        mocker.patch("ksmutils.helper.as_multi_signature_payload", return_value=None)
        mocker.patch("ksmutils.helper.sign_payload", return_value=None)
        mocker.patch(
            "ksmutils.helper.unsigned_as_multi_construction", return_value="tx"
        )

        assert kusama.release_escrow("", "", (1, 2), []) == "tx"

    def test_cancellation(self, kusama, mocker):
        mocker.patch("ksmutils.core.Kusama.arbitrator_nonce", return_value=4)
        mocker.patch("ksmutils.helper.as_multi_signature_payload", return_value=None)
        mocker.patch("ksmutils.helper.transfer_signature_payload", return_value=None)
        mocker.patch("ksmutils.helper.sign_payload", return_value=None)
        mocker.patch(
            "ksmutils.helper.unsigned_as_multi_construction", return_value="tx"
        )
        mocker.patch(
            "ksmutils.helper.unsigned_transfer_construction", return_value="fx"
        )
        assert kusama.cancellation("", 1, 0.01, [], (1, 2)) == ("tx", "fx")

        with pytest.raises(Exception) as excinfo:
            kusama.cancellation("", 1, 0.02, [], (1, 2)) == ("tx", "fx")
        assert "Fee should not be more than 1% of trade value" in str(excinfo.value)

    def test_resolve_dispute_seller_wins(self, kusama, mocker):
        mocker.patch("ksmutils.core.Kusama.arbitrator_nonce", return_value=4)

        mocker.patch("ksmutils.core.Kusama.cancellation", return_value=("tx", "fx"))

        assert kusama.resolve_dispute("seller", "", 1, 0.01, []) == ("tx", "fx")

    def test_resolve_dispute_buyer_wins(self, kusama, mocker):
        mocker.patch("ksmutils.core.Kusama.arbitrator_nonce", return_value=4)
        mocker.patch(
            "ksmutils.helper.approve_as_multi_signature_payload", return_value=None
        )
        mocker.patch("ksmutils.helper.transfer_signature_payload", return_value=None)
        mocker.patch("ksmutils.helper.sign_payload", return_value=None)
        mocker.patch(
            "ksmutils.helper.unsigned_approve_as_multi_construction", return_value="tx"
        )
        mocker.patch(
            "ksmutils.helper.unsigned_transfer_construction", return_value="wx"
        )

        assert kusama.resolve_dispute("buyer", "", 1, 0.01, []) == ("tx", "wx")

import copy

import pytest

from . import mocked_returns
from substrateutils import Kusama
from substrateutils.cores import NonceManager


class TestVersionEndpoint:
    def test_version_check(self, kusama):
        pass


class TestNoNetwork:
    def test_connect_no_network(self, mocker):
        mocker.patch("substrateutils.network.Network.__init__", return_value=None)
        mocker.patch("substrateutils.cores.Kusama.get_metadata")
        mocker.patch("substrateutils.cores.Kusama.runtime_info")
        mocker.patch("substrateutils.cores.Kusama.get_genesis_hash")
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
            "0x9bee0a6cec7c57e4a0fa999434a8cd5b8a3c603db4a8f829fb8e2bb84d1c96ac"
        )

        result = kusama.get_block(block_hash)

        expected_number = 4886425
        assert result.get("block").get("header").get("number") == expected_number

    def test_get_events(self, kusama, mocker):
        block_hash = (
            "0xedcdb24058b10903807e87b6b1108440cc99583f1780f6b6044ceba3d4ff6924"
        )

        result = kusama.get_events(block_hash)

        assert len(result) > 0

    def test_get_extrinsic_events(self, kusama, mocker):
        block_hash = (
            "0xa8495cdf2eaf0025966e96b06fba92f647e1e316f2abc698186ecf67919dc52b"
        )
        extrinsic_index = 3

        mocker.patch(
            "substrateutils.cores.Kusama.get_events",
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
                        "finalized": "0x5c1b7adc431813938199d58a5e9cb23cb095085b8c0026277022624a7e98e248"
                    },
                    "subscription": 723219,
                },
            },
        }

        extrinsic_data = "0x3d02840080289d77b2a4954ff288c7a320a02b63ddd3bdd29112c7b20ea63ea8fc3d503301580bdf739e89d540d99a67d04b868b20948d4c36e8d2790f7ae425a498ba2d5eb175108f0917888168e0871dcc229f51681036b23c69ae34d6edb04fde24928e008c000400008404ec9dd6e8bb88b32d59c0ac0e24eec6ba3ac5268bbbf4e218c746debf6a4f0700c817a804"

        get_block_return_value = copy.deepcopy(mocked_returns.get_block_mock_1)

        mocker.patch(
            "substrateutils.cores.Kusama.get_block", return_value=get_block_return_value
        )

        expected_result = (9792028, 2)
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
            "substrateutils.network.Network.node_rpc_call",
            return_value=pending_extrinsics,
        )

        result = kusama.get_pending_extrinsics()
        assert len(result) > 0

    def test_escrow_payloads(self, kusama, mocker):
        seller_address = "D2bHQwFcQj11SvtkjULEdKhK4WAeP6MThXgosMHjW9DrmbE"
        escrow_address = "CofvaLbP3m8PLeNRQmLVPWmTT7jGgAXTwyT69k2wkfPxJ9V"
        trade_value = 9900000000
        fee_value = 100000000
        mocker.patch("substrateutils.cores.Kusama.get_nonce", return_value=46)
        result = kusama.escrow_payloads(
            seller_address, escrow_address, trade_value, fee_value
        )
        assert len(result) == 3


class TestNonceManager:
    def test_abstract_methods(self):
        class FakeNonceManager(NonceManager):
            def get_pending_extrinsics(self) -> list:
                super().get_pending_extrinsics()

            def get_nonce(self, address: str) -> int:
                super().get_nonce(address)

        nonce_manager = FakeNonceManager()
        with pytest.raises(NotImplementedError) as excinfo:
            nonce_manager.get_pending_extrinsics()

        assert "Not implemented" in str(excinfo.value)

        with pytest.raises(NotImplementedError) as excinfo:
            nonce_manager.get_nonce("E8MtJbGYirK5gw2syuB1G843rhQ454NwTVQXYYvvPtdQqQh")

        assert "Not implemented" in str(excinfo.value)

    def test_get_mempool_nonce(self, kusama, mocker):
        mocker.patch(
            "substrateutils.cores.Kusama.get_pending_extrinsics",
            return_value=mocked_returns.pending_extrinsics_1,
        )

        nonce = kusama.get_mempool_nonce(
            "E8MtJbGYirK5gw2syuB1G843rhQ454NwTVQXYYvvPtdQqQh"
        )
        assert nonce == 54

        nonce = kusama.get_mempool_nonce(kusama.arbitrator_address)
        assert nonce == -1

    def test_arbitrator_nonce(self, kusama, mocker):
        mocker.patch(
            "substrateutils.cores.NonceManager.get_mempool_nonce", return_value=-1
        )

        mocker.patch("substrateutils.cores.Kusama.get_nonce", return_value=2)
        result = kusama.arbitrator_nonce()

        assert result == 2

        mocker.patch(
            "substrateutils.cores.NonceManager.get_mempool_nonce", return_value=3
        )

        result = kusama.arbitrator_nonce()
        assert result == 3

    def test_arbitrator_nonce_raises_exception(self, kusama, mocker):

        mocker.patch.object(kusama, "arbitrator_address", None)
        with pytest.raises(Exception) as excinfo:
            kusama.arbitrator_nonce()

        assert "Did you forget to setup artitrator address?" in str(excinfo.value)


class TestWrapperMethods:
    # These tests aren't really necessary because they just call another
    # function which are already testd,
    # a better way would be to test if that other function
    # gets called ONCE, can't figure out how to do this without unittest
    def test_broadcast_success(self, kusama, mocker):
        mocker.patch("substrateutils.network.Network.node_rpc_call")

        mocker.patch("substrateutils.cores.Kusama.get_extrinsic_hash", return_value="a")
        mocker.patch("substrateutils.cores.Kusama.get_block_hash")
        mocker.patch(
            "substrateutils.cores.Kusama.get_extrinsic_timepoint", return_value=(1, 2)
        )
        mocker.patch(
            "substrateutils.cores.Kusama.get_extrinsic_events", return_value=[]
        )
        mocker.patch(
            "substrateutils.cores.Kusama.is_transaction_success", return_value=True
        )

        result = kusama.broadcast(
            "transfer",
            "0x3502840c85dc20f15e3d8328b6a162d47ce43771fe6925f0effb8b878bcd1ff28d8f1201986ad54af2d5d8a56df8c6b6674c9d2021b96c9bff3b5f0b292dcfdcbe2e7a2d49f59cfd836df9b070a9de1200285f7023266e7fb055d685fb1277216c67d8830088000400dee35cf94a50737fc2f3c60439e8bae056aabdcde99de4f2d37a5f5957bcec4b0700e40b5403",
        )

        assert result == (True, {"tx_hash": "a", "timepoint": (1, 2)})

    def test_broadcast_fail(self, kusama, mocker):
        """
        mocker.patch("substrateutils.network.Network.node_rpc_call")

        mocker.patch("substrateutils.cores.Kusama.get_extrinsic_hash", return_value=None)
        mocker.patch("substrateutils.cores.Kusama.get_block_hash")
        mocker.patch(
            "substrateutils.cores.Kusama.get_extrinsic_timepoint", return_value=None
        )
        mocker.patch("substrateutils.cores.Kusama.get_extrinsic_events", return_value=[])
        mocker.patch("substrateutils.core.Kusama.is_transaction_success", return_value=False)
        """
        result = kusama.broadcast("t", "tx")
        print(result)
        assert result == (
            False,
            {
                0: {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32602,
                        "message": "Invalid params: 0x prefix is missing.",
                    },
                    "id": 1,
                }
            },
        )

    def test_publish(self, kusama, mocker):
        arbitrator_key = (
            "b5643fe4084cae15ffbbc5c1cbe734bec5da9c351f4aa4d44f2897efeb8375c8"
        )
        kusama.setup_arbitrator(arbitrator_key)

        mocker.patch("substrateutils.cores.Kusama.broadcast", return_value=True)
        mocker.patch("substrateutils.helper.unsigned_transfer_construction")
        mocker.patch("substrateutils.helper.unsigned_transfer_construction")
        mocker.patch("substrateutils.helper.unsigned_as_multi_construction")

        assert kusama.publish("transfer", [True])
        assert kusama.publish("fee_transfer", [1, 2, 3, 4])
        assert kusama.publish("as_multi", [1, 2, 3, 4, 5, 6, 7, 8])

    def test_is_transaction_success(self, kusama):
        assert kusama.is_transaction_success("transfer", [{"event_id": "Transfer"}])

    def test_transfer_payload(self, kusama, mocker):
        mocker.patch("substrateutils.cores.Kusama.get_nonce", return_value=4)
        mocker.patch(
            "substrateutils.helper.transfer_signature_payload", return_value=None
        )

        assert kusama.transfer_payload("", "", 0) is None

    def test_as_multi_payload(self, kusama, mocker):
        mocker.patch("substrateutils.cores.Kusama.get_nonce", return_value=4)
        mocker.patch(
            "substrateutils.helper.as_multi_signature_payload", return_value=None
        )

        assert kusama.as_multi_payload("", "", 0, []) == (None, 4)

    # def test_oct24(self, kusama, mocker):
    #     extrinsic_hash = kusama.get_extrinsic_hash("0x3d02840080289d77b2a4954ff288c7a320a02b63ddd3bdd29112c7b20ea63ea8fc3d503301580bdf739e89d540d99a67d04b868b20948d4c36e8d2790f7ae425a498ba2d5eb175108f0917888168e0871dcc229f51681036b23c69ae34d6edb04fde24928e008c000400008404ec9dd6e8bb88b32d59c0ac0e24eec6ba3ac5268bbbf4e218c746debf6a4f0700c817a804")
    #     block = kusama.get_block("0x5c1b7adc431813938199d58a5e9cb23cb095085b8c0026277022624a7e98e248")
    #     print("+++++++++++++++++++++++++++++++++++++++++++++++")
    #     print(block)
    #     block_number = block.get("block").get("header").get("number")
    #     print(block_number)
    #     print(extrinsic_hash)
    #     extrinsic_index = kusama._get_extrinsic_index(
    #         block.get("block").get("extrinsics"), extrinsic_hash
    #     )
    #     print(extrinsic_index)

import copy

from . import mocked_returns
from ksmutils import Kusama


class TestVersionEndpoint:
    def test_version_check(self, network):
        kusama = Kusama()
        kusama.connect(network=network)


class TestGetMethods:
    def test_get_balance(self, network):
        kusama = Kusama()
        kusama.connect(network=network)

        result = kusama.get_balance("HsgNgA5sgjuKxGUeaZPJE8rRn9RuixjvnPkVLFUYLEpj15G")

        assert result == 22000000000

    def test_get_nonce(self, network):
        kusama = Kusama()
        kusama.connect(network=network)

        result = kusama.get_nonce("HsgNgA5sgjuKxGUeaZPJE8rRn9RuixjvnPkVLFUYLEpj15G")

        assert result == 0

    def test_get_escrow_address(self, network):
        kusama = Kusama(
            arbitrator_key="5c65b9f9f75f95d70b84577ab07e22f7400d394ca3c8bcb227fb6d42920d9b50"
        )
        kusama.connect(network=network)

        buyer_address = "DwRh5ShcnuPzgyhW6J6m4mw1y63hUy1ctR3RSWRSgLg1HQ5"
        seller_address = "CrjrfWVeFM7CFc3fvhwA7etuTdGirnSqBBNBzTiyTcRrPsP"

        result = kusama.get_escrow_address(buyer_address, seller_address)

        assert result == "Fgh5GQ1guNxvurv71cmHm8H5Eo8Ywrdz1mZemffAP2UrrH2"

    def test_get_block(self, network):
        kusama = Kusama()
        kusama.connect(network=network)

        block_hash = (
            "0xa8495cdf2eaf0025966e96b06fba92f647e1e316f2abc698186ecf67919dc52b"
        )

        result = kusama.get_block(block_hash)

        expected_number = 2493157
        print(result)
        assert result.get("block").get("header").get("number") == expected_number

    def test_get_extrinsic_timepoint(self, network, mocker):
        kusama = Kusama()
        kusama.connect(network=network)

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

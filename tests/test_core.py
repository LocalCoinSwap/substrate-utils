from ksmutils import Kusama


class TestVersionEndpoint:
    def test_version_check(self, network):
        kusama = Kusama()
        kusama.connect(network=network)


class TestBalanceEndpoint:
    def test_balance(self, network):
        kusama = Kusama()
        kusama.connect(network=network)

        result = kusama.get_balance("HsgNgA5sgjuKxGUeaZPJE8rRn9RuixjvnPkVLFUYLEpj15G")

        assert result == 22000000000

    def test_nonce(self, network):
        kusama = Kusama()
        kusama.connect(network=network)

        result = kusama.get_nonce("HsgNgA5sgjuKxGUeaZPJE8rRn9RuixjvnPkVLFUYLEpj15G")

        assert result == 0


class TestGetEscrowAddressEndpoint:
    def test_get_escrow_address(self, network):
        kusama = Kusama(
            admin_key="5c65b9f9f75f95d70b84577ab07e22f7400d394ca3c8bcb227fb6d42920d9b50"
        )
        kusama.connect(network=network)

        buyer_addr = "DwRh5ShcnuPzgyhW6J6m4mw1y63hUy1ctR3RSWRSgLg1HQ5"
        seller_addr = "CrjrfWVeFM7CFc3fvhwA7etuTdGirnSqBBNBzTiyTcRrPsP"

        result = kusama.get_escrow_address(buyer_addr, seller_addr)

        assert result == "Fgh5GQ1guNxvurv71cmHm8H5Eo8Ywrdz1mZemffAP2UrrH2"

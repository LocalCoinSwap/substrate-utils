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

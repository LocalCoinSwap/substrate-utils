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

class TestGetEscrowAddressEndpoint():
    def test_get_escrow_address(self, network):
        kusama = Kusama(admin_addr="HvqnQxDQbi3LL2URh7WQfcmi8b2ZWfBhu7TEDmyyn5VK8e2")
        kusama.connect(network=network)

        buyer_addr = "CdVuGwX71W4oRbXHsLuLQxNPns23rnSSiZwZPN4etWf6XYo"
        seller_addr = "J9aQobenjZjwWtU2MsnYdGomvcYbgauCnBeb8xGrcqznvJc"

        result = kusama.get_escrow_address(buyer_addr, seller_addr)

        assert result == "HFXXfXavDuKhLLBhFQTat2aaRQ5CMMw9mwswHzWi76m6iLt"

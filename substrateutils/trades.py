import bip39
import sr25519
from scalecodec.utils.ss58 import ss58_encode

from .cores import Polkadot
from .cores import SubstrateBase
from .helper import sign_payload


class User:
    def __init__(self, address_type=0, *, mnemonic=None, hex=None):
        if mnemonic:
            seed_bytes = bip39.bip39_to_mini_secret(mnemonic, "")
            seed_hex = bytearray(seed_bytes).hex()
            self.hex = seed_hex
        if hex:
            self.hex = hex

        self.keypair = sr25519.pair_from_seed(bytes.fromhex(self.hex))
        self.public_key = self.keypair[0].hex()
        self.private_key = self.keypair[1].hex()
        self.address = ss58_encode(self.keypair[0], address_type)


class TradeManager:
    def __init__(
        self,
        buyer: "User" = None,
        seller: "User" = None,
        arbitrator: "User" = None,
        value: int = 0,
        *,
        chain: "SubstrateBase" = None,
        fee_value: int = 1,  # %
    ):
        self.buyer = buyer
        self.seller = seller
        self.arbitrator = arbitrator
        if chain:
            core = chain
        else:
            core = Polkadot(arbitrator_key=arbitrator.hex)
        self.chain = core
        self.chain.connect()
        self.escrow_address = core.get_escrow_address(
            self.buyer.address, self.seller.address
        )
        self.value = value
        self.fee_value = fee_value
        self.status = "CREATED"

    def fund_escrow(self):
        escrow_payload, fee_payload, nonce = self.chain.escrow_payloads(
            self.seller.address, self.escrow_address, self.value, self.fee_value,
        )
        escrow_signature = sign_payload(self.seller.keypair, escrow_payload)
        fee_signature = sign_payload(self.seller.keypair, fee_payload)
        _, self.escrow_tx = self.chain.publish(
            "transfer",
            [
                self.seller.address,
                escrow_signature,
                nonce,
                self.escrow_address,
                self.value,
            ],
        )
        _, self.fee_tx = self.chain.publish(
            "fee_transfer",
            [self.seller.address, fee_signature, nonce + 1, self.fee_value],
        )
        self.status = "FUNDED_ESCROW"

    def release(self):
        transaction = self.chain.as_multi_storage(
            self.buyer.address, self.seller.address, self.value,
        )

        _, self.release_arb_tx = self.chain.broadcast("as_multi", transaction)

        as_multi_payload, nonce = self.chain.as_multi_payload(
            self.seller.address,
            self.buyer.address,
            self.value,
            [self.buyer.address, self.arbitrator.address],
            self.release_arb_tx["timepoint"],
            False,
        )
        as_multi_signature = sign_payload(self.seller.keypair, as_multi_payload)
        _, self.release_seller = self.chain.publish(
            "as_multi",
            [
                self.seller.address,
                as_multi_signature,
                nonce,
                self.buyer.address,
                self.value,
                self.release_arb_tx["timepoint"],
                [self.buyer.address, self.arbitrator.address],
                0,
            ],
        )
        self.status = "RELEASE"

    def cancel(self):
        transaction = self.chain.as_multi_storage(
            self.seller.address, self.buyer.address, self.value
        )

        _, self.cancel_tx = self.chain.broadcast("as_multi", transaction)

        transaction = self.chain.fee_return_transaction(
            self.seller.address, self.value, self.fee_value,
        )
        _, self.cancel_arb_tx = self.chain.broadcast("transfer", transaction)

        as_multi_payload, nonce = self.chain.as_multi_payload(
            self.seller.address,
            self.seller.address,
            self.value,
            [self.buyer.address, self.chain.arbitrator_address],
            self.cancel_tx["timepoint"],
            False,
        )

        as_multi_signature = sign_payload(self.seller.keypair, as_multi_payload)
        _, self.cancel_seller_tx = self.chain.publish(
            "as_multi",
            [
                self.seller.address,
                as_multi_signature,
                nonce,
                self.seller.address,
                self.value,
                self.cancel_tx["timepoint"],
                [self.buyer.address, self.chain.arbitrator_address],
                0,
            ],
        )
        self.status = "CANCELLED"

    def dispute(self, winner="SELLER"):
        if winner == "BUYER":
            to = self.buyer.address
            other = self.seller.address
        else:
            to = self.seller.address
            other = self.buyer.address
        transaction = self.chain.as_multi_storage(to, other, self.value)

        _, self.dispute_arb = self.chain.broadcast("as_multi", transaction)

        if winner == "BUYER":
            transaction = self.chain.welfare_transaction(self.buyer.address,)
        else:
            transaction = self.chain.fee_return_transaction(
                self.seller.address, self.value, self.fee_value,
            )
        _, self.dispute_special_tx = self.chain.broadcast("transfer", transaction)

        if winner == "BUYER":
            to = self.buyer
            other = self.seller
        else:
            to = self.seller
            other = self.buyer
        as_multi_payload, nonce = self.chain.as_multi_payload(
            to.address,
            to.address,
            self.value,
            [other.address, self.chain.arbitrator_address],
            self.dispute_arb["timepoint"],
            False,
        )

        as_multi_signature = sign_payload(to.keypair, as_multi_payload)
        _, self.dispute_user_tx = self.chain.publish(
            "as_multi",
            [
                to.address,
                as_multi_signature,
                nonce,
                to.address,
                self.value,
                self.dispute_arb["timepoint"],
                [other.address, self.chain.arbitrator_address],
                0,
            ],
        )
        self.status = "DISPUTED"

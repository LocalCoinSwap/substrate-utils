import sr25519

from substrateutils.helper import get_prefix
from substrateutils.helper import order_addresses
from substrateutils.helper import sign_payload
from substrateutils.helper import transfer_signature_payload
from substrateutils.helper import unsigned_as_multi_construction
from substrateutils.helper import unsigned_transfer_construction
from substrateutils.helper import xx128


class TestSignaturePayloads:
    def test_xx128(self):
        assert (
            xx128("Utility") + xx128("Multisigs")
            == "d5e1a2fa16732ce6906189438c0a82c63cd15a3fd6e04e47bee3922dbfa92c8d"
        )

    def test_get_prefix(self):
        escrow_address = "HFXXfXavDuKhLLBhFQTat2aaRQ5CMMw9mwswHzWi76m6iLt"
        assert len(get_prefix(escrow_address)) == 144

    def test_transfer_payload(self, kusama):
        """
        metadata, address, value, nonce, genesis_hash, spec_version
        """
        value = 10000000000
        address = "Ed7AYYmMQYRmU7sbwijGgLkRfhNYnMrBZ5epigL2c2FyBbU"
        nonce = 4
        result = transfer_signature_payload(
            kusama.metadata,
            address,
            value,
            nonce,
            kusama.genesis_hash,
            kusama.spec_version,
            runtime_config=kusama.runtime_config,
        )
        assert len(result) == 232 and result[0:2] == "0x"


class TestPayloadConstruction:
    def test_transfer_construction(self, kusama):
        """
        metadata, account_id, signature, nonce, to_address, amount
        """
        account_id = (
            "0x14097421065c7bb0efc6770ffc5d604654159d45910cc7a3cb602be16acc5528"
        )
        amount = 10000000000
        to_address = "Ed7AYYmMQYRmU7sbwijGgLkRfhNYnMrBZ5epigL2c2FyBbU"
        nonce = 4
        signature = (
            "0x820a0bddcf9793603c6d5abf54bfad0053adaa4d4ac5147c81135f12a699c254ea82d4ce"
            "5829d7e39910f28b6198c89b8c172398ff6e1367fd90c710a3bc3e89"
        )
        expected_final_extrinsic = (
            "0x35028414097421065c7bb0efc6770ffc5d604654159d45910cc7a3cb602be16acc552801"
            "820a0bddcf9793603c6d5abf54bfad0053adaa4d4ac5147c81135f12a699c254ea82d4ce58"
            "29d7e39910f28b6198c89b8c172398ff6e1367fd90c710a3bc3e8900100004005a989f0526"
            "b8a619b90205b6c3bef293f7b0c38fae7353afe10feae4c471255b0700e40b5402"
        )
        result = unsigned_transfer_construction(
            kusama.metadata,
            account_id,
            signature,
            nonce,
            to_address,
            amount,
            runtime_config=kusama.runtime_config,
        )
        assert result == expected_final_extrinsic

    def test_as_multi_construction(self, kusama):
        """
        metadata, account_id, signature, nonce, to_address, amount, timepoint,
        other_signatories
        """
        account_id = (
            "0x5ed592d82e3711f9b0655ed39aa591a008c04d1aada60dbb541375250dc2ff4e"
        )
        signature = (
            "0x7cfbed1268b30829ab48dee7ba97c12b7c7e0c299539eb7f64a8fc69995f9d2e5f4a63f63"
            "3b9e78021d30393afe085ab8f1f8479ec471a85a5ec142723b9e58e"
        )
        amount = 9900000000
        timepoint = (9000, 1)
        to_address = "CofvaLbP3m8PLeNRQmLVPWmTT7jGgAXTwyT69k2wkfPxJ9V"
        nonce = 5
        other_signatories = [
            "CofvaLbP3m8PLeNRQmLVPWmTT7jGgAXTwyT69k2wkfPxJ9V",
            "D2bHQwFcQj11SvtkjULEdKhK4WAeP6MThXgosMHjW9DrmbE",
        ]
        result = unsigned_as_multi_construction(
            kusama.metadata,
            account_id,
            signature,
            nonce,
            to_address,
            amount,
            timepoint,
            other_signatories,
            "0xb0a8d493285c2df73290dfb7e61f870f17b41801197a149ca93654499ea3dafe",
            runtime_config=kusama.runtime_config,
        )
        assert len(result) == 464 and result[0:2] == "0x"

    def test_sign_payload(self):
        payload = (
            "04005a989f0526b8a619b90205b6c3bef293f7b0c38fae7353afe10feae4c4712"
            "55b0700e40b540200100026040000b0a8d493285c2df73290dfb7e61f870f17b418"
            "01197a149ca93654499ea3dafeb0a8d493285c2df73290dfb7e61f870f17b418011"
            "97a149ca93654499ea3dafe"
        )
        signer_hex = "52bb9cee00b1f93a8ff5c022360c97457a7bd1e7c9387002728cac022aedf1b0"

        keypair = sr25519.pair_from_seed(bytes.fromhex(signer_hex))
        result = sign_payload(keypair, payload)
        assert len(result) == 128

    def test_sign_0x_payload(self):
        payload = (
            "0x04005a989f0526b8a619b90205b6c3bef293f7b0c38fae7353afe10feae4c4712"
            "55b0700e40b540200100026040000b0a8d493285c2df73290dfb7e61f870f17b418"
            "01197a149ca93654499ea3dafeb0a8d493285c2df73290dfb7e61f870f17b418011"
            "97a149ca93654499ea3dafe"
        )
        signer_hex = "52bb9cee00b1f93a8ff5c022360c97457a7bd1e7c9387002728cac022aedf1b0"

        keypair = sr25519.pair_from_seed(bytes.fromhex(signer_hex))
        result = sign_payload(keypair, payload)
        assert len(result) == 128

    def test_order_addresses(self):
        out_of_order_addresses = [
            "126ehG4n9BkmV8HKtQUqBHoTCwv5ogPA7F8X7giJrXZqA6Hs",
            "1HZVSdsyXmeR6E1RpcTPdGMkw4bi5J6pvVxbS9zPA4acvmN",
        ]
        ordered_addresses = [
            "1HZVSdsyXmeR6E1RpcTPdGMkw4bi5J6pvVxbS9zPA4acvmN",
            "126ehG4n9BkmV8HKtQUqBHoTCwv5ogPA7F8X7giJrXZqA6Hs",
        ]

        result = order_addresses(out_of_order_addresses)
        assert result[0] == ordered_addresses[0]
        assert result[1] == ordered_addresses[1]

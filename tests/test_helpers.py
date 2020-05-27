from .fixtures import genesis_hash
from .fixtures import metadata
from .fixtures import spec_version
from ksmutils.helper import approve_as_multi_signature_payload
from ksmutils.helper import as_multi_signature_payload
from ksmutils.helper import transfer_signature_payload
from ksmutils.helper import unsigned_approve_as_multi_construction
from ksmutils.helper import unsigned_as_multi_construction
from ksmutils.helper import unsigned_transfer_construction


class TestSignaturePayloads:
    def test_transfer_payload(self):
        """
        metadata, address, value, nonce, genesis_hash, spec_version
        """
        value = 10000000000
        address = "Ed7AYYmMQYRmU7sbwijGgLkRfhNYnMrBZ5epigL2c2FyBbU"
        nonce = 4
        expected_signature_payload = (
            "0x04005a989f0526b8a619b90205b6c3bef293f7b0c38fae7353afe10feae4c4712"
            "55b0700e40b540200100026040000b0a8d493285c2df73290dfb7e61f870f17b418"
            "01197a149ca93654499ea3dafeb0a8d493285c2df73290dfb7e61f870f17b418011"
            "97a149ca93654499ea3dafe"
        )
        result = transfer_signature_payload(
            metadata, address, value, nonce, genesis_hash, spec_version
        )
        assert result == expected_signature_payload

    def test_approve_as_multi_payload(self):
        """
        metadata, spec_version, genesis_hash, nonce, to_address, amount,
        other_signatories, threshold=2, tip=0
        """
        nonce = 4
        to_address = "CofvaLbP3m8PLeNRQmLVPWmTT7jGgAXTwyT69k2wkfPxJ9V"
        amount = 9900000000
        other_signatories = [
            "EifTqgEMBpjRD3WnV9jmdN3ArMj1JGKXAKw2eeHCSLw1Bkg",
            "CofvaLbP3m8PLeNRQmLVPWmTT7jGgAXTwyT69k2wkfPxJ9V",
        ]

        expected_signature_payload = (
            "0x18030200080a2ee2acc37fa96e818e2817afc104ce55770bcccb7333bbf848"
            "1d5bc3c6fa465ed592d82e3711f9b0655ed39aa591a008c04d1aada60dbb5413"
            "75250dc2ff4e004fb795510de9b60a094066dbfa0dc1283371735779dda481ea"
            "5d7ad7725a00f600100026040000b0a8d493285c2df73290dfb7e61f870f17b4"
            "1801197a149ca93654499ea3dafeb0a8d493285c2df73290dfb7e61f870f17b4"
            "1801197a149ca93654499ea3dafe"
        )
        result = approve_as_multi_signature_payload(
            metadata,
            spec_version,
            genesis_hash,
            nonce,
            to_address,
            amount,
            other_signatories,
        )
        assert result == expected_signature_payload

    def test_as_multi_payload(self):
        """
        metadata, spec_version, genesis_hash, nonce, to_address, amount,
        other_signatories, timepoint, threshold=2, tip=0,
        """
        nonce = 5
        to_address = "CofvaLbP3m8PLeNRQmLVPWmTT7jGgAXTwyT69k2wkfPxJ9V"
        amount = 9900000000
        other_signatories = [
            "CofvaLbP3m8PLeNRQmLVPWmTT7jGgAXTwyT69k2wkfPxJ9V",
            "D2bHQwFcQj11SvtkjULEdKhK4WAeP6MThXgosMHjW9DrmbE",
        ]
        timepoint = (9000, 1)
        expected_signature_payload = (
            "0x18020200080a2ee2acc37fa96e818e2817afc104ce55770bcccb7333b"
            "bf8481d5bc3c6fa4614097421065c7bb0efc6770ffc5d604654159d4591"
            "0cc7a3cb602be16acc552801282300000100000004000a2ee2acc37fa96"
            "e818e2817afc104ce55770bcccb7333bbf8481d5bc3c6fa46070003164e"
            "0200140026040000b0a8d493285c2df73290dfb7e61f870f17b41801197"
            "a149ca93654499ea3dafeb0a8d493285c2df73290dfb7e61f870f17b418"
            "01197a149ca93654499ea3dafe"
        )
        result = as_multi_signature_payload(
            metadata,
            spec_version,
            genesis_hash,
            nonce,
            to_address,
            amount,
            other_signatories,
            timepoint,
        )
        assert result == expected_signature_payload


class TestPayloadConstruction:
    def test_transfer_construction(self):
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
            metadata, account_id, signature, nonce, to_address, amount
        )
        assert result == expected_final_extrinsic

    def test_approve_as_multi_construction(self):
        """
        metadata, account_id, signature, nonce, to_address, amount,
        other_signatories
        """
        account_id = (
            "0x14097421065c7bb0efc6770ffc5d604654159d45910cc7a3cb602be16acc5528"
        )
        signature = (
            "0x26ef62025f86b150442d1e1f2996dce635b591250f60a532dc32f8cf319c6515eea9bb7"
            "60e442b6a816aef9fdbc535eca0d663e9b9d783a0616153df2ac0fd87"
        )
        expected_final_extrinsic = (
            "0x2d038414097421065c7bb0efc6770ffc5d604654159d45910cc7a3cb602be16acc55280"
            "126ef62025f86b150442d1e1f2996dce635b591250f60a532dc32f8cf319c6515eea9bb76"
            "0e442b6a816aef9fdbc535eca0d663e9b9d783a0616153df2ac0fd8700100018030200080"
            "a2ee2acc37fa96e818e2817afc104ce55770bcccb7333bbf8481d5bc3c6fa465ed592d82e"
            "3711f9b0655ed39aa591a008c04d1aada60dbb541375250dc2ff4e004fb795510de9b60a0"
            "94066dbfa0dc1283371735779dda481ea5d7ad7725a00f6"
        )
        amount = 9900000000
        to_address = "CofvaLbP3m8PLeNRQmLVPWmTT7jGgAXTwyT69k2wkfPxJ9V"
        nonce = 4
        other_signatories = [
            "EifTqgEMBpjRD3WnV9jmdN3ArMj1JGKXAKw2eeHCSLw1Bkg",
            "CofvaLbP3m8PLeNRQmLVPWmTT7jGgAXTwyT69k2wkfPxJ9V",
        ]
        result = unsigned_approve_as_multi_construction(
            metadata,
            account_id,
            signature,
            nonce,
            to_address,
            amount,
            other_signatories,
        )
        assert result == expected_final_extrinsic

    def test_as_multi_construction(self):
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
        expected_final_extrinsic = (
            "0x6d03845ed592d82e3711f9b0655ed39aa591a008c04d1aada60dbb541375250dc2ff4e017"
            "cfbed1268b30829ab48dee7ba97c12b7c7e0c299539eb7f64a8fc69995f9d2e5f4a63f633b9"
            "e78021d30393afe085ab8f1f8479ec471a85a5ec142723b9e58e00140018020200080a2ee2a"
            "cc37fa96e818e2817afc104ce55770bcccb7333bbf8481d5bc3c6fa4614097421065c7bb0ef"
            "c6770ffc5d604654159d45910cc7a3cb602be16acc552801282300000100000004000a2ee2a"
            "cc37fa96e818e2817afc104ce55770bcccb7333bbf8481d5bc3c6fa46070003164e02"
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
            metadata,
            account_id,
            signature,
            nonce,
            to_address,
            amount,
            timepoint,
            other_signatories,
        )
        assert result == expected_final_extrinsic

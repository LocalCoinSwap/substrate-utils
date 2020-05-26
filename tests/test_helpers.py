from .fixtures import genesis_hash
from .fixtures import metadata
from .fixtures import spec_version
from ksmutils.helper import transfer_signature_payload
from ksmutils.helper import unsigned_transfer_construction

# from ksmutils.helper import approve_as_multi_signature_payload
# from ksmutils.helper import as_multi_signature_payload
# from ksmutils.helper import unsigned_approve_as_multi_construction
# from ksmutils.helper import unsigned_as_multi_construction


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
        pass

    def test_as_multi_payload(self):
        """
        metadata, spec_version, genesis_hash, nonce, to_address, amount,
        other_signatories, timepoint, threshold=2, tip=0,
        """
        pass


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
        pass

    def test_as_multi_construction(self):
        """
        metadata, account_id, signature, nonce, to_address, amount, timepoint,
        other_signatories
        """
        pass

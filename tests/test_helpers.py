from .fixtures import genesis_hash
from .fixtures import metadata
from .fixtures import spec_version
from ksmutils.helper import transfer_signature_payload

# from ksmutils.helper import approve_as_multi_signature_payload
# from ksmutils.helper import as_multi_signature_payload

# from ksmutils.helper import unsigned_approve_as_multi_construction
# from ksmutils.helper import unsigned_as_multi_construction
# from ksmutils.helper import unsigned_transfer_construction


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
        pass

    def test_approve_as_multi_construction(self):
        pass

    def test_as_multi_construction(self):
        pass

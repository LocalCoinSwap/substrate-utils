class TestBasicConnection:
    def test_basic_connection(self, network):
        storage_key = (
            "0x26aa394eea5630e07c48ae0c9558cef780d41e5e16056765bc8461851072c9d7"
        )

        test_block = (
            "0x9371a6742726810f20ef7e26c53a141270d76e50b2c636baa4a0a1f5961f33ef"
        )
        result = network.node_rpc_call("state_getStorage", [storage_key, test_block])[
            "result"
        ]

        expected_result = (
            "0x1800000000000000c0257a09000000000200000001000000000000ca9a3b000000000200000"
            "0020000001102da91521070ef71375c5db41bc7f6276b3048178bd7456322fbced4a756886620"
            "e58625bc778dcd2dd0faaba532be4cdc0a44a5796eacbd6297c8783698d526d8f526cf0bfe78f"
            "cc5c2d69a44c7b10ca9533cadb95ed94fdcb1da14b50f3a27b00000020000000d060008af2f00"
            "000000000000000000000000000200000002041a7938fede32e1275281b3eee5708706d88444a"
            "6dc898a4dec463f1eb298463f00c2eb0b000000000000000000000000000002000000000000a8"
            "250a00000000000000"
        )

        assert result == expected_result

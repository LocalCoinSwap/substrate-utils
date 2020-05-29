get_block_mock_1 = {
    "block": {
        "extrinsics": [
            {"valueRaw": "040200", "extrinsic_length": 10},
            {"valueRaw": "040900", "extrinsic_length": 7},
            {"valueRaw": "041400", "extrinsic_length": 4},
            {
                "valueRaw": "840400",
                "extrinsic_length": 141,
                "version_info": "84",
                "account_length": "ff",
                "account_id": "44ac0e6cb2c7e9adfcc86919959ff044cd6f6aefcc99152592a4fe8e6d22ce77",
                "account_index": None,
                "account_idx": None,
                "signature_version": 1,
                "signature": "d86d7a5e2fdecb5a927a2e38beb91ec2d7ac97680d8271638676684c3d1f0e5fec54215035204e2e0d6323e029cee37938c5984bdca37d1c1fa7890cdecd7a82",
                "extrinsic_hash": "a07d72e9ad68bed3177252c3646fc82874d9e9d524d02b8a1be2a36a761457ee",
                "call_code": "0400",
                "call_function": "transfer",
                "call_module": "balances",
                "nonce": 44,
                "era": "00",
                "tip": 0,
                "params": [
                    {
                        "name": "dest",
                        "type": "Address",
                        "value": "0xbe51e7d8eb439683272967dfce076362514e8519a51164e73f21272d157b446e",
                        "valueRaw": "",
                    },
                    {
                        "name": "value",
                        "type": "Compact<Balance>",
                        "value": 10000000000,
                        "valueRaw": "0700e40b5402",
                    },
                ],
            },
        ],
        "header": {
            "digest": {"logs": []},
            "extrinsicsRoot": "0x279e02b9226cc0cef2e52a1b7d85ca29cc4d29e7becd371cda8d3c01c51de654",
            "number": 2493157,
            "parentHash": "0x689c6a7b41d3ed6dd3d2bf682675a17a86e5bfd83c005aa1881c165ada73a534",
            "stateRoot": "0xf6fc126880916cbca767412ba1cc64ba96b500b155af7cc46f89388c8710c196",
        },
    },
    "justification": None,
}

node_rpc_call_return_1 = "0x1c00000000000000c0257a09000000000200000001000000000000000000000000000200000002000000000000ca9a3b000000000200000003000000020244ac0e6cb2c7e9adfcc86919959ff044cd6f6aefcc99152592a4fe8e6d22ce77be51e7d8eb439683272967dfce076362514e8519a51164e73f21272d157b446e00e40b540200000000000000000000000000030000000d060008af2f00000000000000000000000000000300000002043412f138b55741bb9dd7b4413ad55b00ed2c0b06654b73433d69ccb2e4a4214700c2eb0b0000000000000000000000000000030000000000c0769f0b00000000000000"

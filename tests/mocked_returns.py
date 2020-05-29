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

node_rpc_call_return_1 = {
    "jsonrpc": "2.0",
    "result": "0x1c00000000000000c0257a09000000000200000001000000000000000000000000000200000002000000000000ca9a3b000000000200000003000000020244ac0e6cb2c7e9adfcc86919959ff044cd6f6aefcc99152592a4fe8e6d22ce77be51e7d8eb439683272967dfce076362514e8519a51164e73f21272d157b446e00e40b540200000000000000000000000000030000000d060008af2f00000000000000000000000000000300000002043412f138b55741bb9dd7b4413ad55b00ed2c0b06654b73433d69ccb2e4a4214700c2eb0b0000000000000000000000000000030000000000c0769f0b00000000000000",
    "id": 1,
}

node_rpc_call_return_2 = {
    "jsonrpc": "2.0",
    "result": {
        "block": {
            "extrinsics": [
                "0x280402000b60b07e577201",
                "0x1c0409008a2b9800",
                "0x1004140000",
                "0x35028444ac0e6cb2c7e9adfcc86919959ff044cd6f6aefcc99152592a4fe8e6d22ce7701d86d7a5e2fdecb5a927a2e38beb91ec2d7ac97680d8271638676684c3d1f0e5fec54215035204e2e0d6323e029cee37938c5984bdca37d1c1fa7890cdecd7a8200b0000400be51e7d8eb439683272967dfce076362514e8519a51164e73f21272d157b446e0700e40b5402",
            ],
            "header": {
                "digest": {
                    "logs": [
                        "0x0642414245b5010196000000aa1ecd0f00000000b0b938a0d0806425117cdb0683d8daa9e4b1a97ab126da764b076fcf459ecc67ca18a3938872e7755d06963f1f7e57bcefa0dca6a5618b0696358a3c2d4b4801d1f6c6e7a1f5ed1b074c22789134ad1ac3a22192d189a5e85de7de8cc791b409",
                        "0x054241424501011a8d8474fcd4f72b548b4f380a8b7f562d249cd7a52fb8041c64e4cba8cd102ad93fe499d80c066c2ec7a90670ab0ace12428d61ed7a67f185d93dd5f4ea488a",
                    ]
                },
                "extrinsicsRoot": "0x279e02b9226cc0cef2e52a1b7d85ca29cc4d29e7becd371cda8d3c01c51de654",
                "number": "0x260ae5",
                "parentHash": "0x689c6a7b41d3ed6dd3d2bf682675a17a86e5bfd83c005aa1881c165ada73a534",
                "stateRoot": "0xf6fc126880916cbca767412ba1cc64ba96b500b155af7cc46f89388c8710c196",
            },
        },
        "justification": None,
    },
    "id": 1,
}

get_events_return_1 = [
    {
        "phase": 0,
        "extrinsic_idx": 0,
        "type": "0000",
        "module_id": "System",
        "event_id": "ExtrinsicSuccess",
        "params": [
            {
                "type": "DispatchInfo",
                "value": {"weight": 159000000, "class": "Mandatory", "paysFee": "Yes"},
                "valueRaw": "",
            }
        ],
        "topics": [],
        "event_idx": 0,
    },
    {
        "phase": 0,
        "extrinsic_idx": 1,
        "type": "0000",
        "module_id": "System",
        "event_id": "ExtrinsicSuccess",
        "params": [
            {
                "type": "DispatchInfo",
                "value": {"weight": 0, "class": "Mandatory", "paysFee": "Yes"},
                "valueRaw": "",
            }
        ],
        "topics": [],
        "event_idx": 1,
    },
    {
        "phase": 0,
        "extrinsic_idx": 2,
        "type": "0000",
        "module_id": "System",
        "event_id": "ExtrinsicSuccess",
        "params": [
            {
                "type": "DispatchInfo",
                "value": {"weight": 1000000000, "class": "Mandatory", "paysFee": "Yes"},
                "valueRaw": "",
            }
        ],
        "topics": [],
        "event_idx": 2,
    },
    {
        "phase": 0,
        "extrinsic_idx": 3,
        "type": "0202",
        "module_id": "Balances",
        "event_id": "Transfer",
        "params": [
            {
                "type": "AccountId",
                "value": "0x44ac0e6cb2c7e9adfcc86919959ff044cd6f6aefcc99152592a4fe8e6d22ce77",
                "valueRaw": "44ac0e6cb2c7e9adfcc86919959ff044cd6f6aefcc99152592a4fe8e6d22ce77",
            },
            {
                "type": "AccountId",
                "value": "0xbe51e7d8eb439683272967dfce076362514e8519a51164e73f21272d157b446e",
                "valueRaw": "be51e7d8eb439683272967dfce076362514e8519a51164e73f21272d157b446e",
            },
            {
                "type": "Balance",
                "value": 10000000000,
                "valueRaw": "00e40b54020000000000000000000000",
            },
        ],
        "topics": [],
        "event_idx": 3,
    },
    {
        "phase": 0,
        "extrinsic_idx": 3,
        "type": "0d06",
        "module_id": "Treasury",
        "event_id": "Deposit",
        "params": [
            {
                "type": "Balance",
                "value": 800000000,
                "valueRaw": "0008af2f000000000000000000000000",
            }
        ],
        "topics": [],
        "event_idx": 4,
    },
    {
        "phase": 0,
        "extrinsic_idx": 3,
        "type": "0204",
        "module_id": "Balances",
        "event_id": "Deposit",
        "params": [
            {
                "type": "AccountId",
                "value": "0x3412f138b55741bb9dd7b4413ad55b00ed2c0b06654b73433d69ccb2e4a42147",
                "valueRaw": "3412f138b55741bb9dd7b4413ad55b00ed2c0b06654b73433d69ccb2e4a42147",
            },
            {
                "type": "Balance",
                "value": 200000000,
                "valueRaw": "00c2eb0b000000000000000000000000",
            },
        ],
        "topics": [],
        "event_idx": 5,
    },
    {
        "phase": 0,
        "extrinsic_idx": 3,
        "type": "0000",
        "module_id": "System",
        "event_id": "ExtrinsicSuccess",
        "params": [
            {
                "type": "DispatchInfo",
                "value": {"weight": 195000000, "class": "Normal", "paysFee": "Yes"},
                "valueRaw": "",
            }
        ],
        "topics": [],
        "event_idx": 6,
    },
]

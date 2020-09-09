## Trading using only as-multi flow

```python
import os
import sr25519

from ksmutils import Kusama
from ksmutils.helper import sign_payload
from ksmutils.helper import hex_to_bytes
from scalecodec.utils.ss58 import ss58_encode
from dotenv import load_dotenv

# VARIABLES AND SETUP
load_dotenv()
arbitrator_seed = os.getenv("ARB_SEED")
seller_seed = os.getenv("SELLER_SEED")
buyer_seed = os.getenv("BUYER_SEED")

kusama = Kusama()
kusama.setup_arbitrator(arbitrator_seed)
kusama.connect()

seller_keypair = sr25519.pair_from_seed(hex_to_bytes(seller_seed))
buyer_keypair = sr25519.pair_from_seed(hex_to_bytes(buyer_seed))
buyer_address = ss58_encode(buyer_keypair[0], 2)
seller_address = ss58_encode(seller_keypair[0], 2)

escrow_address = kusama.get_escrow_address(buyer_address, seller_address)

trade_value = 10000000000 # Plancks = 0.01 KSM
fee_value = 100000000 # Plancks = 0.0001 KSM

# GET PAYLOADS, SIGN, PUBLISH ESCROW AND FEE
escrow_payload, fee_payload, nonce = kusama.escrow_payloads(
    seller_address, escrow_address, trade_value, fee_value)

escrow_signature = sign_payload(seller_keypair, escrow_payload)
fee_signature = sign_payload(seller_keypair, fee_payload)

"""
# Example: 0x4357ba41eb3a74770f5741b7bb23709ec63e8cd30a1aade021bce7dfc80ea305
success, response = kusama.publish(
    'transfer',
    [seller_address, escrow_signature, nonce, escrow_address, trade_value]
)
# Example: 0xdc384bbd69959038a5f413fe59903be8156189bdccaaab4ec0a27dff85ce4329
success, response = kusama.publish(
    'fee_transfer',
    [seller_address, fee_signature, nonce + 1, fee_value]
)
"""

# ARBITRATER MAKES STORAGE AS_MULTI
transaction = kusama.as_multi_storage(
    buyer_address, # To address
    seller_address,
    trade_value
)

"""
# Example: 0xb9899405c3cdda9352cb3a72e6c10077c0c08ae54bb5506ebae4f437c436c99d
# timepoint = (3971685, 1)
success, response = kusama.broadcast(
    'as_multi', transaction
)
timepoint = response['timepoint']
"""

# SELLERS MAKES REGULAR AS_MULTI TO COMPLETE
as_multi_payload, nonce = kusama.as_multi_payload(
    seller_address,
    buyer_address,
    trade_value,
    [buyer_address, kusama.arbitrator_address],
    timepoint,
    False,
    999999999999,
)
as_multi_signature = sign_payload(seller_keypair, as_multi_payload)
success, response = kusama.publish(
    'as_multi',
    [
        seller_address,
        as_multi_signature,
        nonce,
        buyer_address,
        trade_value,
        timepoint,
        [buyer_address, kusama.arbitrator_address],
        999999999999,
    ]
)
```

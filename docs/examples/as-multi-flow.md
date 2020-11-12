## Trading using only as-multi flow

```python
import os
import sr25519

from substrateutils import Kusama
from substrateutils.helper import sign_payload
from substrateutils.helper import hex_to_bytes
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

success, response = kusama.publish(
    'transfer',
    [seller_address, escrow_signature, nonce, escrow_address, trade_value]
)
success, response = kusama.publish(
    'fee_transfer',
    [seller_address, fee_signature, nonce + 1, fee_value]
)
```

### Happy case: regular release
```python
# Arbitrater makes storage as_multi to buyer
transaction = kusama.as_multi_storage(
    buyer_address, # To address
    seller_address, # Other signatory
    trade_value,
    max_weight = 648378000,
)

success, response = kusama.broadcast(
    'as_multi', transaction
)
timepoint = response['timepoint']

# Seller makes as_multi to release
as_multi_payload, nonce = kusama.as_multi_payload(
    seller_address, # from
    buyer_address, # to
    trade_value,
    [buyer_address, kusama.arbitrator_address],
    timepoint, # timepoint from storage
    False, # don't store
    648378000, # max weight
)
as_multi_signature = sign_payload(seller_keypair, as_multi_payload)
success, response = kusama.publish(
    'as_multi',
    [
        seller_address, # from
        as_multi_signature, # sig
        nonce, # seller nonce
        buyer_address, # to
        trade_value,
        timepoint, # timepoint
        [buyer_address, kusama.arbitrator_address], # other sigs
        648378000, # max weight
    ]
)
```

### Neutral case: cancellation
```python
# Arbitrater makes storage as_multi back to seller
transaction = kusama.as_multi_storage(
    seller_address, # To address
    buyer_address, # Other signatory
    trade_value
)

success, response = kusama.broadcast(
    'as_multi', transaction
)
timepoint = response['timepoint']

# Return the fee
transaction = kusama.fee_return_transaction(
    seller_address,
    trade_value,
    fee_value,
)
success, response = kusama.broadcast(
    'transfer', transaction
)

# Seller as_multi to return funds
as_multi_payload, nonce = kusama.as_multi_payload(
    seller_address, # from
    seller_address, # to
    trade_value,
    [buyer_address, kusama.arbitrator_address],
    timepoint, # timepoint from storage
    False, # don't store
    190949000, # max weight
)
as_multi_signature = sign_payload(seller_keypair, as_multi_payload)
success, response = kusama.publish(
    'as_multi',
    [
        seller_address, # from
        as_multi_signature, # sig
        nonce, # seller nonce
        seller_address, # to
        trade_value,
        timepoint, # timepoint
        [buyer_address, kusama.arbitrator_address], # other sigs
        190949000, # max weight
    ]
)
```

### Sad case: dispute (buyer wins)
```python
# Arbitrater makes storage as_multi to buyer
transaction = kusama.as_multi_storage(
    buyer_address, # To address
    seller_address, # Other signatory
    trade_value
)

success, response = kusama.broadcast(
    'as_multi', transaction
)
timepoint = response['timepoint']

# Arbitrator makes welfare payment to buyer
transaction = kusama.welfare_transaction(
    buyer_address,
)
success, response = kusama.broadcast(
    'transfer', transaction
)

# Buyer as_multi to receive funds
as_multi_payload, nonce = kusama.as_multi_payload(
    buyer_address, # from
    buyer_address, # to
    trade_value,
    [seller_address, kusama.arbitrator_address],
    timepoint, # timepoint from storage
    False, # don't store
    190949000, # max weight
)
as_multi_signature = sign_payload(buyer_keypair, as_multi_payload)
success, response = kusama.publish(
    'as_multi',
    [
        buyer_address, # from
        as_multi_signature, # sig
        nonce, # seller nonce
        buyer_address, # to
        trade_value,
        timepoint, # timepoint
        [seller_address, kusama.arbitrator_address], # other sigs
        190949000, # max weight
    ]
)
```

### Sad case: dispute (seller wins)
In this situation the flow is exactly the same as the cancellation flow
```python
# Arbitrater makes storage as_multi back to seller
transaction = kusama.as_multi_storage(
    seller_address, # To address
    buyer_address, # Other signatory
    trade_value
)

success, response = kusama.broadcast(
    'as_multi', transaction
)
timepoint = response['timepoint']

# Return the fee
transaction = kusama.fee_return_transaction(
    seller_address,
    trade_value,
    fee_value,
)
success, response = kusama.broadcast(
    'transfer', transaction
)

# Seller as_multi to return funds
as_multi_payload, nonce = kusama.as_multi_payload(
    seller_address, # from
    seller_address, # to
    trade_value,
    [buyer_address, kusama.arbitrator_address],
    timepoint, # timepoint from storage
    False, # don't store
    190949000, # max weight
)
as_multi_signature = sign_payload(seller_keypair, as_multi_payload)
success, response = kusama.publish(
    'as_multi',
    [
        seller_address, # from
        as_multi_signature, # sig
        nonce, # seller nonce
        seller_address, # to
        trade_value,
        timepoint, # timepoint
        [buyer_address, kusama.arbitrator_address], # other sigs
        190949000, # max weight
    ]
)
```

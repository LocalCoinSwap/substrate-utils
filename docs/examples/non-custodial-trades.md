## Non-custodial trades using the utility module
First, setup the module and connect to the blockchain using the instructions in the basic-usage section.

You can now use the library to go through each step of the trading process.

Please be aware of the distinction between user transactions and arbitrator transactions. User transactions need to be broadcast using the `publish` method, as there is construction required. Arbitrator transactions can be immediately broadcast using `broadcast` since they are already constructed.

The following code snippet instantiates everything needed to follow these examples. You will need to provide you own environment variables in a local `.env` file:
```python
import os
from dotenv import load_dotenv
from substrateutils import Polkadot as Provider
load_dotenv()

chain = Provider()
arbitrator_key = os.getenv("ARBITRATOR_SEED")
chain.setup_arbitrator(arbitrator_key)
chain.connect()
```

### Generate an escrow address
```python
buyer_address = os.getenv("BUYER_ADDRESS")
seller_address = os.getenv("SELLER_ADDRESS")
escrow_address = chain.get_escrow_address(buyer_address, seller_address)
```

### Generate the signature payloads to fund the escrow and send the fee
```python
# Value of the trade in Plancks
trade_value = 10000000000
# Fee being paid in Plancks (trade_value is not inclusive of fee)
fee_value = 100000000
escrow_payload, fee_payload, nonce = chain.escrow_payloads(
    seller_address, escrow_address, trade_value, fee_value)
```

### Sign the payloads
```python
import sr25519
from substrateutils.helper import sign_payload
seller_key = os.getenv("SELLER_SEED")
keypair = sr25519.pair_from_seed(bytes.fromhex(seller_key))

escrow_signature = sign_payload(keypair, escrow_payload)
fee_signature = sign_payload(keypair, fee_payload)
```

### Construct and broadcast the transactions
```python
success, response = chain.publish(
    'transfer',
    [seller_address,
    escrow_signature,
    nonce,
    escrow_address,
    trade_value]
)
assert success
success, response = chain.publish(
    'fee_transfer',
    [seller_address,
    fee_signature,
    nonce + 1,
    fee_value]
)
assert success
```

### Happy case: regular release
```python
# Arbitrater makes storage as_multi to buyer
transaction = chain.as_multi_storage(
    buyer_address, # To address
    seller_address, # Other signatory
    trade_value,
)

success, response = chain.broadcast(
    'as_multi', transaction
)
timepoint = response['timepoint']

# Seller makes as_multi to release
as_multi_payload, nonce = chain.as_multi_payload(
    seller_address, # from
    buyer_address, # to
    trade_value,
    [buyer_address, chain.arbitrator_address],
    timepoint, # timepoint from storage
    False, # don't store
)
as_multi_signature = sign_payload(seller_keypair, as_multi_payload)
success, response = chain.publish(
    'as_multi',
    [
        seller_address, # from
        as_multi_signature, # sig
        nonce, # seller nonce
        buyer_address, # to
        trade_value,
        timepoint, # timepoint
        [buyer_address, chain.arbitrator_address], # other sigs
    ]
)
```

### Neutral case: trade cancellation, return funds to seller
```python
# Arbitrater makes storage as_multi back to seller
transaction = chain.as_multi_storage(
    seller_address, # To address
    buyer_address, # Other signatory
    trade_value
)

success, response = chain.broadcast(
    'as_multi', transaction
)
timepoint = response['timepoint']

# Return the fee
transaction = chain.fee_return_transaction(
    seller_address,
    trade_value,
    fee_value,
)
success, response = chain.broadcast(
    'transfer', transaction
)

# Seller as_multi to return funds
as_multi_payload, nonce = chain.as_multi_payload(
    seller_address, # from
    seller_address, # to
    trade_value,
    [buyer_address, chain.arbitrator_address],
    timepoint, # timepoint from storage
    False, # don't store
)
as_multi_signature = sign_payload(seller_keypair, as_multi_payload)
success, response = chain.publish(
    'as_multi',
    [
        seller_address, # from
        as_multi_signature, # sig
        nonce, # seller nonce
        seller_address, # to
        trade_value,
        timepoint, # timepoint
        [buyer_address, chain.arbitrator_address], # other sigs
    ]
)
```

### Sad case: dispute (buyer wins)
```python
# Arbitrater makes storage as_multi to buyer
transaction = chain.as_multi_storage(
    buyer_address, # To address
    seller_address, # Other signatory
    trade_value
)

success, response = chain.broadcast(
    'as_multi', transaction
)
timepoint = response['timepoint']

# Arbitrator makes welfare payment to buyer
transaction = chain.welfare_transaction(
    buyer_address,
)
success, response = chain.broadcast(
    'transfer', transaction
)

# Buyer as_multi to receive funds
as_multi_payload, nonce = chain.as_multi_payload(
    buyer_address, # from
    buyer_address, # to
    trade_value,
    [seller_address, chain.arbitrator_address],
    timepoint, # timepoint from storage
    False, # don't store
)
as_multi_signature = sign_payload(buyer_keypair, as_multi_payload)
success, response = chain.publish(
    'as_multi',
    [
        buyer_address, # from
        as_multi_signature, # sig
        nonce, # seller nonce
        buyer_address, # to
        trade_value,
        timepoint, # timepoint
        [seller_address, chain.arbitrator_address], # other sigs
    ]
)
```

### Sad case: dispute (seller wins)
In this situation the flow is exactly the same as the cancellation flow
```python
# Arbitrater makes storage as_multi back to seller
transaction = chain.as_multi_storage(
    seller_address, # To address
    buyer_address, # Other signatory
    trade_value
)

success, response = chain.broadcast(
    'as_multi', transaction
)
timepoint = response['timepoint']

# Return the fee
transaction = chain.fee_return_transaction(
    seller_address,
    trade_value,
    fee_value,
)
success, response = chain.broadcast(
    'transfer', transaction
)

# Seller as_multi to return funds
as_multi_payload, nonce = chain.as_multi_payload(
    seller_address, # from
    seller_address, # to
    trade_value,
    [buyer_address, chain.arbitrator_address],
    timepoint, # timepoint from storage
    False, # don't store
)
as_multi_signature = sign_payload(seller_keypair, as_multi_payload)
success, response = chain.publish(
    'as_multi',
    [
        seller_address, # from
        as_multi_signature, # sig
        nonce, # seller nonce
        seller_address, # to
        trade_value,
        timepoint, # timepoint
        [buyer_address, chain.arbitrator_address], # other sigs
    ]
)
```

### End-to-end trade flow in happy case
This is a purposely verbose, line by line execution for an entire trade. This is useful for manual testing.

```python
import os
import sr25519
from dotenv import load_dotenv
from substrateutils.helper import sign_payload
from substrateutils import Polkadot as Provider
load_dotenv()

chain = Provider()
arbitrator_key = os.getenv("ARBITRATOR_SEED")
chain.setup_arbitrator(arbitrator_key)
chain.connect()

buyer_address = os.getenv("BUYER_ADDRESS")
seller_address = os.getenv("SELLER_ADDRESS")
escrow_address = chain.get_escrow_address(buyer_address, seller_address)

# Value of the trade in Plancks
trade_value = 10000000000
# Fee being paid in Plancks (trade_value is not inclusive of fee)
fee_value = 100000000
escrow_payload, fee_payload, nonce = chain.escrow_payloads(
    seller_address, escrow_address, trade_value, fee_value)

seller_key = os.getenv("SELLER_SEED")
seller_keypair = sr25519.pair_from_seed(bytes.fromhex(seller_key))

escrow_signature = sign_payload(seller_keypair, escrow_payload)
fee_signature = sign_payload(seller_keypair, fee_payload)

success, response = chain.publish(
    'transfer',
    [seller_address, escrow_signature, nonce, escrow_address, trade_value]
)
success, response = chain.publish(
    'fee_transfer',
    [seller_address, fee_signature, nonce + 1, fee_value]
)

transaction = chain.as_multi_storage(
    buyer_address, # To address
    seller_address, # Other signatory
    trade_value,
)

success, response = chain.broadcast(
    'as_multi', transaction
)
timepoint = response['timepoint']

# Seller makes as_multi to release
as_multi_payload, nonce = chain.as_multi_payload(
    seller_address, # from
    buyer_address, # to
    trade_value,
    [buyer_address, chain.arbitrator_address],
    timepoint, # timepoint from storage
    False, # don't store
)
as_multi_signature = sign_payload(seller_keypair, as_multi_payload)
success, response = chain.publish(
    'as_multi',
    [
        seller_address, # from
        as_multi_signature, # sig
        nonce, # seller nonce
        buyer_address, # to
        trade_value,
        timepoint, # timepoint
        [buyer_address, chain.arbitrator_address], # other sigs
    ]
)
```

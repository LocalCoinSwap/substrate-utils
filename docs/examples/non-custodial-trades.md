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

### Release the escrow to buyer
```python
# Arbitrater makes storage as_multi to buyer
transaction = chain.as_multi_storage(
    buyer_address, # To address
    seller_address, # Other signatory
    trade_value,
    max_weight = 648378000,
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
    648378000, # max weight
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
        648378000, # max weight
    ]
)
```

### Trade cancellation, return funds to seller
```python
# Seller broadcasts approve_as_multi for escrow return
approve_as_multi_payload, nonce = chain.approve_as_multi_payload(
    seller_address,
    seller_address,
    trade_value,
    [buyer_address, chain.arbitrator_address]
    )
approve_as_multi_signature = sign_payload(keypair, approve_as_multi_payload)
success, response = chain.publish(
    'approve_as_multi',
    [
        seller_address,
        approve_as_multi_signature,
        nonce,
        seller_address,
        trade_value,
        [buyer_address, chain.arbitrator_address]
    ]
    )
assert success

# Get arbitrator cancellation transactions and broadcast them
revert, fee_revert = chain.cancellation(
    seller_address,
    trade_value,
    fee_value,
    [seller_address, buyer_address],
    response['timepoint']
    )

success, response = chain.broadcast('as_multi', revert)
assert success
success, response = chain.broadcast('transfer', fee_revert)
assert success
```

Note: in all dispute situations the arbitrator broadcasts first. For simplicity, we still broadcast as_multi if the seller wins, in order to reuse the business logic of cancellation.

### Buyer wins dispute
```python
# Get and broadcast the arbitrator transactions
victor = "buyer"
release_transaction, welfare_transaction = chain.resolve_dispute(
    victor,
    seller_address,
    trade_value,
    fee_value,
    [buyer_address, seller_address]
    )

success, escrow_responce = chain.broadcast(
    'as_multi', release_transaction)
assert success
success, response = chain.broadcast(
    'transfer', welfare_transaction)
assert success

# Construct and broadcast the final buyer as_multi, seller or buyer can do this
as_multi_payload, nonce = chain.approve_as_multi_payload(
    seller_address,
    seller_address,
    trade_value,
    [buyer_address, chain.arbitrator_address]
    )
as_multi_signature = sign_payload(keypair, as_multi_payload)
success, response = chain.publish(
    'as_multi',
    [
        seller_address,
        as_multi_signature,
        nonce,
        seller_address,
        trade_value,
        [buyer_address, chain.arbitrator_address],
        escrow_responce['timepoint']
    ]
    )
assert success
```

## End-to-end standard trade
The following example is designed to show the execution logic over an entire trade. This is purposely verbose to eliminate confusion.

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

chain = Kusama()
chain.setup_arbitrator(arbitrator_seed)
chain.connect()

seller_keypair = sr25519.pair_from_seed(hex_to_bytes(seller_seed))
buyer_keypair = sr25519.pair_from_seed(hex_to_bytes(buyer_seed))
buyer_address = ss58_encode(buyer_keypair[0], 2)
seller_address = ss58_encode(seller_keypair[0], 2)

escrow_address = chain.get_escrow_address(buyer_address, seller_address)

trade_value = 10000000000 # Plancks = 0.01 KSM
fee_value = 100000000 # Plancks = 0.0001 KSM

# GET PAYLOADS, SIGN, PUBLISH ESCROW AND FEE
escrow_payload, fee_payload, nonce = chain.escrow_payloads(
    seller_address, escrow_address, trade_value, fee_value)

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
```

### Happy case: regular release
```python
# Arbitrater makes storage as_multi to buyer
transaction = chain.as_multi_storage(
    buyer_address, # To address
    seller_address, # Other signatory
    trade_value,
    max_weight = 648378000,
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
    648378000, # max weight
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
        648378000, # max weight
    ]
)
```

### Neutral case: cancellation
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
    190949000, # max weight
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
        190949000, # max weight
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
    190949000, # max weight
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
        190949000, # max weight
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
    190949000, # max weight
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
        190949000, # max weight
    ]
)
```

### End-to-end process
```python
import os
from dotenv import load_dotenv
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

transaction = chain.as_multi_storage(
    seller_address, # To address
    buyer_address, # Other signatory
    trade_value,
    # max_weight = 2565254000,
    max_weight = 1000000000,
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
    648378000, # max weight
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
        648378000, # max weight
    ]
)
```

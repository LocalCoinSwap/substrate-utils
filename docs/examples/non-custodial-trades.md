## Non-custodial trades using the utility module
First, setup the module and connect to the Kusama blockchain using the instructions in the basic-usage section.

You can now use the library to go through each step of the trading process.

Please be aware of the distinction between user transactions and arbitrator transactions. User transactions need to be broadcast using the `publish` method, as there is construction required. Arbitrator transactions can be immediately broadcast using `broadcast` since they are already constructed.


### Generate an escrow address
```python
buyer_address = "CofvaLbP3m8PLeNRQmLVPWmTT7jGgAXTwyT69k2wkfPxJ9V"
seller_address = "D2bHQwFcQj11SvtkjULEdKhK4WAeP6MThXgosMHjW9DrmbE"
escrow_address = kusama.get_escrow_address(buyer_address, seller_address)
```

### Generate the signature payloads to fund the escrow and send the fee
```python
# Value of the trade in Plancks
trade_value = 10000000000
# Fee being paid in Plancks (trade_value is not inclusive of fee)
fee_value = 100000000
escrow_payload, fee_payload, nonce = kusama.escrow_payloads(
    seller_address, escrow_address, trade_value, fee_value)
```

### Sign the payloads
```python
import sr25519
from helper import sign_payload
seller_key = '427a2c7cdff26fc2ab1dfda2ba991624cad12f8adc8b0851540db6efec2c7431'
keypair = sr25519.pair_from_seed(bytes.fromhex(seller_key))

escrow_signature = sign_payload(keypair, escrow_payload)
fee_signature = sign_payload(keypair, fee_payload)
```

### Construct and broadcast the transactions
```python
escrow_tx_hash, escrow_timepoint, success = kusama.publish(
    'transfer',
    [seller_address,
    escrow_signature,
    nonce,
    escrow_address,
    trade_value]
    )
assert success
fee_tx_hash, fee_timepoint, success = kusama.publish(
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
# Seller broadcasts approve_as_multi for escrow
approve_as_multi_payload, nonce = kusama.approve_as_multi_payload(
    seller_address,
    buyer_address,
    trade_value,
    [buyer_address, kusama.arbitrator_address]
    )

# Sign payload
approve_as_multi_signature = sign_payload(keypair, approve_as_multi_payload)

# Construct and broadcast seller approve_as_multi
tx_hash, timepoint, success = kusama.publish(
    'approve_as_multi', [
        seller_address,
        approve_as_multi_signature,
        nonce,
        buyer_address,
        trade_value,
        [buyer_address, kusama.arbitrator_address]
        ]
        )
assert success

# Get arbitrator release escrow transaction and broadcast it
as_multi = kusama.release_escrow(
    buyer_address,
    trade_value,
    timepoint,
    [seller_address, buyer_address]
    )
tx_hash, timepoint, success = kusama.broadcast('as_multi', as_multi)
assert success
```

### Trade cancellation, return funds to seller
```python
# Seller broadcasts approve_as_multi for escrow return
approve_as_multi_payload, nonce = kusama.approve_as_multi_payload(
    seller_address,
    seller_address,
    trade_value,
    [buyer_address, kusama.arbitrator_address]
    )
approve_as_multi_signature = sign_payload(keypair, approve_as_multi_payload)
tx_hash, timepoint, success = kusama.publish(
    'approve_as_multi', [
        seller_address,
        approve_as_multi_signature,
        nonce,
        seller_address,
        trade_value,
        [buyer_address, kusama.arbitrator_address]
        ]
        )
assert success

# Get arbitrator cancellation transactions and broadcast them
revert, fee_revert = kusama.cancellation(
    seller_address,
    trade_value,
    fee_value,
    [seller_address, buyer_address],
    timepoint
    )

tx_hash, timepoint, success = kusama.broadcast('as_multi', revert)
assert success
tx_hash, timepoint, success = kusama.broadcast('transfer', fee_revert)
assert success
```

Note: in all dispute situations the arbitrator broadcasts first. For simplicity, we still broadcast as_multi if the seller wins, in order to reuse the business logic of cancellation.

### Buyer wins dispute
```python
# Get and broadcast the arbitrator transactions
victor = "buyer"
release_transaction, welfare_transaction = kusama.resolve_dispute(
    victor,
    seller_address,
    trade_value,
    fee_value,
    [buyer_address, seller_address]
    )

tx_hash, escrow_timepoint, success = kusama.broadcast(
    'as_multi', release_transaction)
assert success
tx_hash, timepoint, success = kusama.broadcast(
    'transfer', welfare_transaction)
assert success

# Construct and broadcast the final buyer as_multi, seller or buyer can do this
as_multi_payload, nonce = kusama.approve_as_multi_payload(
    seller_address,
    seller_address,
    trade_value,
    [buyer_address, kusama.arbitrator_address]
    )
as_multi_signature = sign_payload(keypair, as_multi_payload)
tx_hash, timepoint, success = kusama.publish(
    'as_multi', [
        seller_address,
        as_multi_signature,
        nonce,
        seller_address,
        trade_value,
        [buyer_address, kusama.arbitrator_address],
        escrow_timepoint]
    )
assert success
```

## End-to-end standard trade
The following example is designed to show the execution logic over an entire trade. This is purposely verbose to eliminate confusion.
```
import sr25519

from ksmutils import Kusama
from ksmutils.helper import sign_payload
kusama = Kusama()

arbitrator_key = 'b5643fe4084cae15ffbbc5c1cbe734bec5da9c351f4aa4d44f2897efeb8375c8'
kusama.setup_arbitrator(arbitrator_key)
kusama.connect()

buyer_address = "CofvaLbP3m8PLeNRQmLVPWmTT7jGgAXTwyT69k2wkfPxJ9V"
seller_address = "D2bHQwFcQj11SvtkjULEdKhK4WAeP6MThXgosMHjW9DrmbE"
escrow_address = kusama.get_escrow_address(buyer_address, seller_address)

# Value of the trade in Plancks
trade_value = 10000000000
# Fee being paid in Plancks (trade_value is not inclusive of fee)
fee_value = 100000000
escrow_payload, fee_payload, nonce = kusama.escrow_payloads(
    seller_address, escrow_address, trade_value, fee_value)

seller_key = '427a2c7cdff26fc2ab1dfda2ba991624cad12f8adc8b0851540db6efec2c7431'
keypair = sr25519.pair_from_seed(bytes.fromhex(seller_key))

escrow_signature = sign_payload(keypair, escrow_payload)
fee_signature = sign_payload(keypair, fee_payload)

escrow_tx_hash, escrow_timepoint, success = kusama.publish(
    'transfer',
    [seller_address, escrow_signature, nonce, escrow_address, trade_value]
    )
assert success
fee_tx_hash, fee_timepoint, success = kusama.publish(
    'fee_transfer',
    [seller_address, fee_signature, nonce + 1, fee_value]
    )
assert success

# Seller broadcasts approve_as_multi for escrow
approve_as_multi_payload, nonce = kusama.approve_as_multi_payload(
    seller_address,
    buyer_address,
    trade_value,
    [buyer_address, kusama.arbitrator_address]
    )

# Sign payload
approve_as_multi_signature = sign_payload(
    keypair, approve_as_multi_payload)

# Construct and broadcast seller approve_as_multi
tx_hash, timepoint, success = kusama.publish(
    'approve_as_multi', [
        seller_address,
        approve_as_multi_signature,
        nonce,
        buyer_address,
        trade_value,
        [buyer_address, kusama.arbitrator_address]]
        )
assert success

# Get arbitrator release escrow transaction and broadcast it
as_multi = kusama.release_escrow(
    buyer_address,
    trade_value,
    timepoint,
    [seller_address, buyer_address]
    )
tx_hash, timepoint, success = kusama.broadcast('as_multi', as_multi)
assert success
```

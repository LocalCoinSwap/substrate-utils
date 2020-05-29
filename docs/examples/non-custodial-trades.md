## Non-custodial trades using the utility module
First, setup the module and connect to the Kusama blockchain using the instructions in the basic-usage section.

You can now use the library to go through each step of the trading process.

### Generate an escrow address
```python
buyer_address = "CofvaLbP3m8PLeNRQmLVPWmTT7jGgAXTwyT69k2wkfPxJ9V"
seller_address = "D2bHQwFcQj11SvtkjULEdKhK4WAeP6MThXgosMHjW9DrmbE"
escrow_address = kusama.get_escrow_address(buyer_address, seller_address)
```

### Generate the signature payloads to fund the escrow and send the fee
```python
trade_value = 10000000000 # Value of the trade in Plancks
fee_value = 100000000 # Fee being paid in Plancks (trade_value is not inclusive of fee)
escrow_payload, fee_payload, nonce = kusama.escrow_payloads(
    seller_address, escrow_address, trade_value, fee_value)
```

### Sign the payloads
```
import sr25519
from helper import sign_payload
seller_key = '427a2c7cdff26fc2ab1dfda2ba991624cad12f8adc8b0851540db6efec2c7431'
keypair = sr25519.pair_from_seed(bytes.fromhex(seller_key))

escrow_signature = sign_payload(keypair, escrow_payload)
fee_signature = sign_payload(keypair, fee_payload)
```

### Construct and broadcast the transactions
```
escrow_tx = kusama.publish(
    'transfer', [seller_address, escrow_signature, nonce, escrow_address, trade_value])
fee_tx = kusama.publish(
    'fee_transfer', [seller_address, fee_signature, nonce + 1, fee_value])
```

### Release the escrow to buyer
```
# Seller broadcasts approve_as_multi for escrow
approve_as_multi_escrow_payload, nonce = kusama.approve_as_multi_payload(
    seller_address, buyer_address, trade_value, [buyer_address, kusama.arbitrator_address]
    )

# Sign payload
approve_as_multi_escrow_signature = sign_payload(keypair, approve_as_multi_escrow_payload)

# Construct and broadcast
escrow_approve_as_multi_tx = kusama.publish('approve_as_multi', [seller_address,approve_as_multi_escrow_signature, nonce, buyer_address, trade_value, [buyer_address, kusama.arbitrator_address]])

# Arbitrator_address broadcasts as_multi for fee

as_multi_escrow_tx = kusama.release_escrow(buyer_address, trade_value, escrow_as_multi_tx[1],[seller_address, buyer_address])

# Broadcast

broadcasted_as_multi_escrow_tx = kusama.broadcast('as_multi', as_multi_escrow_tx)
```


### Recover the trading fee
```
# Seller broadcasts approve_as_multi for fee
approve_as_multi_fee_payload, nonce = kusama.approve_as_multi_payload(
    seller_address, buyer_address, fee_value, [buyer_address, kusama.arbitrator_address]
    )

# Sign payload
approve_as_multi_fee_signature = sign_payload(keypair, approve_as_multi_fee_payload)

# Construct and broadcast
fee_as_multi_tx = kusama.publish('approve_as_multi', [seller_address, approve_as_multi_fee_signature, nonce, buyer_address, fee_value, [buyer_address, kusama.arbitrator_address]])

# Arbitrator_address broadcasts as_multi for fee

as_multi_fee_tx = kusama.release_escrow(buyer_address, fee_value, fee_as_multi_tx[1], [seller_address, buyer_address])

# Broadcast showing lower level functions
node_response = kusama.network.node_rpc_call(
    "author_submitAndWatchExtrinsic", [as_multi_fee_tx]
)
tx_hash = kusama.get_extrinsic_hash(as_multi_fee_tx)
block_hash = kusama.get_block_hash(node_response)
timepoint = kusama.get_extrinsic_timepoint(node_response, as_multi_fee_tx)
events = kusama.get_extrinsic_events(block_hash, timepoint[1])
success = kusama.is_transaction_success("as_multi", events)

```

### Trade cancellation, return funds to seller
```
# Seller broadcasts approve_as_multi for escrow return
approve_as_multi_escrow_payload, nonce = kusama.approve_as_multi_payload(
    seller_address, seller_address, trade_value, [buyer_address, kusama.arbitrator_address]
    )

# Sign payload
approve_as_multi_escrow_signature = sign_payload(keypair, approve_as_multi_escrow_payload)

# Construct and broadcast
escrow_approve_as_multi_tx = kusama.publish('approve_as_multi', [seller_address, approve_as_multi_escrow_signature, nonce, seller_address, trade_value, [buyer_address, kusama.arbitrator_address]])

# Arbitrator_address broadcasts as_multi for fee

as_multi_escrow_tx = kusama.cancellation(seller_address, trade_value, fee_value, [seller_address, buyer_address])

# Broadcast

broadcasted_as_multi_escrow_tx = kusama.broadcast('as_multi', as_multi_escrow_tx)
```

### Buyer wins dispute
```

```

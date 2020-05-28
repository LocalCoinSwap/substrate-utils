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

```

### Trade cancellation, return funds to seller
```

```

### Buyer wins dispute
```

```

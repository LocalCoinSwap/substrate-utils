The following are end-to-end examples designed to show the execution logic over an entire trade. There are purposely verbose to eliminate confusion.

## End-to-end standard trade
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

trade_value = 10000000000 # Value of the trade in Plancks
fee_value = 100000000 # Fee being paid in Plancks (trade_value is not inclusive of fee)
escrow_payload, fee_payload, nonce = kusama.escrow_payloads(
    seller_address, escrow_address, trade_value, fee_value)

seller_key = '427a2c7cdff26fc2ab1dfda2ba991624cad12f8adc8b0851540db6efec2c7431'
keypair = sr25519.pair_from_seed(bytes.fromhex(seller_key))

escrow_signature = sign_payload(keypair, escrow_payload)
fee_signature = sign_payload(keypair, fee_payload)

escrow_tx_hash, escrow_timepoint, success = kusama.publish(
    'transfer', [seller_address, escrow_signature, nonce, escrow_address, trade_value])
assert success
fee_tx_hash, fee_timepoint, success = kusama.publish(
    'fee_transfer', [seller_address, fee_signature, nonce + 1, fee_value])
assert success
```

## End-to-end cancellation
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

trade_value = 10000000000 # Value of the trade in Plancks
fee_value = 100000000 # Fee being paid in Plancks (trade_value is not inclusive of fee)
escrow_payload, fee_payload, nonce = kusama.escrow_payloads(
    seller_address, escrow_address, trade_value, fee_value)

seller_key = '427a2c7cdff26fc2ab1dfda2ba991624cad12f8adc8b0851540db6efec2c7431'
keypair = sr25519.pair_from_seed(bytes.fromhex(seller_key))

escrow_signature = sign_payload(keypair, escrow_payload)
fee_signature = sign_payload(keypair, fee_payload)

escrow_tx = kusama.publish(
    'transfer', [seller_address, escrow_signature, nonce, escrow_address, trade_value])
fee_tx = kusama.publish(
    'fee_transfer', [seller_address, fee_signature, nonce + 1, fee_value])
```

## End-to-end seller winning dispute
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

trade_value = 10000000000 # Value of the trade in Plancks
fee_value = 100000000 # Fee being paid in Plancks (trade_value is not inclusive of fee)
escrow_payload, fee_payload, nonce = kusama.escrow_payloads(
    seller_address, escrow_address, trade_value, fee_value)

seller_key = '427a2c7cdff26fc2ab1dfda2ba991624cad12f8adc8b0851540db6efec2c7431'
keypair = sr25519.pair_from_seed(bytes.fromhex(seller_key))

escrow_signature = sign_payload(keypair, escrow_payload)
fee_signature = sign_payload(keypair, fee_payload)

escrow_tx = kusama.publish(
    'transfer', [seller_address, escrow_signature, nonce, escrow_address, trade_value])
fee_tx = kusama.publish(
    'fee_transfer', [seller_address, fee_signature, nonce + 1, fee_value])
```

## End-to-end buyer winning dispute
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

trade_value = 10000000000 # Value of the trade in Plancks
fee_value = 100000000 # Fee being paid in Plancks (trade_value is not inclusive of fee)
escrow_payload, fee_payload, nonce = kusama.escrow_payloads(
    seller_address, escrow_address, trade_value, fee_value)

seller_key = '427a2c7cdff26fc2ab1dfda2ba991624cad12f8adc8b0851540db6efec2c7431'
keypair = sr25519.pair_from_seed(bytes.fromhex(seller_key))

escrow_signature = sign_payload(keypair, escrow_payload)
fee_signature = sign_payload(keypair, fee_payload)

escrow_tx = kusama.publish(
    'transfer', [seller_address, escrow_signature, nonce, escrow_address, trade_value])
fee_tx = kusama.publish(
    'fee_transfer', [seller_address, fee_signature, nonce + 1, fee_value])
```

## Trading using only as-multi flow

```python
import sr25519

from ksmutils import Kusama
from ksmutils.helper import sign_payload
from ksmutils.helper import hex_to_bytes
from scalecodec.utils.ss58 import ss58_encode

# VARIABLES AND SETUP
arbitrator_key = 'b5643fe4084cae15ffbbc5c1cbe734bec5da9c351f4aa4d44f2897efeb8375c8'
seller_key = '427a2c7cdff26fc2ab1dfda2ba991624cad12f8adc8b0851540db6efec2c7431'

kusama = Kusama()
kusama.setup_arbitrator(arbitrator_key)
kusama.connect()

seller_keypair = sr25519.pair_from_seed(hex_to_bytes(seller_key))
buyer_address = "CofvaLbP3m8PLeNRQmLVPWmTT7jGgAXTwyT69k2wkfPxJ9V"
seller_address = ss58_encode(seller_keypair[0], 2)

escrow_address = kusama.get_escrow_address(buyer_address, seller_address)

trade_value = 10000000000 # Plancks
fee_value = 100000000 # Plancks

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

# ARBITRATER MAKES STORAGE AS_MULTI
transaction = kusama.as_multi_storage(
    buyer_address,
    seller_address,
    trade_value
)
success, response = kusama.broadcast(
    'as_multi', transaction
)
timepoint = response['timepoint']

# SELLERS MAKES REGULAR AS_MULTI TO COMPLETE
as_multi_payload, nonce = kusama.as_multi_payload(
    seller_address,
    buyer_address,
    trade_value,
    [buyer_address, kusama.arbitrator_address],
    store_call=True,
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
        2, 0, 0, # Need other params in this format
        True,
    ]
)
```

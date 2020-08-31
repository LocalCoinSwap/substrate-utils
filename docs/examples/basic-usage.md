## Basic setup of the module

### Instantiating without configuration
```
from ksmutils import Kusama
kusama = Kusama()
```

### Loading configuration after instantiation
```
from ksmutils import Kusama
kusama = Kusama()

arbitrator_key = 'b5643fe4084cae15ffbbc5c1cbe734bec5da9c351f4aa4d44f2897efeb8375c8'
kusama.setup_arbitrator(arbitrator_key)
```

### Instantiating with arbitrator and websocket configuration
```
from ksmutils import Kusama
kusama = Kusama()

arbitrator_key = 'b5643fe4084cae15ffbbc5c1cbe734bec5da9c351f4aa4d44f2897efeb8375c8'
node_provider = 'wss://kusama-rpc.polkadot.io/'
kusama = Kusama(
    arbitrator_key=arbitrator_key,
    node_url=node_provider
)
```

### Connecting to the Kusama blockchain
```python

kusama.connect()
kusama.runtime_info()
```

### Preparing and sending a generic transfer

```python
import sr25519
from ksmutils import Kusama
from ksmutils.helper import hex_to_bytes
from scalecodec.utils.ss58 import ss58_encode

kusama = Kusama()
kusama.connect()

sender_seed_hex = "<SEED OF SENDER>"
to_address = "JELVFBo1GL82vvEtDqVZMd2NDTFgQC3oi8W2fV3Xtm6CLXX"
value = 10000000000 # 0.01 KSM in Planks

# Prepare key
keypair = sr25519.pair_from_seed(hex_to_bytes(sender_seed_hex))
sender_address = ss58_encode(keypair[0], 2)

# Get transaction payload to sign and nonce
payload = kusama.transfer_payload(sender_address, to_address, value)
nonce = kusama.get_nonce(sender_address)

# Sign payload
signed_payload = sr25519.sign(keypair, hex_to_bytes(payload)).hex()

# Broadcast payload
success, response = kusama.publish(
    'transfer',
    [sender_address,
    signed_payload,
    nonce,
    to_address,
    value]
)
assert success
print(response)
```

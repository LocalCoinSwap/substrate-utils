## Basic setup of the module

### Instantiating without configuration
```python
from substrateutils import Kusama, Polkadot
kusama = Kusama()
polkadot = Polkadot()
```

### Loading configuration after instantiation
```python
from substrateutils import Kusama, Polkadot
kusama, polkadot = Kusama(), Polkadot()

arbitrator_key = 'b5643fe4084cae15ffbbc5c1cbe734bec5da9c351f4aa4d44f2897efeb8375c8'
kusama.setup_arbitrator(arbitrator_key)
polkadot.setup_arbitrator(arbitrator_key)
```

### Instantiating with arbitrator and websocket configuration
```python
from substrateutils import Kusama, Polkadot
kusama, polkadot = Kusama(), Polkadot()

arbitrator_key = 'b5643fe4084cae15ffbbc5c1cbe734bec5da9c351f4aa4d44f2897efeb8375c8'
ksm_provider = 'wss://kusama-rpc.polkadot.io/'
dot_provider = 'wss://rpc.polkadot.io/'
kusama = Kusama(
    arbitrator_key=arbitrator_key,
    node_url=ksm_provider
)
polkadot = Kusama(
    arbitrator_key=arbitrator_key,
    node_url=dot_provider
)
```

### Connecting to the blockchain and getting runtime
```python

chain.connect()
chain.runtime_info()
```

### Preparing and sending a generic transfer

```python
import sr25519
from substrateutils import Polkadot as Provider
from substrateutils.helper import hex_to_bytes
from scalecodec.utils.ss58 import ss58_encode

chain = Provider()
chain.connect()

sender_seed_hex = "<SEED OF SENDER>"
to_address = "<TO ADDRESS>"
value = 10000000000 # 1 DOT

# Prepare key
keypair = sr25519.pair_from_seed(hex_to_bytes(sender_seed_hex))
sender_address = ss58_encode(keypair[0], ss58_format=0)

# Get transaction payload to sign and nonce
payload = chain.transfer_payload(sender_address, to_address, value)
nonce = chain.get_nonce(sender_address)

# Sign payload
signed_payload = sr25519.sign(keypair, hex_to_bytes(payload)).hex()

# Broadcast payload
success, response = chain.publish(
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

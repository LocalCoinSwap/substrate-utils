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
    address=node_provider
)
```

## Connecting to the Kusama node
```
kusama.connect()
```

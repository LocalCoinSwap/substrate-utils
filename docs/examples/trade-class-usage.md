## Using the trade class
The trade class is intended to allow developers to examine the mechanics of a P2P trade in the most straightforward manner possible.

You can run through the process of a trade, and then examine the individual functions to see what happens.

The process of a non-custodial trade is explained in our Substrate reference document:  
https://github.com/LocalCoinSwap/substrate-multisig-reference/

The trade class is not appropriate for production usage, because it requires all trading parties to expose their private keys to the class. Instead, you can use the mechanics of the process for your own implementations.

If you need an API service which abstracts the useful mechanics of the process into REST-API calls, you can use:
https://github.com/LocalCoinSwap/substrate-api

### Instantiation
You'll first need some private keys, mnemonics or address hexs. The default cryptocurrency in the trade class is Polkadot, but you can pass it any kind of crypto core.

```python
import os
from dotenv import load_dotenv
load_dotenv()

from substrateutils import TradeManager
from substrateutils import User


Buyer = User(hex=os.getenv("BUYER_SEED"))
Seller = User(hex=os.getenv("SELLER_SEED"))
Arbitrator = User(hex=os.getenv("ARBITRATOR_SEED"))

Trade = TradeManager(
    Buyer,
    Seller,
    Arbitrator,
    25000000000, # Trade value
    fee_value = 200000000,
)
```

### Demonstrating the trading flow
The trading flow is deliberately simple so you can examine the underlying code yourself. In fact you only need a single command for each step.

Funding escrow:
```python
Trade.fund_escrow()
```

Releasing escrow:
```python
Trade.release()
```

Cancel a trade:
```python
Trade.cancel()
```

Disputing in favour of a buyer:
```python
Trade.dispute(winner="BUYER")
```

Disputing in favour of a seller:
```python
Trade.dispute(winner="SELLER")
```

Yep, it's that easy :)

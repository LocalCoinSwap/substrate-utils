import asyncio
import binascii
import json

import websockets
from substrateinterface import SubstrateInterface
#import settings

class SubstrateUtils:
    def __init__(self,
                node_url,
                 **kwargs):
        self.substrate = SubstrateInterface(
        url=node_url, address_type=2, type_registry_preset="kusama",
        )

    def get_balance_for_address(self, address):
        """
        Params:
        -------
        address - str

        Returns:
        --------
        dict

        Example:
        {
            "free": 22000000000,
            "reserved": 0,
            "miscFrozen": 0,
            "feeFrozen": 0,
        }
        """
        block = self.substrate.get_chain_finalised_head()

        account_data = self.substrate.get_runtime_state(
            module="System", storage_function="Account", params=[address], block_hash=block,
        )

        if not account_data.get("result"):
            return {
                "free": 0,
                "reserved": 0,
                "miscFrozen": 0,
                "feeFrozen": 0,
            }
        return account_data.get("result", {}).get("data")
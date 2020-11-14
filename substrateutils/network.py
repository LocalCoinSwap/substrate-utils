import asyncio
import json
import logging

import websockets

logger = logging.getLogger(__name__)


class Network:
    """
    The Network class manages a connection to local/remote Substrate node
    """

    def __init__(self, *, node_url: str = "wss://kusama-rpc.polkadot.io/"):
        logger.info(f"Instantiating network connection to {node_url}")
        self.node_url = node_url

    def node_rpc_call(self, method, params, watch: bool = False):
        logger.info("node_rpc_call for {}".format(method))
        execution = (
            asyncio.run(self._node_rpc_call(method, params, loop_limit=0))
            if watch
            else asyncio.run(self._node_rpc_call(method, params, loop_limit=1))[0]
        )
        return execution

    async def _node_rpc_call(self, method, params, *, loop_limit: int = 0):
        """
        Generic method for node RPC calls. It's important to set loop_limit to 1 if
        you are not pushing transactions or you will get an infinite loop
        """
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1,
        }
        ws_results = {}

        async def ws_request(payload):
            async with websockets.connect(self.node_url) as websocket:
                await websocket.send(json.dumps(payload))
                event_number = 0
                loops = 0
                looping = True
                while looping:
                    result = json.loads(await websocket.recv())
                    # logger.info(f"Received from server {result}")
                    ws_results.update({event_number: result})

                    # Kill things immediately for simple requests
                    loops += 1
                    if loop_limit and loop_limit <= loops:
                        looping = False

                    # End transactions when they are finalised
                    looping = (
                        False
                        if (
                            (
                                "params" in result
                                and type(result["params"]["result"]) is dict
                                and "finalized" in result["params"]["result"]
                            )
                            or ("error" in result)
                        )
                        else looping
                    )

                    event_number += 1

        await ws_request(payload)
        return ws_results

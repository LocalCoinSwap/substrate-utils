import json
from logging import Logger

import websockets

_INSTANCE = None


class Network:
    """
    The Network class manages a connection to local/remote Kusama node
    """

    def __init__(
        self,
        *,
        logger: "Logger" = Logger,
        address: str = "wss://kusama-rpc.polkadot.io/",
    ):
        global _INSTANCE
        assert _INSTANCE is None, "Network is a singleton!"
        _INSTANCE = self

        self.logger = logger()
        self.logger.info(f"Instantiating network connection to {address}")
        self.address = address

    async def node_rpc_call(self, method, params, loop_limit=False, *, debug=False):
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
            async with websockets.connect(self.address) as websocket:
                await websocket.send(json.dumps(payload))
                event_number = 0
                loops = 0
                looping = True
                while looping:
                    result = json.loads(await websocket.recv())
                    print("Received from server", result)
                    if debug:
                        self.logger.debug("Received from server", result)
                    ws_results.update({event_number: result})

                    # Kill things immediately for simple requests
                    loops += 1
                    if loop_limit and loop_limit <= loops:
                        looping = False

                    # This is nasty but nested ifs are worse
                    if (
                        "params" in result
                        and type(result["params"]["result"]) is dict
                        and "finalized" in result["params"]["result"]
                    ):
                        looping = False

                    event_number += 1

        await ws_request(payload)
        return ws_results

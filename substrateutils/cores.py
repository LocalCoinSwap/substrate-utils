import logging
from abc import ABC
from abc import abstractmethod
from hashlib import blake2b

import sr25519
from scalecodec import ScaleBytes
from scalecodec.base import RuntimeConfiguration
from scalecodec.base import ScaleDecoder
from scalecodec.block import ExtrinsicsDecoder
from scalecodec.metadata import MetadataDecoder
from scalecodec.type_registry import load_type_registry_preset
from scalecodec.utils.ss58 import ss58_decode
from scalecodec.utils.ss58 import ss58_encode

from . import helper
from .network import Network

logger = logging.getLogger(__name__)


class NonceManager(ABC):
    """

    Abstract Class: Extending this class allows a user to build advanced
    nonce management in asyncronous environments where ordering is important
    """

    @abstractmethod
    def get_pending_extrinsics(self) -> list:
        raise NotImplementedError("Not implemented")

    @abstractmethod
    def get_nonce(self, address: str) -> int:
        raise NotImplementedError("Not implemented")

    def get_mempool_nonce(self, address: str) -> int:
        """
        Returns the nonce of any pending extrinsics for a given address
        """
        account_id = ss58_decode(address)

        pending_extrinsics = self.get_pending_extrinsics()
        nonce = -1

        for idx, extrinsic in enumerate(pending_extrinsics):
            if extrinsic.get("account_id") == account_id:
                nonce = max(extrinsic.get("nonce", nonce), nonce)
        return nonce

    def arbitrator_nonce(self) -> int:
        """
        Returns the nonce of any pending extrinsics for the arbitrator
        """
        if not self.arbitrator_address:
            raise Exception("Did you forget to setup artitrator address?")

        mempool_nonce = self.get_mempool_nonce(self.arbitrator_address)
        if mempool_nonce == -1:
            return self.get_nonce(self.arbitrator_address)
        return mempool_nonce


class SubstrateBase(NonceManager):
    def __init__(
        self, *, node_url: str = None, arbitrator_key: str = None,
    ):
        self.node_url = node_url
        if arbitrator_key:
            self.setup_arbitrator(arbitrator_key)

    def load_type_registry(self):
        RuntimeConfiguration().update_type_registry(
            load_type_registry_preset(self.chain)
        )

    def connect(self, *, node_url: str = "", network: "Network" = None):
        """
        Connect to a Substrate node and instantiate necessary constants for chain communication
        """
        node_url = self.node_url if not node_url else node_url
        if not network:
            network = Network(node_url=node_url)

        self.network = network
        self.runtime_info()

        RuntimeConfiguration().update_type_registry(
            load_type_registry_preset("default")
        )

        self.load_type_registry()

        self.metadata = self.get_metadata()
        self.runtime_info()
        self.genesis_hash = self.get_genesis_hash()

    def setup_arbitrator(self, arbitrator_key: str):
        """
        Set up constants required for arbitrator functionality
        """
        self.keypair = sr25519.pair_from_seed(bytes.fromhex(arbitrator_key))
        self.arbitrator_account_id = self.keypair[0].hex()
        self.arbitrator_address = ss58_encode(self.keypair[0], self.address_type)

    def runtime_info(self) -> int:
        """
        Check the current runtime and load the correct spec vesion and
        transaction version
        """
        result = self.network.node_rpc_call("state_getRuntimeVersion", [])
        self.spec_version = result["result"]["specVersion"]
        self.transaction_version = result["result"]["transactionVersion"]
        return result["result"]

    def get_metadata(self) -> "MetadataDecoder":
        """
        Returns decoded chain metadata
        """
        raw_metadata = self.network.node_rpc_call("state_getMetadata", [None])["result"]
        self.raw_metadata = raw_metadata
        metadata = MetadataDecoder(ScaleBytes(raw_metadata))
        metadata.decode()
        return metadata

    def dump_metadata(self, filename: str = "metadata.txt") -> None:
        """
        Dump the raw metadata to a file in root directory
        """
        with open(filename, "w") as f:
            f.write(self.raw_metadata)

    def get_genesis_hash(self) -> str:
        """
        Returns the chain's genesis block hash
        """
        return self.network.node_rpc_call("chain_getBlockHash", [0])["result"]

    def _get_address_info(self, address: str) -> dict:
        """
        Returns information associated with provided address
        """
        # Storage key:
        # xxHash128(System) + xxHash128(Account)
        storage_key = (
            "0x26aa394eea5630e07c48ae0c9558cef7b99d880ec681799c0cf30e8886371da9"
        )

        account_id = ss58_decode(address, self.address_type)
        hashed_address = f"{blake2b(bytes.fromhex(account_id), digest_size=16).digest().hex()}{account_id}"
        storage_hash = storage_key + hashed_address
        result = self.network.node_rpc_call("state_getStorageAt", [storage_hash, None])[
            "result"
        ]
        if not result:
            # TODO: Check if the format of this dict changes frequently
            return {
                "nonce": 0,
                "refcount": 0,
                "data": {"free": 0, "reserved": 0, "miscFrozen": 0, "feeFrozen": 0},
            }

        return_decoder = ScaleDecoder.get_decoder_class(
            "AccountInfo<Index, AccountData>",
            ScaleBytes(result),
            metadata=self.metadata,
        )
        return return_decoder.decode()

    def get_balance(self, address: str) -> int:
        """
        Returns the free balance associated with provided address
        """
        result = self._get_address_info(address)
        return result["data"]["free"]

    def get_nonce(self, address: str) -> int:
        """
        Returns the nonce associated with provided address
        """
        result = self._get_address_info(address)
        return result["nonce"]

    def get_block(self, block_hash: str) -> dict:
        """
        Returns the block information associated with provided block hash
        """
        response = self.network.node_rpc_call("chain_getBlock", [block_hash])["result"]

        response["block"]["header"]["number"] = int(
            response["block"]["header"]["number"], 16
        )

        for idx, data in enumerate(response["block"]["extrinsics"]):
            extrinsic_decoder = ExtrinsicsDecoder(
                data=ScaleBytes(data), metadata=self.metadata
            )
            extrinsic_decoder.decode()
            response["block"]["extrinsics"][idx] = extrinsic_decoder.value

        return response

    def get_events(self, block_hash: str) -> list:
        """
        Returns events broadcasted within the provided block
        """
        # Storage key:
        # xxHash128(System) + xxHash128(Events)
        storage_hash = (
            "0x26aa394eea5630e07c48ae0c9558cef780d41e5e16056765bc8461851072c9d7"
        )

        result = self.network.node_rpc_call(
            "state_getStorageAt", [storage_hash, block_hash]
        )["result"]

        return_decoder = ScaleDecoder.get_decoder_class(
            "Vec<EventRecord<Event, Hash>>", ScaleBytes(result), metadata=self.metadata,
        )
        return return_decoder.decode()

    def _get_extrinsic_index(self, block_extrinsics: list, extrinsic_hash: str) -> int:
        """
        Returns the index of a provided extrinsic
        """
        for idx, extrinsics in enumerate(block_extrinsics):
            ehash = extrinsics.get("extrinsic_hash")
            if ehash == extrinsic_hash:
                return idx
        return -1

    def get_extrinsic_hash(self, final_transaction: str) -> str:
        """
        Returns the extrinsic hash for a provided complete extrinsic
        """
        return (
            blake2b(bytes.fromhex(final_transaction[2:]), digest_size=32).digest().hex()
        )

    def get_extrinsic_timepoint(
        self, node_response: dict, final_transaction: str
    ) -> tuple:
        """
        Returns the timepoint of a provided extrinsic
        """
        if not node_response:
            raise Exception("node_response is empty")

        finalized_hash = self.get_block_hash(node_response)
        if not finalized_hash:
            raise Exception("Last item in the node_response is not finalized hash")

        extrinsic_hash = self.get_extrinsic_hash(final_transaction)

        block = self.get_block(finalized_hash)
        block_number = block.get("block").get("header").get("number")
        extrinsic_index = self._get_extrinsic_index(
            block.get("block").get("extrinsics"), extrinsic_hash
        )

        return (block_number, extrinsic_index)

    def get_extrinsic_events(self, block_hash: str, extrinsinc_index: int) -> list:
        """
        Returns events triggered by provided extrinsic
        """
        events = self.get_events(block_hash)
        extrinsic_events = []
        for event in events:
            if event.get("extrinsic_idx") == extrinsinc_index:
                extrinsic_events.append(event)
        return extrinsic_events

    def get_pending_extrinsics(self) -> list:
        """
        Returns decoded pending extrinsics
        """
        decoded_extrinsics = []
        extrinsics = self.network.node_rpc_call("author_pendingExtrinsics", [])[
            "result"
        ]

        for idx, extrinsic in enumerate(extrinsics):
            extrinsic_decoder = ExtrinsicsDecoder(
                data=ScaleBytes(extrinsic), metadata=self.metadata
            )
            decoded_extrinsics.append(extrinsic_decoder.decode())

        return decoded_extrinsics

    def get_escrow_address(
        self, buyer_address: str, seller_address: str, threshold: int = 2
    ) -> str:
        """
        Returns an escrow address for multisignature transactions
        """
        MultiAccountId = RuntimeConfiguration().get_decoder_class("MultiAccountId")

        multi_sig_account_id = MultiAccountId.create_from_account_list(
            [buyer_address, seller_address, self.arbitrator_address], 2
        )

        multi_sig_address = ss58_encode(
            multi_sig_account_id.value.replace("0x", ""), self.address_type
        )
        return multi_sig_address

    def transfer_payload(self, from_address: str, to_address: str, value: int) -> str:
        """
        Returns signature payloads for a regular transfer
        """
        nonce = self.get_nonce(from_address)
        return helper.transfer_signature_payload(
            self.metadata,
            to_address,
            value,
            nonce,
            self.genesis_hash,
            self.spec_version,
        )

    def approve_as_multi_payload(
        self, from_address: str, to_address: str, value: int, other_signatories: list
    ) -> tuple:
        """
        Returns signature payloads for approve_as_multi
        """
        nonce = self.get_nonce(from_address)
        approve_as_multi_payload = helper.approve_as_multi_signature_payload(
            self.metadata,
            self.spec_version,
            self.genesis_hash,
            nonce,
            to_address,
            value,
            other_signatories,
            transaction_version=self.transaction_version,
        )
        return approve_as_multi_payload, nonce

    def as_multi_payload(
        self,
        from_address: str,
        to_address: str,
        value: int,
        other_signatories: list,
        timepoint: tuple = None,
        store_call: bool = False,
        max_weight: int = 0,
    ) -> tuple:
        """
        Returns signature payloads for as_multi
        """
        nonce = self.get_nonce(from_address)
        as_multi_payload = helper.as_multi_signature_payload(
            self.metadata,
            self.spec_version,
            self.genesis_hash,
            nonce,
            to_address,
            value,
            other_signatories,
            timepoint,
            max_weight=max_weight,
            store_call=store_call,
            transaction_version=self.transaction_version,
        )
        return as_multi_payload, nonce

    def escrow_payloads(
        self, seller_address: str, escrow_address: str, trade_value: int, fee_value: int
    ) -> tuple:
        """
        Returns signature payloads for funding the multisig escrow,
        and sending the fee to the arbitrator
        """
        nonce = self.get_nonce(seller_address)
        escrow_payload = helper.transfer_signature_payload(
            self.metadata,
            escrow_address,
            trade_value,
            nonce,
            self.genesis_hash,
            self.spec_version,
            transaction_version=self.transaction_version,
        )
        fee_payload = helper.transfer_signature_payload(
            self.metadata,
            self.arbitrator_address,
            fee_value,
            nonce + 1,
            self.genesis_hash,
            self.spec_version,
            transaction_version=self.transaction_version,
        )
        return escrow_payload, fee_payload, nonce

    def release_escrow(
        self,
        buyer_address: str,
        trade_value: int,
        timepoint: tuple,
        other_signatories: list,
    ) -> str:
        """
        Return final arbitrator as_multi transaction for releasing escrow
        """
        nonce = self.arbitrator_nonce()
        release_payload = helper.as_multi_signature_payload(
            self.metadata,
            self.spec_version,
            self.genesis_hash,
            nonce,
            buyer_address,
            trade_value,
            other_signatories,
            timepoint,
            transaction_version=self.transaction_version,
        )
        release_signature = helper.sign_payload(self.keypair, release_payload)
        release_transaction = helper.unsigned_as_multi_construction(
            self.metadata,
            self.arbitrator_address,
            release_signature,
            nonce,
            buyer_address,
            trade_value,
            timepoint,
            other_signatories,
        )
        return release_transaction

    def cancellation(
        self,
        seller_address: str,
        trade_value: int,
        fee_value: int,
        other_signatories: list,
        timepoint: tuple,
    ) -> tuple:
        """
        Return signed and ready transactions for the fee return and escrow return
        """

        nonce = self.arbitrator_nonce()

        revert_payload = helper.as_multi_signature_payload(
            self.metadata,
            self.spec_version,
            self.genesis_hash,
            nonce,
            seller_address,
            trade_value,
            other_signatories,
            timepoint,
            transaction_version=self.transaction_version,
        )
        fee_revert_payload = helper.transfer_signature_payload(
            self.metadata,
            seller_address,
            fee_value,
            nonce + 1,
            self.genesis_hash,
            self.spec_version,
            transaction_version=self.transaction_version,
        )

        revert_signature = helper.sign_payload(self.keypair, revert_payload)
        fee_revert_signature = helper.sign_payload(self.keypair, fee_revert_payload)

        revert_transaction = helper.unsigned_as_multi_construction(
            self.metadata,
            self.arbitrator_address,
            revert_signature,
            nonce,
            seller_address,
            trade_value,
            timepoint,
            other_signatories,
        )
        fee_revert_transaction = helper.unsigned_transfer_construction(
            self.metadata,
            self.arbitrator_address,
            fee_revert_signature,
            nonce + 1,
            seller_address,
            fee_value,
        )
        return revert_transaction, fee_revert_transaction

    def resolve_dispute(
        self,
        victor: str,
        seller_address: str,
        trade_value: int,
        fee_value: int,
        other_signatories: list,
        welfare_value: int = 1000000000,
    ) -> tuple:
        """
        If sellers wins then return cancellation logic
        If buyer wins then return ready approveAsMulti and ready buyer welfare transfer
        """
        nonce = self.arbitrator_nonce()

        if victor == "seller":
            return self.cancellation(
                seller_address, trade_value, fee_value, other_signatories, None
            )

        release_payload = helper.approve_as_multi_signature_payload(
            self.metadata,
            self.spec_version,
            self.genesis_hash,
            nonce,
            seller_address,
            trade_value,
            other_signatories,
            transaction_version=self.transaction_version,
        )
        welfare_payload = helper.transfer_signature_payload(
            self.metadata,
            seller_address,
            welfare_value,
            nonce + 1,
            self.genesis_hash,
            self.spec_version,
            transaction_version=self.transaction_version,
        )

        release_signature = helper.sign_payload(self.keypair, release_payload)
        welfare_signature = helper.sign_payload(self.keypair, welfare_payload)

        release_transaction = helper.unsigned_approve_as_multi_construction(
            self.metadata,
            self.arbitrator_address,
            release_signature,
            nonce,
            seller_address,
            trade_value,
            other_signatories,
        )
        welfare_transaction = helper.unsigned_transfer_construction(
            self.metadata,
            self.arbitrator_address,
            welfare_signature,
            nonce + 1,
            seller_address,
            welfare_value,
        )
        return release_transaction, welfare_transaction

    def get_block_hash(self, node_response: dict) -> str:
        """
        Returns the block hash of a provided node response
        """
        return (
            node_response[max(node_response.keys())]
            .get("params", {})
            .get("result", {})
            .get("finalized")
        )

    def is_transaction_success(self, transaction_type: str, events: list) -> bool:
        """
        Returns if the a transaction according to the provided events and transaction type
        """
        successful = False
        event_names = []
        for event in events:
            event_names.append(event["event_id"])
        successful = (
            True
            if transaction_type == "transfer" and "Transfer" in event_names
            else successful
        )
        successful = (
            True
            if transaction_type == "approve_as_multi" and "NewMultisig" in event_names
            else successful
        )
        successful = (
            True
            if transaction_type == "as_multi"
            and (("MultisigExecuted" in event_names) or ("NewMultisig" in event_names))
            else successful
        )
        return successful

    def publish(self, type: str, params: list) -> tuple:
        """
        Raw extrinsic broadcast
        """
        if type == "transfer":
            transaction = helper.unsigned_transfer_construction(self.metadata, *params)
            return self.broadcast(type, transaction)

        if type == "fee_transfer":
            transaction = helper.unsigned_transfer_construction(
                self.metadata,
                params[0],
                params[1],
                params[2],
                self.arbitrator_address,
                params[3],
            )
            return self.broadcast("transfer", transaction)

        if type == "approve_as_multi":
            transaction = helper.unsigned_approve_as_multi_construction(
                self.metadata, *params
            )
            return self.broadcast(type, transaction)

        if type == "as_multi":
            transaction = helper.unsigned_as_multi_construction(self.metadata, *params)
            return self.broadcast(type, transaction)

    def broadcast(self, type: str, transaction: str) -> tuple:
        """
        Utility function to broadcast complete final transactions
        """
        node_response = self.network.node_rpc_call(
            "author_submitAndWatchExtrinsic", [transaction], watch=True
        )
        if "error" in str(node_response):
            return False, node_response
        tx_hash = self.get_extrinsic_hash(transaction)
        block_hash = self.get_block_hash(node_response)
        timepoint = self.get_extrinsic_timepoint(node_response, transaction)
        events = self.get_extrinsic_events(block_hash, timepoint[1])
        success = self.is_transaction_success(type, events)
        response = {
            "tx_hash": tx_hash,
            "timepoint": timepoint,
        }
        return success, response

    def diagnose(self, escrow_address: str) -> dict:
        """
        Returns details of all unfinished multisigs from an address
        """
        response = {}
        prefix = f"0x{helper.get_prefix(escrow_address, self.address_type)}"
        getkeys_response = self.network.node_rpc_call("state_getKeys", [prefix])

        if not getkeys_response.get("result", False):
            response["status"] = "error getting unfinished escrows"
            response["details"] = getkeys_response
            return response

        for item in getkeys_response["result"]:
            storage_result = self.network.node_rpc_call("state_getStorage", [item])[
                "result"
            ]
            return_decoder = ScaleDecoder.get_decoder_class(
                "Multisig<BlockNumber, BalanceOf, AccountId>",
                ScaleBytes(storage_result),
                metadata=self.metadata,
            )
            response[item[178:]] = return_decoder.decode()
        response["status"] = "unfinised escrows found"
        return response

    def as_multi_storage(
        self,
        to_address: str,
        other_signatory: str,
        amount: str,
        store_call: bool = True,
        max_weight: int = 648378000,
    ):
        nonce = self.arbitrator_nonce()
        payload = helper.as_multi_signature_payload(
            self.metadata,
            self.spec_version,
            self.genesis_hash,
            nonce,
            to_address,
            amount,
            [other_signatory, to_address],
            None,
            store_call=store_call,
            max_weight=max_weight,
            transaction_version=self.transaction_version,
        )
        signature = helper.sign_payload(self.keypair, payload)
        transaction = helper.unsigned_as_multi_construction(
            self.metadata,
            self.arbitrator_address,
            signature,
            nonce,
            to_address,
            amount,
            None,
            [other_signatory, to_address],
            store_call=store_call,
            max_weight=max_weight,
        )
        return transaction

    def fee_return_transaction(
        self, seller_address: str, trade_value: int, fee_value: int,
    ) -> str:
        nonce = self.arbitrator_nonce()
        fee_revert_payload = helper.transfer_signature_payload(
            self.metadata,
            seller_address,
            fee_value,
            nonce,
            self.genesis_hash,
            self.spec_version,
            transaction_version=self.transaction_version,
        )
        fee_revert_signature = helper.sign_payload(self.keypair, fee_revert_payload)
        fee_revert_transaction = helper.unsigned_transfer_construction(
            self.metadata,
            self.arbitrator_address,
            fee_revert_signature,
            nonce,
            seller_address,
            fee_value,
        )
        return fee_revert_transaction

    def welfare_transaction(
        self, buyer_address: str, welfare_value: int = 4000000000,
    ) -> str:
        # Note: 4000000000 (0.004 KSM) seems to be the minimum
        # To make an as_multi final tx once call is stored
        nonce = self.arbitrator_nonce()
        welfare_payload = helper.transfer_signature_payload(
            self.metadata,
            buyer_address,
            welfare_value,
            nonce,
            self.genesis_hash,
            self.spec_version,
            transaction_version=self.transaction_version,
        )
        welfare_signature = helper.sign_payload(self.keypair, welfare_payload)
        welfare_transaction = helper.unsigned_transfer_construction(
            self.metadata,
            self.arbitrator_address,
            welfare_signature,
            nonce,
            buyer_address,
            welfare_value,
        )
        return welfare_transaction


class Kusama(SubstrateBase):
    def __init__(
        self,
        *,
        node_url: str = "wss://kusama-rpc.polkadot.io/",
        arbitrator_key: str = None,
    ):
        self.chain = "kusama"
        self.address_type = 2
        super(Kusama, self).__init__(node_url=node_url, arbitrator_key=arbitrator_key)


class Polkadot(SubstrateBase):
    def __init__(
        self, *, node_url: str = "wss://rpc.polkadot.io/", arbitrator_key: str = None,
    ):
        self.chain = "polkadot"
        self.address_type = 0
        super(Polkadot, self).__init__(node_url=node_url, arbitrator_key=arbitrator_key)


class Kulupu(SubstrateBase):
    def __init__(
        self,
        *,
        node_url: str = "wss://rpc.kulupu.corepaper.org/ws",
        arbitrator_key: str = None,
    ):
        self.chain = "kulupu"
        self.address_type = 16
        super(Kulupu, self).__init__(node_url=node_url, arbitrator_key=arbitrator_key)

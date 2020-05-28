import logging
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

# Hardcode this because we WANT things to break if it changes
BLOCKCHAIN_VERSION = 1062

logger = logging.getLogger(__name__)


class NonceManager:
    """
    Extending this class allows a user to build in advanced nonce management
    in asyncronous environments where ordering is important
    """

    def arbitrator_nonce(self):
        return self.get_nonce(self.arbitrator_address)


class Kusama(NonceManager):
    def __init__(
        self,
        *,
        node_url: str = "wss://kusama-rpc.polkadot.io/",
        arbitrator_key: str = None,
        # The amount we give the buyer if they win a dispute
        welfare_value: int = 1000000000,
    ):
        self.node_url = node_url
        if arbitrator_key:
            self.setup_arbitrator(arbitrator_key)

    def connect(self, *, node_url: str = "", network: "Network" = None):
        node_url = self.node_url if not node_url else node_url
        if not network:
            network = Network(node_url=node_url)

        self.network = network
        assert self.check_version() == BLOCKCHAIN_VERSION

        RuntimeConfiguration().update_type_registry(
            load_type_registry_preset("default")
        )
        RuntimeConfiguration().update_type_registry(load_type_registry_preset("kusama"))

        self.metadata = self.get_metadata()
        self.spec_version = self.get_spec_version()
        self.genesis_hash = self.get_genesis_hash()

    def setup_arbitrator(self, arbitrator_key):
        self.keypair = sr25519.pair_from_seed(bytes.fromhex(arbitrator_key))
        self.arbitrator_account_id = self.keypair[0].hex()
        self.arbitrator_address = ss58_encode(self.keypair[0], 2)

    def check_version(self):
        """
        Make sure the versioning of the Kusama blockchain has not been
        updated since the last developer verification of the codebase
        """
        version = self.network.node_rpc_call(
            "state_getRuntimeVersion", [], loop_limit=1
        )
        return version[0]["result"]["specVersion"]

    def get_metadata(self):
        raw_metadata = self.network.node_rpc_call(
            "state_getMetadata", [None], loop_limit=1
        )[0]["result"]
        metadata = MetadataDecoder(ScaleBytes(raw_metadata))
        metadata.decode()
        return metadata

    def get_spec_version(self):
        return BLOCKCHAIN_VERSION

    def get_genesis_hash(self):
        return self.network.node_rpc_call("chain_getBlockHash", [0], loop_limit=1)[0][
            "result"
        ]

    def _get_address_info(self, address):
        # xxHash128(System) + xxHash128(Account)
        storage_key = (
            "0x26aa394eea5630e07c48ae0c9558cef7b99d880ec681799c0cf30e8886371da9"
        )

        account_id = ss58_decode(address, 2)
        hashed_address = f"{blake2b(bytes.fromhex(account_id), digest_size=16).digest().hex()}{account_id}"
        storage_hash = storage_key + hashed_address

        result = self.network.node_rpc_call(
            "state_getStorageAt", [storage_hash, None], loop_limit=1
        )[0]["result"]

        return_decoder = ScaleDecoder.get_decoder_class(
            "AccountInfo<Index, AccountData>",
            ScaleBytes(result),
            metadata=self.metadata,
        )
        return return_decoder.decode()

    def get_balance(self, address):
        result = self._get_address_info(address)
        return result["data"]["free"]

    def get_nonce(self, address):
        result = self._get_address_info(address)
        return result["nonce"]

    def get_block(self, block_hash):
        response = self.network.node_rpc_call(
            "chain_getBlock", [block_hash], loop_limit=1
        )[0]["result"]

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

    def get_events(self, block_hash):
        # If there's one more function where we have to do ths, let's add the helper function
        # xxHash128(System) + xxHash128(Events)
        storage_hash = (
            "0x26aa394eea5630e07c48ae0c9558cef780d41e5e16056765bc8461851072c9d7"
        )

        result = self.network.node_rpc_call(
            "state_getStorageAt", [storage_hash, block_hash], loop_limit=1
        )[0]["result"]

        return_decoder = ScaleDecoder.get_decoder_class(
            "Vec<EventRecord<Event, Hash>>", ScaleBytes(result), metadata=self.metadata,
        )
        return return_decoder.decode()

    def _get_extrinsix_index(self, block_extrinsics, extrinsic_hash):
        for idx, extrinsics in enumerate(block_extrinsics):
            ehash = extrinsics.get("extrinsic_hash")
            if ehash == extrinsic_hash:
                return idx
        return 0

    def get_extrinsic_hash(self, final_transaction):
        return (
            blake2b(bytes.fromhex(final_transaction[2:]), digest_size=32).digest().hex()
        )

    def get_extrinsic_timepoint(self, node_response, final_transaction):
        if not node_response:
            raise Exception("node_response is empty")

        last_item = node_response[max(node_response.keys())]
        finalized_hash = last_item.get("params", {}).get("result", {}).get("finalized")

        if not finalized_hash:
            raise Exception("Last item in the node_response is not finalized hash")

        extrinsic_hash = self.get_extrinsic_hash(final_transaction)

        block = self.get_block(finalized_hash)
        block_number = block.get("block").get("header").get("number")
        extrinsic_index = self._get_extrinsix_index(
            block.get("block").get("extrinsics"), extrinsic_hash
        )

        return (block_number, extrinsic_index)

    def get_extrinsic_events(self, block_hash, extrinsinc_index):
        events = self.get_events(block_hash)
        extrinsic_events = []
        for event in events:
            if event.get("extrinsic_idx") == extrinsinc_index:
                extrinsic_events.append(event)
        return extrinsic_events

    def get_escrow_address(self, buyer_address, seller_address, threshold=2):
        """
        Returns an escrow address for multisignature transactions
        """
        MultiAccountId = RuntimeConfiguration().get_decoder_class("MultiAccountId")

        multi_sig_account_id = MultiAccountId.create_from_account_list(
            [buyer_address, seller_address, self.arbitrator_address], 2
        )

        multi_sig_address = ss58_encode(multi_sig_account_id.value.replace("0x", ""), 2)
        return multi_sig_address

    def transfer_payload(self, from_address, to_address, value):
        """
        Get signature payloads for a regular transfer
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

    def escrow_payloads(self, seller_address, escrow_address, trade_value, fee_value):
        """
        Get signature payloads for funding the multisig escrow,
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
        )
        fee_payload = helper.transfer_signature_payload(
            self.metadata,
            self.arbitrator_address,
            fee_value,
            nonce + 1,
            self.genesis_hash,
            self.spec_version,
        )
        return escrow_payload, fee_payload, nonce

    def release_escrow(self, buyer_address, trade_value, timepoint, other_signatories):
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

    def cancellation(self, seller_address, trade_value, fee_value, other_signatories):
        """
        Return signed and ready transactions for the fee return and escrow return
        """
        assert fee_value <= trade_value * 0.01
        nonce = self.arbitrator_nonce()

        revert_payload = helper.approve_as_multi_signature_payload(
            self.metadata,
            self.spec_version,
            self.genesis_hash,
            nonce,
            seller_address,
            trade_value,
            other_signatories,
        )
        fee_revert_payload = helper.transfer_signature_payload(
            self.metadata,
            seller_address,
            fee_value,
            nonce + 1,
            self.genesis_hash,
            self.spec_version,
        )

        revert_signature = helper.sign_payload(self.keypair, revert_payload)
        fee_revert_signature = helper.sign_payload(self.keypair, fee_revert_payload)

        revert_transaction = helper.unsigned_approve_as_multi_construction(
            self.metadata,
            self.arbitrator_account_id,
            revert_signature,
            nonce,
            seller_address,
            trade_value,
            other_signatories,
        )
        fee_revert_transaction = helper.unsigned_transfer_construction(
            self.metadata,
            self.arbitrator_account_id,
            fee_revert_signature,
            nonce + 1,
            seller_address,
            fee_value,
        )
        return revert_transaction, fee_revert_transaction

    def resolve_dispute(
        self, victor, seller_address, trade_value, fee_value, other_signatories
    ):
        """
        If sellers wins then return cancellation logic
        If buyer wins then return ready approveAsMulti and ready buyer replenishment
        """
        if victor == "seller":
            return self.cancellation(
                seller_address, trade_value, fee_value, other_signatories
            )

        nonce = self.arbitrator_nonce()
        release_payload = helper.approve_as_multi_signature_payload(
            self.metadata,
            self.spec_version,
            self.genesis_hash,
            nonce,
            seller_address,
            trade_value,
            other_signatories,
        )
        buyer_welfare_payload = helper.transfer_signature_payload(
            self.metadata,
            seller_address,
            self.welfare_value,
            nonce + 1,
            self.genesis_hash,
            self.spec_version,
        )

        release_signature = helper.sign_payload(self.keypair, release_payload)
        welfare_signature = helper.sign_payload(self.keypair, buyer_welfare_payload)

        release_transaction = helper.unsigned_approve_as_multi_construction(
            self.metadata,
            self.arbitrator_account_id,
            release_signature,
            nonce,
            seller_address,
            trade_value,
            other_signatories,
        )
        welfare_transaction = helper.unsigned_transfer_construction(
            self.metadata,
            self.arbitrator_account_id,
            welfare_signature,
            nonce + 1,
            seller_address,
            self.welfare_value,
        )
        return release_transaction, welfare_transaction

    def get_block_hash(self, node_response):
        return (
            node_response[max(node_response.keys())]
            .get("params", {})
            .get("result", {})
            .get("finalized")
        )

    def is_transaction_success(self, transaction_type, events):
        successfull = False
        event_names = []
        for event in events:
            event_names.append(event["event_id"])
        if transaction_type == "transfer" and "Transfer" in event_names:
            successfull = True
        return successfull

    def publish(self, type, params):
        """
        Raw extrinsic broadcast
        """
        if type == "transfer":
            final_transaction = helper.unsigned_transfer_construction(
                self.metadata, *params
            )
            node_response = self.network.node_rpc_call(
                "author_submitAndWatchExtrinsic", [final_transaction]
            )
            tx_hash = self.get_extrinsic_hash(final_transaction)
            block_hash = self.get_block_hash(node_response)
            timepoint = self.get_extrinsic_timepoint(node_response, final_transaction)
            events = self.get_extrinsic_events(block_hash, timepoint[1])
            success = self.is_transaction_success("transfer", events)
            return tx_hash, timepoint, success

        if type == "fee_transfer":
            final_transaction = helper.unsigned_transfer_construction(
                self.metadata,
                params[0],
                params[1],
                params[2],
                self.arbitrator_address,
                params[3],
            )
            node_response = self.network.node_rpc_call(
                "author_submitAndWatchExtrinsic", [final_transaction]
            )
            tx_hash = self.get_extrinsic_hash(final_transaction)
            block_hash = self.get_block_hash(node_response)
            timepoint = self.get_extrinsic_timepoint(node_response, final_transaction)
            events = self.get_extrinsic_events(block_hash, timepoint[1])
            success = self.is_transaction_success("transfer", events)
            return tx_hash, timepoint, success

        if type == "approve_as_multi":
            final_transaction = helper.unsigned_approve_as_multi_construction(
                self.metadata, *params
            )
            node_response = self.network.node_rpc_call(
                "author_submitAndWatchExtrinsic", [final_transaction]
            )
            tx_hash = self.get_extrinsic_hash(final_transaction)
            block_hash = self.get_block_hash(node_response)
            timepoint = self.get_extrinsic_timepoint(node_response, final_transaction)
            events = self.get_extrinsic_events(block_hash, timepoint[1])
            success = self.is_transaction_success("approve_as_multi", events)
            return tx_hash, timepoint, success

        if type == "as_multi":
            final_transaction = helper.unsigned_as_multi_construction(
                self.metadata, *params
            )
            node_response = self.network.node_rpc_call(
                "author_submitAndWatchExtrinsic", [final_transaction]
            )
            tx_hash = self.get_extrinsic_hash(final_transaction)
            block_hash = self.get_block_hash(node_response)
            timepoint = self.get_extrinsic_timepoint(node_response, final_transaction)
            events = self.get_extrinsic_events(block_hash, timepoint[1])
            success = self.is_transaction_success("as_multi", events)
            return tx_hash, timepoint, success

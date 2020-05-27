import logging
from hashlib import blake2b

from scalecodec import ScaleBytes
from scalecodec.base import RuntimeConfiguration
from scalecodec.base import ScaleDecoder
from scalecodec.metadata import MetadataDecoder
from scalecodec.type_registry import load_type_registry_preset
from scalecodec.utils.ss58 import ss58_decode

from .helper import kusama_addr_to_id
from .helper import id_to_kusama_addr
from .network import Network

# Hardcode this because we WANT things to break if it changes
BLOCKCHAIN_VERSION = 1062

logger = logging.getLogger(__name__)


class Kusama:
    def __init__(self, *, address: str = "wss://kusama-rpc.polkadot.io/", admin_addr: str = ""):
        self.address = address
        self.admin_addr = admin_addr

    def connect(self, *, address: str = "", network: "Network" = None):
        address = self.address if not address else address
        if not network:
            network = Network(address=address)

        self.network = network
        assert self.check_version() == BLOCKCHAIN_VERSION

        # WARNING: Relying on side effects to run code is dangerous, refactor this if possible
        RuntimeConfiguration().update_type_registry(
            load_type_registry_preset("default")
        )
        RuntimeConfiguration().update_type_registry(load_type_registry_preset("kusama"))

        self.metadata = self.get_metadata()
        self.spec_version = self.get_spec_version()
        self.genesis_hash = self.get_genesis_hash()

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

    def broadcast_extrinsic(self):
        """
        Raw extrinsic broadcast
        """
        pass

    def broadcast(self):
        """
        Handles final transaction construction according to transaction type
        """
        pass

    def unsigned_transfer(self):
        """
        Unsigned transfer endpoint
        """
        pass

    def create_escrow(self):
        """
        Get unsigned escrow transactions
        """
        pass

    def get_escrow_address(self, buyer_addr, seller_addr, threshold=2):
        """
        Gets an escrow address for multisignature transactions

        Params:
        -------
        buyer_address - str
        seller_address - str
        escrow_address - str
        threshold - int

        Returns:
        --------
        escrow address - str
        """
        MultiAccountId = RuntimeConfiguration().get_decoder_class("MultiAccountId")

        multi_sig_account = MultiAccountId.create_from_account_list(
            [buyer_addr, seller_addr, self.admin_addr], 2)

        multi_sig_address = id_to_kusama_addr(multi_sig_account.value.replace('0x', ''))
        return multi_sig_address


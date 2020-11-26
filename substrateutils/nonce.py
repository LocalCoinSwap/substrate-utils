from abc import ABC
from abc import abstractmethod

from scalecodec.utils.ss58 import ss58_decode


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

from abc import ABC, abstractmethod
import inspect
from ..device.model import DeviceIdentifier

class CertificateStore(ABC):

    def __new__(cls, *arg, **kwargs):
        # get all coros 
        parent_coros = inspect.getmembers(CertificateStore, predicate=inspect.iscoroutinefunction)

        # check if parent's coros are still coros in a child
        for coro in parent_coros:
            child_method = getattr(cls, coro[0])
            if not inspect.iscoroutinefunction(child_method):
                raise RuntimeError('The method %s must be a coroutine' % (child_method,))

        # return super(CertificateStore, cls).__new__(cls, *arg, **kwargs)
        return super(CertificateStore, cls).__new__(cls)

    @abstractmethod
    async def getBootstrapCertificateAuthority(self, deviceIdentifier: DeviceIdentifier) -> str:
        """
        Implementation as to return a string/buffer of bootstrap's CA certificate
        * @param deviceIdentifier Device properties
        """
        pass

    @abstractmethod
    async def getBootstrapChainCertificate(self, deviceIdentifier: DeviceIdentifier) -> str:
        """
        Implementation as to return a string/buffer of bootstrap's Device certificate
        * @param deviceIdentifier Device properties
        """
        pass

    @abstractmethod
    async def getBootstrapPrivateKey(self, deviceIdentifier: DeviceIdentifier) -> str:
        """
        Implementation as to return a string/buffer of bootstrap's private key certificate
        * @param deviceIdentifier Device properties
        """
        pass

    @abstractmethod
    async def getPerpetualCertificateAuthority(self, deviceIdentifier: DeviceIdentifier) -> str:
        """
        Implementation as to return a string/buffer of perpetual's CA certificate
        * @param deviceIdentifier Device properties
        """
        pass

    @abstractmethod
    async def getPerpetualChainCertificate(self, deviceIdentifier: DeviceIdentifier) -> str:
        """
        Implementation as to return a string/buffer of perpetual's Device certificate
        * @param deviceIdentifier Device properties
        """
        pass

    @abstractmethod
    async def getPerpetualPrivateKey(self, deviceIdentifier: DeviceIdentifier) -> str:
        """
        Implementation as to return a string/buffer of perpetual's private key certificate
        * @param deviceIdentifier Device properties
        """
        pass

    @abstractmethod
    async def savePerpetualCertificateAuthority(self, deviceIdentifier: DeviceIdentifier, certificate: str) -> None:
        """
        Implementation as to save a string/buffer of perpetual's CA certificate
        * @param deviceIdentifier Device properties
        """
        pass

    @abstractmethod
    async def savePerpetualChainCertificate(self, deviceIdentifier: DeviceIdentifier, certificate: str) -> None:
        """
        Implementation as to save a string/buffer of perpetual's Device certificate
        * @param deviceIdentifier Device properties
        """
        pass

    @abstractmethod
    async def savePerpetualPrivateKey(self, deviceIdentifier: DeviceIdentifier, certificate: str) -> None:
        """
        Implementation as to save a string/buffer of perpetual's private key certificate
        * @param deviceIdentifier Device properties
        """
        pass
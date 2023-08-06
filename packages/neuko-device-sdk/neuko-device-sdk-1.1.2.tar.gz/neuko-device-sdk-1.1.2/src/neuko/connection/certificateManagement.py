from ..utility.logger import Logger
from .certificateStore import CertificateStore
from ..device.model import DeviceIdentifier
from .model import Certificate

logger = Logger("CertificateManagement").set()

class CertificateManagement:
    
    def __init__(self, store: CertificateStore) -> None:
        self._store = store

    @property
    def store(self):
        """Internal property - store"""
        return self._store

    @store.getter
    def store(self):
        return self._store

    @store.setter
    def store(self, store: CertificateStore):
        self._store = store

    async def getBootstrapCertificates(self, deviceIdentifier: DeviceIdentifier) -> Certificate:
        try:
            return Certificate(
                await self._store.getBootstrapCertificateAuthority(deviceIdentifier),
                await self._store.getBootstrapChainCertificate(deviceIdentifier),
                await self._store.getBootstrapPrivateKey(deviceIdentifier)
            )
        except:
            logger.error("Error fetching bootstrap certificates")
            raise Exception("OperationError")

    async def getPerpetualCertificates(self, deviceIdentifier: DeviceIdentifier) -> Certificate:
        try:
            return Certificate(
                await self._store.getPerpetualCertificateAuthority(deviceIdentifier),
                await self._store.getPerpetualChainCertificate(deviceIdentifier),
                await self._store.getPerpetualPrivateKey(deviceIdentifier)
            )
        except:
            logger.error("Error fetching perpetual certificates")
            raise Exception("OperationError")

    async def savePerpetualCertificates(self, deviceIdentifier: DeviceIdentifier, certificates: Certificate) -> bool:
        try:
            await self._store.savePerpetualCertificateAuthority(deviceIdentifier, certificates.certificateAuthority)
            logger.debug("Perpetual certificate authority saved")

            await self._store.savePerpetualChainCertificate(deviceIdentifier, certificates.chainCertificate)
            logger.debug("Perpetual chain certificate saved")

            await self._store.savePerpetualPrivateKey(deviceIdentifier, certificates.privateKey)
            logger.debug("Perpetual private key saved")
            return True
        except:
            logger.error("Error saving perpetual certificates")
            raise Exception("OperationError")
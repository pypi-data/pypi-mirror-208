import unittest
from unittest.mock import patch
from src.neuko.connection.certificateStore import CertificateStore
from src.neuko.device.model import DeviceIdentifier

class TestObjectCertificateStore(CertificateStore):

    def __init__(self, arg1: str, arg2: str, *arg, **kwargs) -> None:
        super().__init__(*arg, **kwargs)
        self.arg1 = arg1
        self.arg2 = arg2

    async def getBootstrapCertificateAuthority(self, deviceIdentifier: DeviceIdentifier) -> str:
        return ""

    async def getBootstrapChainCertificate(self, deviceIdentifier: DeviceIdentifier) -> str:
        return ""

    async def getBootstrapPrivateKey(self, deviceIdentifier: DeviceIdentifier) -> str:
        return ""

    async def getPerpetualCertificateAuthority(self, deviceIdentifier: DeviceIdentifier) -> str:
        return ""

    async def getPerpetualChainCertificate(self, deviceIdentifier: DeviceIdentifier) -> str:
        return ""

    async def getPerpetualPrivateKey(self, deviceIdentifier: DeviceIdentifier) -> str:
        return ""

    async def savePerpetualCertificateAuthority(self, deviceIdentifier: DeviceIdentifier, certificate: str) -> None:
        pass

    async def savePerpetualChainCertificate(self, deviceIdentifier: DeviceIdentifier, certificate: str) -> None:
        pass

    async def savePerpetualPrivateKey(self, deviceIdentifier: DeviceIdentifier, certificate: str) -> None:
        pass

class ConnectionStoreTest(unittest.TestCase):

    @patch("src.neuko.connection.certificateStore.CertificateStore.__abstractmethods__", set())
    def test_01_init_class(self):
        '''
        Test to initiate the class
        '''
        certStore = CertificateStore()
        self.assertTrue(True)

    # @patch("src.neuko.connection.certificateStore.CertificateStore.__abstractmethods__", set())
    def test_02_init_class_with_local_args(self):
        '''
        Test to initiate the class
        '''
        certStore = TestObjectCertificateStore("a", "b")
        with self.subTest():
            self.assertEqual(certStore.arg1, "a")
        with self.subTest():
            self.assertEqual(certStore.arg2, "b")


if __name__ == '__main__':
    unittest.main()
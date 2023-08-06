import unittest
import asyncio
from src.neuko.connection.certificateManagement import CertificateManagement
from src.neuko.connection.certificateStore import CertificateStore
from src.neuko.connection.model import Certificate
from src.neuko.device.model import DeviceIdentifier

class CertificateStoreTestObject(CertificateStore):

    async def getBootstrapCertificateAuthority(self, deviceIdentifier: DeviceIdentifier) -> str:
        fd = open("./tests/cacerttest.txt", mode="r")
        raw = fd.read()
        fd.close()
        return raw

    async def getBootstrapChainCertificate(self, deviceIdentifier: DeviceIdentifier) -> str:
        fd = open("./tests/chaincerttest.txt", mode="r")
        raw = fd.read()
        fd.close()
        return raw

    async def getBootstrapPrivateKey(self, deviceIdentifier: DeviceIdentifier) -> str:
        fd = open("./tests/privatekeytest.txt", mode="r")
        raw = fd.read()
        fd.close()
        return raw

    async def getPerpetualCertificateAuthority(self, deviceIdentifier: DeviceIdentifier) -> str:
        fd = open("./tests/cacerttest.txt", mode="r")
        raw = fd.read()
        fd.close()
        return raw

    async def getPerpetualChainCertificate(self, deviceIdentifier: DeviceIdentifier) -> str:
        fd = open("./tests/chaincerttest.txt", mode="r")
        raw = fd.read()
        fd.close()
        return raw

    async def getPerpetualPrivateKey(self, deviceIdentifier: DeviceIdentifier) -> str:
        fd = open("./tests/privatekeytest.txt", mode="r")
        raw = fd.read()
        fd.close()
        return raw

    async def savePerpetualCertificateAuthority(self, deviceIdentifier: DeviceIdentifier, certificate: str) -> None:
        fd = open("./tests/cacertsavetest.txt", mode="w")
        fd.write(certificate)
        fd.close()

    async def savePerpetualChainCertificate(self, deviceIdentifier: DeviceIdentifier, certificate: str) -> None:
        fd = open("./tests/chaincertsavetest.txt", mode="w")
        fd.write(certificate)
        fd.close()

    async def savePerpetualPrivateKey(self, deviceIdentifier: DeviceIdentifier, certificate: str) -> None:
        fd = open("./tests/privatekeysavetest.txt", mode="w")
        fd.write(certificate)
        fd.close()

class CertificateManagementTest(unittest.TestCase):
    
    def setUp(self):
        self.asyncloop = asyncio.new_event_loop()
        self.addCleanup(self.asyncloop.close)

    def test_01_get_bootstrap_certificates(self):
        deviceId = DeviceIdentifier("testAccountId", "testProjectId", "testSchemaId", "testDeviceId")
        store = CertificateStoreTestObject()
        manager = CertificateManagement(store)
        certs = self.asyncloop.run_until_complete(manager.getBootstrapCertificates(deviceId)) 
        print(certs.certificateAuthority)
        with self.subTest():
            self.assertAlmostEqual(certs.certificateAuthority, "certificateauthority")
        with self.subTest():
            self.assertAlmostEqual(certs.chainCertificate, "chaincerttest")
        with self.subTest():
            self.assertAlmostEqual(certs.privateKey, "privatekeytest")

    def test_02_get_perpetual_certificates(self):
        deviceId = DeviceIdentifier("testAccountId", "testProjectId", "testSchemaId", "testDeviceId")
        store = CertificateStoreTestObject()
        manager = CertificateManagement(store)
        certs = self.asyncloop.run_until_complete(manager.getPerpetualCertificates(deviceId)) 
        print(certs.certificateAuthority)
        with self.subTest():
            self.assertAlmostEqual(certs.certificateAuthority, "certificateauthority")
        with self.subTest():
            self.assertAlmostEqual(certs.chainCertificate, "chaincerttest")
        with self.subTest():
            self.assertAlmostEqual(certs.privateKey, "privatekeytest")

    def test_03_save_perpetual_certificates(self):
        deviceId = DeviceIdentifier("testAccountId", "testProjectId", "testSchemaId", "testDeviceId")
        store = CertificateStoreTestObject()
        manager = CertificateManagement(store)
        certs = Certificate("cacertsavetest", "chaincertsavetest", "privatekeysavetest")
        self.asyncloop.run_until_complete(manager.savePerpetualCertificates(deviceId, certs))
        with self.subTest():
            fd = open("./tests/cacertsavetest.txt", mode="r")
            raw = fd.read()
            fd.close()
            self.assertAlmostEqual(raw, "cacertsavetest")
        with self.subTest():
            fd = open("./tests/chaincertsavetest.txt", mode="r")
            raw = fd.read()
            fd.close()
            self.assertAlmostEqual(raw, "chaincertsavetest")
        with self.subTest():
            fd = open("./tests/privatekeysavetest.txt", mode="r")
            raw = fd.read()
            fd.close()
            self.assertAlmostEqual(raw, "privatekeysavetest")

    
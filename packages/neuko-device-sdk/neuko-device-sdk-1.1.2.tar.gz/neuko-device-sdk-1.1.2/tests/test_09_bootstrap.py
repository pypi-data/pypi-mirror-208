import unittest
import asyncio
import json
import shutil
import os
from paho.mqtt.client import MQTTMessage
from os.path import exists
from dotenv import load_dotenv
from src.neuko.utility.logger import Logger
from src.neuko.connection.certificateManagement import CertificateManagement
from src.neuko.connection.certificateStore import CertificateStore
from src.neuko.connection.connectionManagement import ConnectionManagement
from src.neuko.connection.connectionStore import ConnectionStore
from src.neuko.connection.model import Certificate, Provider
from src.neuko.device.model import DeviceIdentifier
from src.neuko.iot.bootstrap import BootstrapClient

load_dotenv()
logger = Logger("BootstrapTest").set()

class CertificateStoreTestObject(CertificateStore):

    async def getBootstrapCertificateAuthority(self, deviceIdentifier: DeviceIdentifier) -> str:
        # fd = open("./tests/tmp/cert.ca.pem", mode="r")
        # raw = fd.read()
        # fd.close()
        # return raw
        return "./tests/tmp/cert.ca.pem"

    async def getBootstrapChainCertificate(self, deviceIdentifier: DeviceIdentifier) -> str:
        # fd = open("./tests/tmp/6ccc8d6d46-certificate.pem.crt", mode="r")
        # raw = fd.read()
        # fd.close()
        # return raw
        return "./tests/tmp/6ccc8d6d46-certificate.pem.crt"
        # return "./tests/tmp/certificate.pem.crt"

    async def getBootstrapPrivateKey(self, deviceIdentifier: DeviceIdentifier) -> str:
        # fd = open("./tests/tmp/6ccc8d6d46-private.pem.key", mode="r")
        # raw = fd.read()
        # fd.close()
        # return raw
        return "./tests/tmp/6ccc8d6d46-private.pem.key"
        # return "./tests/tmp/private.pem.key"

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


class ConnectionStoreTest(ConnectionStore):
    async def getPerpetualConnectionSettings(self, deviceIdentifier: DeviceIdentifier) -> str:
        fd = open("./tests/connectionSettingsTestValue.json", mode="r")
        raw = json.load(fd)
        fd.close()
        return raw

    async def savePerpetualConnectionSettings(self, deviceIdentifier: DeviceIdentifier, settings: str) -> bool:
        fd = open("./tests/connectionSettingsTestValueSaveTest.json", mode="w")
        json.dump(settings, fd)
        fd.close()
        return True

    async def deletePerpetualConnectionSettings(self, deviceIdentifier: DeviceIdentifier) -> bool:
        return True

    async def isPerpetualConnectionSettingsExists(self, deviceIdentifier: DeviceIdentifier) -> bool:
        return False


class BootstrapTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        # backup before test
        shutil.copy("./config.ini", "config-backup-before-test.ini")
        # copy test config
        shutil.copy("./tests/config.ini", "./config.ini")

    @classmethod
    def tearDownClass(cls) -> None:
        # restore
        shutil.copy("./config-backup-before-test.ini", "config.ini")
        # remove backup file
        os.remove("./config-backup-before-test.ini")

    def setUp(self):
        self.asyncloop = asyncio.new_event_loop()
        self.addCleanup(self.asyncloop.close)
        self.deviceId = DeviceIdentifier("acc_i8Ga2RzmtQ8X", "prj_vH5VmqBjWYJU", "sch_V5HoA4ZtuwCQ", "SP0002")
        certStore = CertificateStoreTestObject()
        certManager = CertificateManagement(certStore)
        connStore = ConnectionStoreTest()
        connManager = ConnectionManagement(connStore)

        self.bootstrapClient = BootstrapClient(deviceIdentifier= self.deviceId,connectionManager= connManager,certificateManager= certManager)

    def tearDown(self) -> None:
        if self.bootstrapClient.connected:
            self.asyncloop.run_until_complete(self.bootstrapClient.disconnect())

    def test_01_connection(self):
        try:
            self.asyncloop.run_until_complete(self.bootstrapClient.loadContextCertificate(Provider.BOOTSTRAP))
            self.asyncloop.run_until_complete(self.bootstrapClient.loadContextConfiguration(Provider.BOOTSTRAP))
            with self.subTest():
                self.asyncloop.run_until_complete(self.bootstrapClient.connect())
                logger.info("IoT is connected")
                self.assertTrue(True)
            with self.subTest():
                self.asyncloop.run_until_complete(self.bootstrapClient.disconnect())
                logger.info("IoT is disconnected")
                self.assertTrue(True)
            
        except Exception as ex:
            logger.error(ex)
            self.assertTrue(False)

    def test_02_subscribe_wrong_topic(self):
        try:
            self.asyncloop.run_until_complete(self.bootstrapClient.loadContextCertificate(Provider.BOOTSTRAP))
            self.asyncloop.run_until_complete(self.bootstrapClient.loadContextConfiguration(Provider.BOOTSTRAP))
            self.asyncloop.run_until_complete(self.bootstrapClient.connect())
            topic = f'$aws/rules/non-exists'
            with self.subTest():
                self.asyncloop.run_until_complete(self.bootstrapClient.subscribe(topic))
                self.assertTrue(self.bootstrapClient.connected)
        except Exception as ex:
            self.asyncloop.run_until_complete(self.bootstrapClient.disconnect())
            logger.info(ex)
            self.assertTrue(True)

    def test_03_subscribe_without_listener_and_unsubscribe(self):
        try:
            self.asyncloop.run_until_complete(self.bootstrapClient.loadContextCertificate(Provider.BOOTSTRAP))
            self.asyncloop.run_until_complete(self.bootstrapClient.loadContextConfiguration(Provider.BOOTSTRAP))
            self.asyncloop.run_until_complete(self.bootstrapClient.connect())
            topic = f'$aws/things/{self.deviceId.accountId}-{self.deviceId.projectId}-{self.deviceId.deviceId}/shadow/name/state_1/get/accepted'
            with self.subTest():
                self.asyncloop.run_until_complete(self.bootstrapClient.subscribe(topic))
                self.assertEqual(self.bootstrapClient._topics[0], topic)
        except Exception as ex:
            self.asyncloop.run_until_complete(self.bootstrapClient.disconnect())
            logger.error(ex)
            self.assertTrue(False)

    def test_04_subscribe_without_listener(self):
        try:
            self.asyncloop.run_until_complete(self.bootstrapClient.loadContextCertificate(Provider.BOOTSTRAP))
            self.asyncloop.run_until_complete(self.bootstrapClient.loadContextConfiguration(Provider.BOOTSTRAP))
            self.asyncloop.run_until_complete(self.bootstrapClient.connect())
            topic = f'$aws/things/{self.deviceId.accountId}-{self.deviceId.projectId}-{self.deviceId.deviceId}/shadow/name/state_1/get/accepted'
            with self.subTest():
                self.asyncloop.run_until_complete(self.bootstrapClient.subscribe(topic))
                self.assertEqual(self.bootstrapClient._topics[0], topic)
            with self.subTest():
                self.asyncloop.run_until_complete(self.bootstrapClient.unsubscribe(topic))
                self.assertEqual(len(self.bootstrapClient._topics), 0)
        except Exception as ex:
            self.asyncloop.run_until_complete(self.bootstrapClient.disconnect())
            logger.error(ex)
            self.assertTrue(False)

    def test_05_subscribe_listener(self):
        try:
            self.asyncloop.run_until_complete(self.bootstrapClient.loadContextCertificate(Provider.BOOTSTRAP))
            self.asyncloop.run_until_complete(self.bootstrapClient.loadContextConfiguration(Provider.BOOTSTRAP))
            self.asyncloop.run_until_complete(self.bootstrapClient.connect())
            topic = f'$aws/things/{self.deviceId.accountId}-{self.deviceId.projectId}-{self.deviceId.deviceId}/shadow/name/state_1/get'

            def callback(context: BootstrapTest, client, userdata, message: MQTTMessage):
                data = json.loads(message.payload)
                value = data['state']['reported']['attribute_1']
                context.assertEqual(value, 'high')

            self.asyncloop.run_until_complete(self.bootstrapClient.subscribe(f'{topic}/accepted', lambda client, userdata, message: callback(self, client, userdata, message)))
            self.asyncloop.run_until_complete(self.bootstrapClient.publish(topic, None))
            
        except Exception as ex:
            self.asyncloop.run_until_complete(self.bootstrapClient.disconnect())
            logger.error(ex)
            self.assertTrue(False)

    def test_06_fetch_all_telemetric_statenames_illegal(self):
        self.asyncloop.run_until_complete(self.bootstrapClient.loadContextCertificate(Provider.BOOTSTRAP))
        self.asyncloop.run_until_complete(self.bootstrapClient.loadContextConfiguration(Provider.BOOTSTRAP))
        self.asyncloop.run_until_complete(self.bootstrapClient.connect())
        with self.assertRaises(Exception) as context:
            self.asyncloop.run_until_complete(self.bootstrapClient.fetchAllTelemetricStateNames())
        self.assertTrue('IllegalMethod' in str(context.exception))

    def test_07_pull_telemetric_state_illegal(self):
        self.asyncloop.run_until_complete(self.bootstrapClient.loadContextCertificate(Provider.BOOTSTRAP))
        self.asyncloop.run_until_complete(self.bootstrapClient.loadContextConfiguration(Provider.BOOTSTRAP))
        self.asyncloop.run_until_complete(self.bootstrapClient.connect())
        with self.assertRaises(Exception) as context:
            self.asyncloop.run_until_complete(self.bootstrapClient.pullTelemetricState('state_1'))
        self.assertTrue('IllegalMethod' in str(context.exception))

    def test_08_push_telemetric_state_illegal(self):
        self.asyncloop.run_until_complete(self.bootstrapClient.loadContextCertificate(Provider.BOOTSTRAP))
        self.asyncloop.run_until_complete(self.bootstrapClient.loadContextConfiguration(Provider.BOOTSTRAP))
        self.asyncloop.run_until_complete(self.bootstrapClient.connect())
        with self.assertRaises(Exception) as context:
            self.asyncloop.run_until_complete(self.bootstrapClient.pushTelemetricState('state_1', {}))
        self.assertTrue('IllegalMethod' in str(context.exception))

    def test_09_timestream_storage_illegal(self):
        self.asyncloop.run_until_complete(self.bootstrapClient.loadContextCertificate(Provider.BOOTSTRAP))
        self.asyncloop.run_until_complete(self.bootstrapClient.loadContextConfiguration(Provider.BOOTSTRAP))
        self.asyncloop.run_until_complete(self.bootstrapClient.connect())
        with self.assertRaises(Exception) as context:
            self.asyncloop.run_until_complete(self.bootstrapClient.timestreamStorage('state_1', {}))
        self.assertTrue('IllegalMethod' in str(context.exception))

    def test_10_on_telemetric_state_change_request_illegal(self):
        self.asyncloop.run_until_complete(self.bootstrapClient.loadContextCertificate(Provider.BOOTSTRAP))
        self.asyncloop.run_until_complete(self.bootstrapClient.loadContextConfiguration(Provider.BOOTSTRAP))
        self.asyncloop.run_until_complete(self.bootstrapClient.connect())
        with self.assertRaises(Exception) as context:
            self.asyncloop.run_until_complete(self.bootstrapClient.onTelemetricStateChangedRequest(self, None))
        self.assertTrue('IllegalMethod' in str(context.exception))
        
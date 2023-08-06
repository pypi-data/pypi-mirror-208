import unittest
import asyncio
import json
import uuid
import time
import shutil
import random
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
from src.neuko.iot.model import UpdateDelta
from src.neuko.iot.neuko import NeukoClient

load_dotenv()
logger = Logger("NeukoTest").set()

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


class NeukoTest(unittest.TestCase):

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
        self.outsideFlag = False
        self.asyncloop = asyncio.new_event_loop()
        self.addCleanup(self.asyncloop.close)
        self.deviceId = DeviceIdentifier("acc_i8Ga2RzmtQ8X", "prj_vH5VmqBjWYJU", "sch_V5HoA4ZtuwCQ", "SP0002")
        certStore = CertificateStoreTestObject()
        certManager = CertificateManagement(certStore)
        connStore = ConnectionStoreTest()
        connManager = ConnectionManagement(connStore)

        self.client = NeukoClient(deviceIdentifier= self.deviceId,connectionManager= connManager,certificateManager= certManager)

    def tearDown(self) -> None:
        if self.client.connected:
            logger.debug("Disconnecting IoT client")
            self.asyncloop.run_until_complete(self.client.disconnect())

    def test_01_connection(self):
        try:
            self.asyncloop.run_until_complete(self.client.loadContextCertificate(Provider.BOOTSTRAP))
            self.asyncloop.run_until_complete(self.client.loadContextConfiguration(Provider.BOOTSTRAP))
            with self.subTest():
                self.asyncloop.run_until_complete(self.client.connect())
                logger.info("IoT is connected")
                self.assertTrue(True)
            with self.subTest():
                self.asyncloop.run_until_complete(self.client.disconnect())
                logger.info("IoT is disconnected")
                self.assertTrue(True)
            
        except Exception as ex:
            logger.error(ex)
            self.assertTrue(False)

    def test_02_subscribe_wrong_topic(self):
        try:
            self.asyncloop.run_until_complete(self.client.loadContextCertificate(Provider.BOOTSTRAP))
            self.asyncloop.run_until_complete(self.client.loadContextConfiguration(Provider.BOOTSTRAP))
            self.asyncloop.run_until_complete(self.client.connect())
            topic = f'$aws/rules/non-exists'
            with self.subTest():
                self.asyncloop.run_until_complete(self.client.subscribe(topic))
                self.assertTrue(self.client.connected)
        except Exception as ex:
            self.asyncloop.run_until_complete(self.client.disconnect())
            logger.info(ex)
            self.assertTrue(True)

    def test_03_subscribe_without_listener_and_unsubscribe(self):
        try:
            self.asyncloop.run_until_complete(self.client.loadContextCertificate(Provider.BOOTSTRAP))
            self.asyncloop.run_until_complete(self.client.loadContextConfiguration(Provider.BOOTSTRAP))
            self.asyncloop.run_until_complete(self.client.connect())
            topic = f'$aws/things/{self.deviceId.accountId}-{self.deviceId.projectId}-{self.deviceId.deviceId}/shadow/name/state_1/get/accepted'
            with self.subTest():
                self.asyncloop.run_until_complete(self.client.subscribe(topic))
                self.assertEqual(self.client._topics[0], topic)
        except Exception as ex:
            self.asyncloop.run_until_complete(self.client.disconnect())
            logger.error(ex)
            self.assertTrue(False)

    def test_04_subscribe_without_listener(self):
        try:
            self.asyncloop.run_until_complete(self.client.loadContextCertificate(Provider.BOOTSTRAP))
            self.asyncloop.run_until_complete(self.client.loadContextConfiguration(Provider.BOOTSTRAP))
            self.asyncloop.run_until_complete(self.client.connect())
            topic = f'$aws/things/{self.deviceId.accountId}-{self.deviceId.projectId}-{self.deviceId.deviceId}/shadow/name/state_1/get/accepted'
            with self.subTest():
                self.asyncloop.run_until_complete(self.client.subscribe(topic))
                self.assertEqual(self.client._topics[0], topic)
            with self.subTest():
                self.asyncloop.run_until_complete(self.client.unsubscribe(topic))
                self.assertEqual(len(self.client._topics), 0)
        except Exception as ex:
            self.asyncloop.run_until_complete(self.client.disconnect())
            logger.error(ex)
            self.assertTrue(False)

    def test_05_subscribe_listener(self):
        try:
            self.asyncloop.run_until_complete(self.client.loadContextCertificate(Provider.BOOTSTRAP))
            self.asyncloop.run_until_complete(self.client.loadContextConfiguration(Provider.BOOTSTRAP))
            self.asyncloop.run_until_complete(self.client.connect())
            topic = f'$aws/things/{self.deviceId.accountId}-{self.deviceId.projectId}-{self.deviceId.deviceId}/shadow/name/state_1/get'

            def callback(context: NeukoTest, client, userdata, message: MQTTMessage):
                data = json.loads(message.payload)
                value = data['state']['reported']['attribute_1']
                context.assertEqual(value, 'high')

            self.asyncloop.run_until_complete(self.client.subscribe(f'{topic}/accepted', lambda client, userdata, message: callback(self, client, userdata, message)))
            self.asyncloop.run_until_complete(self.client.publish(topic, None))
            
        except Exception as ex:
            self.asyncloop.run_until_complete(self.client.disconnect())
            logger.error(ex)
            self.assertTrue(False)

    def test_06_fetch_all_telemetric_statenames(self):
        self.asyncloop.run_until_complete(self.client.loadContextCertificate(Provider.BOOTSTRAP))
        self.asyncloop.run_until_complete(self.client.loadContextConfiguration(Provider.BOOTSTRAP))
        self.asyncloop.run_until_complete(self.client.connect())
        names = self.asyncloop.run_until_complete(self.client.fetchAllTelemetricStateNames())
        self.assertEqual(len(names), 4)

    def test_07_pull_telemetric_state(self):
        self.asyncloop.run_until_complete(self.client.loadContextCertificate(Provider.BOOTSTRAP))
        self.asyncloop.run_until_complete(self.client.loadContextConfiguration(Provider.BOOTSTRAP))
        self.asyncloop.run_until_complete(self.client.connect())
        data = self.asyncloop.run_until_complete(self.client.pullTelemetricState('state_1'))
        self.assertEqual(data['state']['reported']['attribute_1'], 'high')

    def test_08_pull_nonexists_telemetric_state(self):
        self.asyncloop.run_until_complete(self.client.loadContextCertificate(Provider.BOOTSTRAP))
        self.asyncloop.run_until_complete(self.client.loadContextConfiguration(Provider.BOOTSTRAP))
        self.asyncloop.run_until_complete(self.client.connect())
        with self.assertRaises(Exception) as context:
            data = self.asyncloop.run_until_complete(self.client.pullTelemetricState('no_state_at_all'))
        self.assertTrue('NotFound' in str(context.exception))

    def test_09_push_telemetric_state(self):
        self.asyncloop.run_until_complete(self.client.loadContextCertificate(Provider.BOOTSTRAP))
        self.asyncloop.run_until_complete(self.client.loadContextConfiguration(Provider.BOOTSTRAP))
        self.asyncloop.run_until_complete(self.client.connect())
        value = random.random()
        data = self.asyncloop.run_until_complete(self.client.pushTelemetricState('state_2', {
            'state': {
                'reported': {
                    'attribute_1': {
                        'attribute_a': value
                    }
                }
            }
        }))
        self.assertEqual(data['state']['reported']['attribute_1']['attribute_a'], value)

    def test_10_push_timestream_storage(self):
        self.asyncloop.run_until_complete(self.client.loadContextCertificate(Provider.BOOTSTRAP))
        self.asyncloop.run_until_complete(self.client.loadContextConfiguration(Provider.BOOTSTRAP))
        self.asyncloop.run_until_complete(self.client.connect())
        value = random.random()
        try:
            self.asyncloop.run_until_complete(self.client.timestreamStorage('state_2', {
                'attribute_1': {
                    'attribute_a': value
                }
            }))
            self.assertTrue(True)
        except Exception as ex:
            self.asyncloop.run_until_complete(self.client.disconnect())
            logger.error(ex)
            self.assertTrue(False)

    def test_11_listen_when_telemetric_changed(self):
        try:
            self.outsideFlag = False
            self.asyncloop.run_until_complete(self.client.loadContextCertificate(Provider.BOOTSTRAP))
            self.asyncloop.run_until_complete(self.client.loadContextConfiguration(Provider.BOOTSTRAP))
            self.asyncloop.run_until_complete(self.client.connect())
            value = random.random()

            def callback(myContext: NeukoTest, data: UpdateDelta):
                logger.debug(data)
                for i in range(4):
                    logger.debug(f'Simulating blocking operation... {i}')
                    time.sleep(1)
                myContext.outsideFlag = True
                logger.debug(f'payload = {data.delta["attribute_1"]["attribute_a"]}')
                logger.debug(f'value = {value}')
                myContext.assertEqual(data.delta['attribute_1']['attribute_a'], value)

            self.asyncloop.run_until_complete(self.client.onTelemetricStateChangedRequest(self, callback))
            self.asyncloop.run_until_complete(asyncio.sleep(3))
            self.asyncloop.run_until_complete(self.client.pushTelemetricState('state_2', {
                'state': {
                    'desired': {
                        'attribute_1': {
                            'attribute_a': value
                        }
                    }
                }
            }))

            async def checkForResponse():
                logger.debug("Simulating long running application")
                for i in range(10):
                    if self.outsideFlag:
                        logger.debug("Response has been fired and executed")
                        return True
                    else:
                        logger.debug("Response is not completed yet")
                        await asyncio.sleep(1)
                raise Exception('TimeoutError')

            self.asyncloop.run_until_complete(checkForResponse())
        except Exception as ex:
            self.asyncloop.run_until_complete(self.client.disconnect())
            logger.error(ex)
            self.assertTrue(False)
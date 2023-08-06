import unittest
import configparser
import shutil
import os
from dotenv import load_dotenv
from src.neuko.utility.logger import Logger
from src.neuko.device.identifierStore import DeviceIdentifierStore
from src.neuko.device.deviceManagement import DeviceManagement

load_dotenv()
logger = Logger("DeviceManagementTest").set()
ACCOUNT_ID  = 'accountId'
PROJECT_ID  = 'projectId'
SCHEMA_ID   = 'schemaId'
DEVICE_ID   = 'deviceId'

class DeviceIdentifierStoreRTestObject(DeviceIdentifierStore):
    def getAccountId(self) -> str:
        return 'fromoverridenmethod'

    def getProjectId(self) -> str:
        return 'fromoverridenmethod'

    def getDeviceSchemaId(self) -> str:
        return 'fromoverridenmethod'

    def getDeviceId(self) -> str:
        return 'fromoverridenmethod'

class DeviceManagementTest(unittest.TestCase):

    def setUp(self) -> None:
        logger.debug("Setup Test")
        self._deviceConfig = None

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

    def _readConfigDevice(self, keyname: str) -> None:
        try:
            return self._deviceConfig[keyname]
        except KeyError:
            return None
        except Exception as ex:
            logger.error(ex)
            raise Exception(ex)

    def test_01_get_device_identifier_from_parameter(self):
        store = DeviceIdentifierStoreRTestObject("accid", "proid", "schid", "devid")
        manager = DeviceManagement(store)
        deviceId = manager.getDeviceIdentifier()
        with self.subTest():
            self.assertEqual(deviceId.accountId, 'accid')
        with self.subTest():
            self.assertEqual(deviceId.projectId, 'proid')
        with self.subTest():
            self.assertEqual(deviceId.deviceSchemaId, 'schid')
        with self.subTest():
            self.assertEqual(deviceId.deviceId, 'devid')

    def test_02_get_device_identifier_from_config_file(self):
        store = DeviceIdentifierStoreRTestObject()
        manager = DeviceManagement(store)
        deviceId = manager.getDeviceIdentifier()
        config = configparser.ConfigParser()
        config.read('config.ini')
        self._deviceConfig = config['device']
        accid = self._readConfigDevice(ACCOUNT_ID)
        proid = self._readConfigDevice(PROJECT_ID)
        schid = self._readConfigDevice(SCHEMA_ID)
        devid = self._readConfigDevice(DEVICE_ID)
        with self.subTest():
            self.assertEqual(deviceId.accountId, accid)
        with self.subTest():
            self.assertEqual(deviceId.projectId, proid)
        with self.subTest():
            self.assertEqual(deviceId.deviceSchemaId, schid)
        with self.subTest():
            self.assertEqual(deviceId.deviceId, devid)

    def test_03_get_device_schema_id(self):
        store = DeviceIdentifierStoreRTestObject()
        manager = DeviceManagement(store)
        id = manager.getDeviceSchemaId()
        self.assertEqual(id, 'fromoverridenmethod')

    # This test always has to be the last test since we need to delete config.ini file
    # for it to immitate "no config file situation"
    def test_04_get_device_identifier_from_overwritten_methos(self):
        os.remove("./config.ini")
        store = DeviceIdentifierStoreRTestObject()
        manager = DeviceManagement(store)
        deviceId = manager.getDeviceIdentifier()
        with self.subTest():
            self.assertEqual(deviceId.accountId, 'fromoverridenmethod')
        with self.subTest():
            self.assertEqual(deviceId.projectId, 'fromoverridenmethod')
        with self.subTest():
            self.assertEqual(deviceId.deviceSchemaId, 'fromoverridenmethod')
        with self.subTest():
            self.assertEqual(deviceId.deviceId, 'fromoverridenmethod')

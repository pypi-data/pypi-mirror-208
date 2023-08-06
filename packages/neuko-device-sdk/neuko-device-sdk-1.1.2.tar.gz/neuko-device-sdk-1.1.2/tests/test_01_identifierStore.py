import unittest
import configparser
import shutil
import os
from dotenv import load_dotenv
from src.neuko.utility.logger import Logger
from src.neuko.device.identifierStore import DeviceIdentifierStore

load_dotenv()
logger = Logger("DeviceIdentifierStoreTest").set()
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

class DeviceIdentifierStoreTest(unittest.TestCase):

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

    def setUp(self) -> None:
        logger.debug('Setup Test')
        self._deviceConfig = None

    def _readConfigDevice(self, keyname: str) -> None:
        try:
            return self._deviceConfig[keyname]
        except KeyError:
            return None
        except Exception as ex:
            logger.error(ex)
            raise Exception(ex)

    def test_01_no_instance_resolve_device_identifier_defaut_location(self):
        obj = DeviceIdentifierStore()
        deviceId = obj.resolveDeviceIdentifier()
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

    def test_02_no_instance_resolve_device_identifier_test_location(self):
        obj2 = DeviceIdentifierStore()
        deviceId = obj2.resolveDeviceIdentifier('./tests/config.ini')
        with self.subTest():
            self.assertEqual(deviceId.accountId, 'acc_test')
        with self.subTest():
            self.assertEqual(deviceId.projectId, 'prj_test')
        with self.subTest():
            self.assertEqual(deviceId.deviceSchemaId, 'sch_test')
        with self.subTest():
            self.assertEqual(deviceId.deviceId, 'dev_test')

    def test_03_no_instance_resolve_device_identifier_non_exists_location(self):
        obj3 = DeviceIdentifierStore()
        with self.assertRaises(Exception) as context:
           deviceId = obj3.resolveDeviceIdentifier('./tests/confignovalue1.ini')
        self.assertTrue('Please override the getAccountId method to and return the value' in str(context.exception))

    def test_04_with_instance_resolve_device_identifier_defaut_location(self):
        obj4 = DeviceIdentifierStoreRTestObject()
        deviceId = obj4.resolveDeviceIdentifier()
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

    def test_05_instance_params_has_higher_priority(self):
        obj2 = DeviceIdentifierStore("accid", "proid", "schid", "devid")
        deviceId = obj2.resolveDeviceIdentifier()
        with self.subTest():
            self.assertEqual(deviceId.accountId, 'accid')
        with self.subTest():
            self.assertEqual(deviceId.projectId, 'proid')
        with self.subTest():
            self.assertEqual(deviceId.deviceSchemaId, 'schid')
        with self.subTest():
            self.assertEqual(deviceId.deviceId, 'devid')

    def test_05_instance_params_value_from_method(self):
        obj2 = DeviceIdentifierStore("accid", "proid", "schid", "devid")
        # deviceId = obj2.resolveDeviceIdentifier()
        with self.subTest():
            self.assertEqual(obj2.getAccountId(), 'accid')
        with self.subTest():
            self.assertEqual(obj2.getProjectId(), 'proid')
        with self.subTest():
            self.assertEqual(obj2.getDeviceSchemaId(), 'schid')
        with self.subTest():
            self.assertEqual(obj2.getDeviceId(), 'devid')
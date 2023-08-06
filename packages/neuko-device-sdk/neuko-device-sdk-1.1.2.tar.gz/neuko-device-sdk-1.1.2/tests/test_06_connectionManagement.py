import unittest
import asyncio
import json
from os.path import exists
from src.neuko.iot.model import Provider
from src.neuko.device.model import DeviceIdentifier
from src.neuko.connection.connectionStore import ConnectionStore
from src.neuko.connection.connectionManagement import ConnectionManagement
from src.neuko.connection.model import Configuration

rawdata = {
    "tier": "testTierValue",
    "localConnection": {
        "ownershipToken": "testOwnershipTokenValue",
    },
    "connection": {
        "provider": Provider.NEUKO,
        "protocols": {
            "mqtt": {
                "endpoint": "testendpoint.neukolabs.com",
                "port": 443,
                "options": {
                    "rejectUnauthorized": False,
                    "ALPNProtocols": ["x-amzn-mqtt-ca"]
                }
            },
            "http": {
                "endpoint": "testendpoint.neukolabs.com",
                "port": 443,
                "options": {
                    "keepAlive": True,
                    "rejectUnauthorized": False,
                    "ALPNProtocols": ["x-amzn-http-ca"]
                }
            }
        }
    }
}

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
        return exists("./tests/connectionSettingsTestValue.json")

class ConnectionManagementTest(unittest.TestCase):

    def setUp(self):
        self.my_loop = asyncio.new_event_loop()
        self.addCleanup(self.my_loop.close)

    def test_01_save_perpetual_settings(self):
        deviceId = DeviceIdentifier("testAccountId", "testProjectId", "testSchemaId", "testDeviceId")
        store = ConnectionStoreTest()
        manager = ConnectionManagement(store)
        self.my_loop.run_until_complete(manager.savePerpetualConnectionConfiguration(deviceId, rawdata))
        fd = open("./tests/connectionSettingsTestValueSaveTest.json", mode="r")
        raw = json.load(fd)
        fd.close()
        j = json.loads(raw)
        data = Configuration(**j)
        with self.subTest():
            self.assertEqual(data["tier"], "testTierValue")
        with self.subTest():
            self.assertEqual(data["localConnection"]["ownershipToken"], "testOwnershipTokenValue")
        with self.subTest():
            self.assertEqual(data["connection"]["provider"], Provider.NEUKO)
        with self.subTest():
            self.assertEqual(data["connection"]["protocols"]["mqtt"]["endpoint"], "testendpoint.neukolabs.com")
        with self.subTest():
            self.assertEqual(data["connection"]["protocols"]["mqtt"]["port"], 443)
        with self.subTest():
            self.assertEqual(data["connection"]["protocols"]["mqtt"]["options"]["rejectUnauthorized"], False)
        with self.subTest():
            self.assertEqual(data["connection"]["protocols"]["mqtt"]["options"]["ALPNProtocols"], ["x-amzn-mqtt-ca"])
        with self.subTest():
            self.assertEqual(data["connection"]["protocols"]["http"]["endpoint"], "testendpoint.neukolabs.com")
        with self.subTest():
            self.assertEqual(data["connection"]["protocols"]["http"]["port"], 443)
        with self.subTest():
            self.assertEqual(data["connection"]["protocols"]["http"]["options"]["keepAlive"], True)
        with self.subTest():
            self.assertEqual(data["connection"]["protocols"]["http"]["options"]["rejectUnauthorized"], False)
        with self.subTest():
            self.assertEqual(data["connection"]["protocols"]["http"]["options"]["ALPNProtocols"], ["x-amzn-http-ca"])

    def test_02_get_and_load_perpetual_settings(self):
        deviceId = DeviceIdentifier("testAccountId", "testProjectId", "testSchemaId", "testDeviceId")
        store = ConnectionStoreTest()
        manager = ConnectionManagement(store)
        data = self.my_loop.run_until_complete(manager.getPerpetualConnectionConfiguration(deviceId))
        with self.subTest():
            self.assertEqual(data["tier"], "testTierValue")
        with self.subTest():
            self.assertEqual(data["localConnection"]["ownershipToken"], "testOwnershipTokenValue")
        with self.subTest():
            self.assertEqual(data["connection"]["provider"], Provider.NEUKO)
        with self.subTest():
            self.assertEqual(data["connection"]["protocols"]["mqtt"]["endpoint"], "testendpoint.neukolabs.com")
        with self.subTest():
            self.assertEqual(data["connection"]["protocols"]["mqtt"]["port"], 443)
        with self.subTest():
            self.assertEqual(data["connection"]["protocols"]["mqtt"]["options"]["rejectUnauthorized"], False)
        with self.subTest():
            self.assertEqual(data["connection"]["protocols"]["mqtt"]["options"]["ALPNProtocols"], ["x-amzn-mqtt-ca"])
        with self.subTest():
            self.assertEqual(data["connection"]["protocols"]["http"]["endpoint"], "testendpoint.neukolabs.com")
        with self.subTest():
            self.assertEqual(data["connection"]["protocols"]["http"]["port"], 443)
        with self.subTest():
            self.assertEqual(data["connection"]["protocols"]["http"]["options"]["keepAlive"], True)
        with self.subTest():
            self.assertEqual(data["connection"]["protocols"]["http"]["options"]["rejectUnauthorized"], False)
        with self.subTest():
            self.assertEqual(data["connection"]["protocols"]["http"]["options"]["ALPNProtocols"], ["x-amzn-http-ca"])

    def test_03_validate_configuration_settings_file_exists(self):
        deviceId = DeviceIdentifier("testAccountId", "testProjectId", "testSchemaId", "testDeviceId")
        store = ConnectionStoreTest()
        manager = ConnectionManagement(store)
        self.assertTrue(self.my_loop.run_until_complete(manager.checkIfConfigurationSaved(deviceId)))

    def test_04_connected_to_internet(self):
        deviceId = DeviceIdentifier("testAccountId", "testProjectId", "testSchemaId", "testDeviceId")
        store = ConnectionStoreTest()
        manager = ConnectionManagement(store)
        self.assertTrue(self.my_loop.run_until_complete(manager.checkIfConnectedToInternet()))  


if __name__ == '__main__':
    unittest.main()
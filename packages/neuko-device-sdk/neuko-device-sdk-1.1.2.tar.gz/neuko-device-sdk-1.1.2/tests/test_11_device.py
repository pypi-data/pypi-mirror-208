from genericpath import exists
from multiprocessing.connection import wait
import unittest
import asyncio
import os
import configparser
import json
import uuid
import shutil
import random
from os.path import exists
from typing import Union
from src.neuko.device.telemetricState import TelemetricStateType
from src.neuko.utility.utils import get_project_root
from src.neuko.utility.logger import Logger
from src.neuko.device.device import Device, DeviceIdentifier, DeviceState
from src.neuko.device.identifierStore import DeviceIdentifierStore
from src.neuko.connection.certificateStore import CertificateStore
from src.neuko.connection.connectionStore import ConnectionStore
from src.neuko.device.model import TelemetricStateChangeParameter
from src.neuko.iot.bootstrap import BootstrapClient
from src.neuko.iot.neuko import NeukoClient
from src.neuko.iot.model import Provider, UpdateDelta
from src.neuko.lifecycle.connectionStateMachine import ConnectionStateNachineLifecycle

logger = Logger("DeviceTest").set()
config = configparser.ConfigParser()
CONFIG_PATHNAME = 'unittestconfig.ini'
config.read(CONFIG_PATHNAME)

class DeviceIdentifierStoreTestObject(DeviceIdentifierStore):
    def getAccountId(self) -> str:
        return 'neuko'

    def getProjectId(self) -> str:
        return 'device-sdk'

    def getDeviceSchemaId(self) -> str:
        return 'schema'

    def getDeviceId(self) -> str:
        return 'test'

class CertificateStoreTestObject(CertificateStore):

    rootdir = '../security/device-test'
    schemaId = '53574467eedece26473ab7fa19833dda31147f8ccc5c756c084fbbe204e61639'
    cacert = f'{rootdir}/AmazonRootCA1.pem'
    cert = f'{rootdir}/{schemaId}-certificate.pem.crt'
    privateKey = f'{rootdir}/{schemaId}-private.pem.key'

    async def getBootstrapCertificateAuthority(self, deviceIdentifier: DeviceIdentifier) -> str:
        return self.cacert

    async def getBootstrapChainCertificate(self, deviceIdentifier: DeviceIdentifier) -> str:
        return self.cert

    async def getBootstrapPrivateKey(self, deviceIdentifier: DeviceIdentifier) -> str:
        return self.privateKey

    async def getPerpetualCertificateAuthority(self, deviceIdentifier: DeviceIdentifier) -> str:
        return self.cacert

    async def getPerpetualChainCertificate(self, deviceIdentifier: DeviceIdentifier) -> str:
        return self.cert

    async def getPerpetualPrivateKey(self, deviceIdentifier: DeviceIdentifier) -> str:
        return self.privateKey

    async def savePerpetualCertificateAuthority(self, deviceIdentifier: DeviceIdentifier, certificate: str) -> None:
        return None

    async def savePerpetualChainCertificate(self, deviceIdentifier: DeviceIdentifier, certificate: str) -> None:
        return None

    async def savePerpetualPrivateKey(self, deviceIdentifier: DeviceIdentifier, certificate: str) -> None:
        return None

class ConnectionStoreTest(ConnectionStore):
    async def getPerpetualConnectionSettings(self, deviceIdentifier: DeviceIdentifier) -> str:
        fd = open("./tests/deviceTestConnectionSettings.json", mode="r")
        raw = json.load(fd)
        fd.close()
        return raw

    async def savePerpetualConnectionSettings(self, deviceIdentifier: DeviceIdentifier, settings: str) -> bool:
        fd = open("./tests/connection2SettingsTestValueSaveTest.json", mode="w")
        json.dump(settings, fd)
        fd.close()
        return True

    async def deletePerpetualConnectionSettings(self, deviceIdentifier: DeviceIdentifier) -> bool:
        return True

    async def isPerpetualConnectionSettingsExists(self, deviceIdentifier: DeviceIdentifier) -> bool:
        return exists("./tests/deviceTestConnectionSettings.json")

class DeviceTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        # backup before test
        shutil.copy("./config.ini", "config-backup-before-test.ini")
        # copy test config
        # shutil.copy("./tests/config.ini", "./config.ini")
        os.remove("./config.ini")

    @classmethod
    def tearDownClass(cls) -> None:
        # restore
        shutil.copy("./config-backup-before-test.ini", "config.ini")
        # remove backup file
        os.remove("./config-backup-before-test.ini")

    def _readConfigDefault(self, keyname: str, default = None) -> None:
        try:
            return self._defaultConfig[keyname]
        except KeyError:
            return default
        except Exception as ex:
            logger.error(ex)
            raise Exception(ex)

    def setUp(self):
        logger.debug("Test Start")
        self.outsideFlag = False
        self.asyncloop = asyncio.new_event_loop()
        if 'default' in config:
            self._defaultConfig =  config['default']

        self._endpoint = self._readConfigDefault('endpoint', 'neuko.io')
        self._port = self._readConfigDefault('port', 443)
        self._region = self._readConfigDefault('region', 'apse-1')

    # def test_01_start(self):
    #     device = Device()
    #     self.asyncloop.run_until_complete(device.start_async())
    #     logger.debug(json.dumps(device._localTelemetricState.states))
    #     logger.debug(json.dumps(device._features))
    #     waitTime = 0
    #     timeoutTime = 5
    #     # 15s timeout
    #     while waitTime < timeoutTime:
    #         logger.debug(f'Test end in {timeoutTime - waitTime}')
    #         waitTime += 1 
    #         self.asyncloop.run_until_complete(asyncio.sleep(1))
            
    #     self.assertTrue(True)

    def test_02_startthreadsafe_and_stop_after_5s(self):
        device = Device(deviceIdentifierStore=DeviceIdentifierStoreTestObject(), certificateStore=CertificateStoreTestObject(), connectionStore=ConnectionStoreTest())
        device.start_threadsafe()
        waitTime = 0
        timeoutTime = 5
        while waitTime < timeoutTime:
            logger.debug(f'Test end in {timeoutTime - waitTime}')
            waitTime += 1 
            self.asyncloop.run_until_complete(asyncio.sleep(1))

        
        self.asyncloop.run_until_complete(device.stop())
        logger.debug(device._localTelemetricState.allStates)
        self.assertTrue(True)

    def test_03_startthreadsafe_and_stop_after_20s(self):
        device = Device(deviceIdentifierStore=DeviceIdentifierStoreTestObject(), certificateStore=CertificateStoreTestObject(), connectionStore=ConnectionStoreTest())
        device.start_threadsafe()
        waitTime = 0
        timeoutTime = 20
        while waitTime < timeoutTime:
            logger.debug(f'Test end in {timeoutTime - waitTime}')
            waitTime += 1 
            self.asyncloop.run_until_complete(asyncio.sleep(1))

        with self.subTest():
            self.assertEqual(device.state, DeviceState.READY)
        with self.subTest():
            self.asyncloop.run_until_complete(device.stop())
            self.assertEqual(device.state, DeviceState.DISCONNECTED)

    def test_04_sync_useEffect(self):
        
        def callback(data: TelemetricStateChangeParameter):
            logger.info(f'masuk callback: {data}')
            return True

        device = Device(deviceIdentifierStore=DeviceIdentifierStoreTestObject(), certificateStore=CertificateStoreTestObject(), connectionStore=ConnectionStoreTest())
        device.useEffect(self, callback, 'state_a', 'att.deep')
        device.start_threadsafe()
        waitTime = 0
        timeoutTime = 30
        value = random.random()
        while waitTime < timeoutTime:
            logger.debug(f'Test end in {timeoutTime - waitTime}')
            waitTime += 1 
            if waitTime == 20:
                self.asyncloop.run_until_complete(device._deviceClient.publish(
                    '$aws/things/neuko-device-sdk-test/shadow/name/state_a/update', 
                    json.dumps({
                        'state': {
                            'desired': {
                                'att': {
                                    'deep': value
                                }
                            }
                        }
                    })
                ))
                
            self.asyncloop.run_until_complete(asyncio.sleep(1))

        self.asyncloop.run_until_complete(device.stop())
        self.assertTrue(True)

    def test_05_listen_to_device_lifecycle(self):

        self.INTERNET_CONNECTED: bool = False
        self.PERPETUAL_CONNECTED: bool = False
        self.TELEMETRIC_STATE_INITED: bool = False
        self.TELEMETRIC_STATE_SYNCED: bool = False
        self.GOODBYE: bool = False
        
        def callback(data: TelemetricStateChangeParameter):
            logger.info(f'masuk callback: {data.stateName}::{data.context}')
            if data.stateName == f'DEVICE_LIFECYCLE_{ConnectionStateNachineLifecycle.INTERNET_CONNECTED}': 
                data.context.INTERNET_CONNECTED = True

            if data.stateName == f'DEVICE_LIFECYCLE_{ConnectionStateNachineLifecycle.PERPETUAL_CONNECTED}': 
                data.context.PERPETUAL_CONNECTED = True

            if data.stateName == f'DEVICE_LIFECYCLE_{ConnectionStateNachineLifecycle.TELEMETRIC_STATE_INITED}': 
                data.context.TELEMETRIC_STATE_INITED = True

            if data.stateName == f'DEVICE_LIFECYCLE_{ConnectionStateNachineLifecycle.TELEMETRIC_STATE_SYNCED}': 
                data.context.TELEMETRIC_STATE_SYNCED = True

            if data.stateName == f'DEVICE_LIFECYCLE_{ConnectionStateNachineLifecycle.GOODBYE}': 
                data.context.GOODBYE = True

            return True

        device = Device(deviceIdentifierStore=DeviceIdentifierStoreTestObject(), certificateStore=CertificateStoreTestObject(), connectionStore=ConnectionStoreTest())
        device.listenLifecycleState(self, callback, ConnectionStateNachineLifecycle.INTERNET_CONNECTED)
        device.listenLifecycleState(self, callback, ConnectionStateNachineLifecycle.PERPETUAL_CONNECTED)
        device.listenLifecycleState(self, callback, ConnectionStateNachineLifecycle.TELEMETRIC_STATE_INITED)
        device.listenLifecycleState(self, callback, ConnectionStateNachineLifecycle.TELEMETRIC_STATE_SYNCED)
        device.listenLifecycleState(self, callback, ConnectionStateNachineLifecycle.GOODBYE)
        device.start_threadsafe()
        waitTime = 0
        timeoutTime = 20
        value = uuid.uuid4().hex
        while waitTime < timeoutTime:
            waitTime += 1
            self.asyncloop.run_until_complete(asyncio.sleep(1))

        self.asyncloop.run_until_complete(device.stop())

        with self.subTest():
            self.assertEqual(self.INTERNET_CONNECTED, True)
        with self.subTest():
            self.assertEqual(self.PERPETUAL_CONNECTED, True)
        with self.subTest():
            self.assertEqual(self.TELEMETRIC_STATE_INITED, True)
        with self.subTest():
            self.assertEqual(self.TELEMETRIC_STATE_SYNCED, True)
        with self.subTest():
            self.assertEqual(self.GOODBYE, True)
    
    def test_06_sync_useEffect_state_of_array(self):
        
        def callback(data: TelemetricStateChangeParameter):
            logger.info(f'masuk callback: {data.value}')
            return True

        device = Device(deviceIdentifierStore=DeviceIdentifierStoreTestObject(), certificateStore=CertificateStoreTestObject(), connectionStore=ConnectionStoreTest())
        device.useEffect(self, callback, 'state_c', 'att.upward')
        device.start_threadsafe()
        waitTime = 0
        timeoutTime = 30
        value = random.random()

        newvalue = [
            {
                "a": 321,
                "b": {
                    "c": value
                }
            },
            {
                "a": 222,
                "b": {
                    "c": random.random()
                }
            }
        ]
        while waitTime < timeoutTime:
            logger.debug(f'Test end in {timeoutTime - waitTime}')
            waitTime += 1 
            if waitTime == 20:
                self.asyncloop.run_until_complete(device._deviceClient.publish(
                    '$aws/things/neuko-device-sdk-test/shadow/name/state_c/update', 
                    json.dumps({
                        'state': {
                            'desired': {
                                'att': {
                                    'upward': newvalue
                                }
                            }
                        }
                    })
                ))
                
            self.asyncloop.run_until_complete(asyncio.sleep(1))

        self.asyncloop.run_until_complete(device.stop())
        self.assertTrue(True)

    def test_07_get_current_reported_value(self):
        
        def callback(data: TelemetricStateChangeParameter):
            logger.info(f'masuk callback: {data}')
            return True

        device = Device(deviceIdentifierStore=DeviceIdentifierStoreTestObject(), certificateStore=CertificateStoreTestObject(), connectionStore=ConnectionStoreTest())
        device.useEffect(self, callback, 'state_a', 'att.deep')
        device.start_threadsafe()
        waitTime = 0
        timeoutTime = 30
        value = random.random()
        while waitTime < timeoutTime:
            logger.debug(f'Test end in {timeoutTime - waitTime}')
            waitTime += 1 
            if waitTime == 20:
                self.asyncloop.run_until_complete(device._deviceClient.publish(
                    '$aws/things/neuko-device-sdk-test/shadow/name/state_a/update', 
                    json.dumps({
                        'state': {
                            'desired': {
                                'att': {
                                    'deep': value
                                }
                            }
                        }
                    })
                ))
                
            self.asyncloop.run_until_complete(asyncio.sleep(1))

        stateValue = device.getLocalTelemetricStateValue("state_a", TelemetricStateType.Reported)
        self.asyncloop.run_until_complete(device.stop())
        self.assertEqual(stateValue, {
            "att": {
                "deep": value,
                "deep2": False
            }
        })

    def test_08_report_value(self):
        
        def callback(data: TelemetricStateChangeParameter):
            logger.info(f'masuk callback: {data}')
            return True

        device = Device(deviceIdentifierStore=DeviceIdentifierStoreTestObject(), certificateStore=CertificateStoreTestObject(), connectionStore=ConnectionStoreTest())
        device.useEffect(self, callback, 'state_a', 'att.deep')
        device.start_threadsafe()
        waitTime = 0
        timeoutTime = 30
        value = random.random()
        while waitTime < timeoutTime:
            logger.debug(f'Test end in {timeoutTime - waitTime}')
            waitTime += 1 
            # if waitTime == 20:
            #     self.asyncloop.run_until_complete(device._deviceClient.publish(
            #         '$aws/things/neuko-device-sdk-test/shadow/name/state_a/update', 
            #         json.dumps({
            #             'state': {
            #                 'desired': {
            #                     'att': {
            #                         'deep': value
            #                     }
            #                 }
            #             }
            #         })
            #     ))
                
            self.asyncloop.run_until_complete(asyncio.sleep(1))
        self.asyncloop.run_until_complete(asyncio.sleep(1))
        self.asyncloop.run_until_complete(device.updateTelemetricState("state_a", {
            "att": {
                "deep": value
            }
        }, False))
        stateValue = device.getLocalTelemetricStateValue("state_a", TelemetricStateType.Reported)
        self.asyncloop.run_until_complete(device.stop())
        self.assertEqual(stateValue, {
            "att": {
                "deep": value,
                "deep2": False
            }
        })

    def test_09_force_update_virtual_twin(self):
        
        def callback(data: TelemetricStateChangeParameter):
            logger.info(f'masuk callback: {data}')
            return True

        device = Device(deviceIdentifierStore=DeviceIdentifierStoreTestObject(), certificateStore=CertificateStoreTestObject(), connectionStore=ConnectionStoreTest())
        device.useEffect(self, callback, 'state_a', 'att.deep')
        device.start_threadsafe()
        waitTime = 0
        timeoutTime = 30
        value = random.random()

        while waitTime < timeoutTime:
            logger.debug(f'Test end in {timeoutTime - waitTime}')
            waitTime += 1  
            self.asyncloop.run_until_complete(asyncio.sleep(1))

        self.asyncloop.run_until_complete(asyncio.sleep(1))
        self.asyncloop.run_until_complete(device.updateTelemetricState("state_a", {
            "att": {
                "deep": value
            }
        }, True))

        # # lets wait for 2 seconds
        # waitTime = 0
        # while waitTime < 2:
        #     logger.debug(f'Wait end in {timeoutTime - waitTime}')
        #     waitTime += 1   
        #     self.asyncloop.run_until_complete(asyncio.sleep(1))

        # let pull the data
        # self.asyncloop.run_until_complete(device._deviceClient.pullTelemetricState('state_a'))
        stateValue = device.getLocalTelemetricStateValue("state_a", TelemetricStateType.Reported)
        self.asyncloop.run_until_complete(device.stop())
        logger.debug(f'Random value = {value}')
        self.assertEqual(stateValue, {
            "att": {
                "deep": value,
                "deep2": False
            }
        })
    
    def test_10_get_internal_configuration(self):
        
        def callback(data: TelemetricStateChangeParameter):
            logger.info(f'masuk callback: {data}')
            return True

        device = Device(deviceIdentifierStore=DeviceIdentifierStoreTestObject(), certificateStore=CertificateStoreTestObject(), connectionStore=ConnectionStoreTest())
        device.useEffect(self, callback, 'internal_configuration')
        device.start_threadsafe()
        waitTime = 0
        timeoutTime = 15
        value = uuid.uuid4().hex
        while waitTime < timeoutTime:
            logger.debug(f'Test end in {timeoutTime - waitTime}')
            waitTime += 1
            self.asyncloop.run_until_complete(asyncio.sleep(1))

        stateValue = device.getLocalTelemetricStateValue("internal_configuration", TelemetricStateType.Reported)
        self.asyncloop.run_until_complete(device.stop())
        logger.debug(stateValue)
        with self.subTest():
            self.assertEqual(stateValue["features"]["interval"]["version"], 1)
        with self.subTest():
            self.assertEqual(stateValue["features"]["interval"]["value"], 60000)
        with self.subTest():
            self.assertEqual(stateValue["features"]["timestreamStorage"]["version"], 1)
        with self.subTest():
            self.assertEqual(stateValue["features"]["timestreamStorage"]["value"], ["*"])
        with self.subTest():
            self.assertEqual(stateValue["features"]["backupStorage"]["version"], 1)
        with self.subTest():
            self.assertEqual(stateValue["features"]["backupStorage"]["value"], [])
        with self.subTest():
            self.assertEqual(stateValue["features"]["relay"]["version"], 1)
        with self.subTest():
            self.assertEqual(stateValue["features"]["relay"]["value"], [])

    
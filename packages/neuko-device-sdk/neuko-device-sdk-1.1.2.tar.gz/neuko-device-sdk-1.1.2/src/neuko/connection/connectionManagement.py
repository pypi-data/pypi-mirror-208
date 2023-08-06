import json
import os
import configparser
from ..utility.logger import Logger
from .connectionStore import ConnectionStore
from ..device.model import DeviceIdentifier
from .model import Configuration
from ..iot.model import Provider

logger = Logger("ConnectionManagement").set()
config = configparser.ConfigParser()
CONFIG_PATHNAME = 'config.ini'

class ConnectionManagement:

    def __init__(self, store: ConnectionStore) -> None:
        self._store = store
        self._defaultConfig = {}
        
        try:
            config.read(CONFIG_PATHNAME)
            if 'default' in config:
                logger.debug(f'__init__: Found "default" in {CONFIG_PATHNAME}')
                self._defaultConfig =  config['default']
        except:
            logger.debug(f'__init__: Cannot find "default" {CONFIG_PATHNAME}')
            self._defaultConfig = {}

        self._endpoint = self._readConfigDefault('endpoint', 'neuko.io')
        self._port = self._readConfigDefault('port', 443)
        self._region = self._readConfigDefault('region', 'apse-1')

    def _readConfigDefault(self, keyname: str, default = None) -> None:
        """
        If the keyname is in the default config, return the value, otherwise try to read it from the
        environment variable, otherwise return the default value
        
        :param keyname: The name of the key to read from the config file
        :type keyname: str
        :param default: The default value to return if the key is not found in the config file or
        environment variable
        :return: The value of the keyname in the defaultConfig dictionary.
        """
        try:
            return self._defaultConfig[keyname]
        except KeyError:
            return self._readConfigFromEnvVar(keyname, default)
        except Exception as ex:
            logger.error(ex)
            return default

    def _readConfigFromEnvVar(self, keyname: str, default = None):
        """
        Read config from the environment variable, otherwise return the default value
        
        :param keyname: The name of the parameter to read from the environment variable
        :type keyname: str
        :param default: The default value to return if the environment variable is not set
        :return: The value of the environment variable.
        """
        try:
            logger.debug(f'_readConfigFromEnvVar: Read from environment variable')
            if (keyname == "endpoint"):
                return os.getenv("NEUKO_BOOT_ENDPOINT", default)
            elif (keyname == "port"):
                return os.getenv("NEUKO_BOOT_PORT", default)
            elif (keyname == "region"):
                return os.getenv("NEUKO_BOOT_REGION", default)
            else:
                return default
        except Exception as ex:
            logger.error(ex)
            return default

    @property
    def store(self):
        """Internal property - store"""
        return self._store

    @store.setter
    def store(self, store: ConnectionStore):
        self._store = store

    @store.getter
    def store(self):
        return self._store

    def getBootstrapConnectionConfiguration(self):
        j = {
            "tier": None,
            "localConnection": {
                "ownershipToken": None,
            },
            "connection": {
                "provider": Provider.BOOTSTRAP,
                "protocols": {
                    "mqtt": {
                        "endpoint": f"bootstrap.{self._region}.{self._endpoint}",
                        "port": int(self._port),
                        "options": {
                            "rejectUnauthorized": False,
                            "ALPNProtocols": ["x-amzn-mqtt-ca"]
                        }
                    },
                    "http": {
                        "endpoint": f"bootstrap.{self._region}.{self._endpoint}",
                        "port": int(self._port),
                        "options": {
                            "keepAlive": True,
                            "rejectUnauthorized": False,
                            "ALPNProtocols": ["x-amzn-http-ca"]
                        }
                    }
                }
            }
        }
        return Configuration(**j)

    async def getPerpetualConnectionConfiguration(self, deviceIdentifier: DeviceIdentifier) -> Configuration:
        try:
            raw = await self._store.getPerpetualConnectionSettings(deviceIdentifier)
            j = json.loads(raw)
            # logger.debug(Configuration(**j))
            return Configuration(**j)
        except:
            logger.error("Error fetching perpetual configuration file")
            raise Exception("OperationError")

    async def savePerpetualConnectionConfiguration(self, deviceIdentifier: DeviceIdentifier, settings: Configuration) -> bool:
        try:
            res = await self._store.savePerpetualConnectionSettings(deviceIdentifier, json.dumps(settings, indent=4))
            if res:
                return True
            else:
                raise Exception("OperationError")
        except:
            logger.error("Error saving perpetual configuration file")
            raise Exception("OperationError")

    async def checkIfConfigurationSaved(self, deviceIdentifier: DeviceIdentifier) -> bool:
        try:
            res = await self._store.isPerpetualConnectionSettingsExists(deviceIdentifier)
            if res:
                logger.debug(f'checkIfConfigurationSaved: Perpetual settings found')
                return True
            else:
                logger.debug(f'checkIfConfigurationSaved: Perpetual settings doesnt exits')
                return False
        except:
            logger.error("Error saving perpetual configuration file")
            raise Exception("OperationError")

    async def checkIfConnectedToInternet(self) -> bool:
        try:
            res = await self._store.isConnectedToInternet()
            if res:
                return True
            else:
                return False
        except:
            logger.error("Error saving perpetual configuration file")
            raise Exception("OperationError")
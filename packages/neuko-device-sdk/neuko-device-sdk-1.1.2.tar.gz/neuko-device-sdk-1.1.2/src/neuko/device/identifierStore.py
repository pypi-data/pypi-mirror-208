import configparser
from abc import ABC, abstractmethod

from ..utility.logger import Logger
from .model import DeviceIdentifier

logger = Logger("DeviceIdentifierStore").set()
config = configparser.ConfigParser()

# const
ACCOUNT_ID  = 'accountId'
PROJECT_ID  = 'projectId'
SCHEMA_ID   = 'schemaId'
DEVICE_ID   = 'deviceId'

class DeviceIdentifierStore(ABC):

    def __init__(self, accountId: str = None, projectId: str = None, deviceSchemaId: str = None, deviceId: str = None) -> None:
        self._deviceConfig   = None
        self._accountId      = accountId
        self._projectId      = projectId
        self._deviceSchemaId = deviceSchemaId
        self._deviceId       = deviceId


    def _getParamAccountId(self) -> str:
        return self._accountId

    def _getParamProjectId(self) -> str:
        return self._projectId

    def _getParamSchemaId(self) -> str:
        return self._deviceSchemaId

    def _getParamDeviceId(self) -> str:
        return self._deviceId

    def getAccountId(self) -> str:
        val = self._accountId
        if val != None: return val
        else: raise Exception("Please override the getAccountId method to and return the value")

    def getProjectId(self) -> str:
        val = self._projectId
        if val != None: return val
        else: raise Exception("Please override the getProjectId method to and return the value")

    def getDeviceSchemaId(self) -> str:
        val = self._deviceSchemaId
        if val != None: return val
        else: raise Exception("Please override the getDeviceSchemaId method to and return the value")
        

    def getDeviceId(self) -> str:
        val = self._deviceId
        if val != None: return val
        else: raise Exception("Please override the getDeviceId method to and return the value")

    def _readConfigDevice(self, keyname: str) -> None:
        try:
            return self._deviceConfig[keyname]
        except KeyError:
            return None
        except Exception as ex:
            logger.error(ex)
            return None

    def resolveDeviceIdentifier(self, configFilePathName: str = 'config.ini') -> DeviceIdentifier:
        try:
            if (self._accountId == None or
                self._projectId == None or
                self._deviceSchemaId == None or
                self._deviceId == None
            ):
                logger.debug("resolveDeviceIdentifier: Some of identifier is null")
                if self._deviceConfig == None: 
                    try:
                        logger.debug("resolveDeviceIdentifier: Read from config file")
                        config.read(configFilePathName)
                        if 'device' in config:
                            self._deviceConfig = config['device']
                            if (self._accountId == None): self._accountId = self._readConfigDevice(ACCOUNT_ID)
                            else: self._deviceConfig[ACCOUNT_ID] = self._accountId

                            if (self._projectId == None): self._projectId = self._readConfigDevice(PROJECT_ID)
                            else: self._deviceConfig[PROJECT_ID] = self._projectId

                            if (self._deviceSchemaId == None): self._deviceSchemaId = self._readConfigDevice(SCHEMA_ID)
                            else: self._deviceConfig[SCHEMA_ID] = self._deviceSchemaId

                            if (self._deviceId == None): self._deviceId = self._readConfigDevice(DEVICE_ID)
                            else: self._deviceConfig[DEVICE_ID] = self._deviceId

                            logger.debug(f'resolveDeviceIdentifier: accountId: {self._accountId}')
                            logger.debug(f'resolveDeviceIdentifier: projectId: {self._projectId}')
                            logger.debug(f'resolveDeviceIdentifier: schemaId:  {self._deviceSchemaId}')
                            logger.debug(f'resolveDeviceIdentifier: deviceId:  {self._deviceId}')

                            return DeviceIdentifier(
                                self._accountId, 
                                self._projectId, 
                                self._deviceSchemaId, 
                                self._deviceId
                            )
                    except Exception as ex:
                        logger.debug("resolveDeviceIdentifier: Error reading config file")
                        logger.warn(ex)
                        self._deviceConfig = {} 
                
                logger.debug("resolveDeviceIdentifier: Config file does not exists")
                logger.debug("resolveDeviceIdentifier: Read from methods")
                self._accountId      = self.getAccountId()
                self._projectId      = self.getProjectId()
                self._deviceSchemaId = self.getDeviceSchemaId()
                self._deviceId       = self.getDeviceId()
                self._deviceConfig = {
                    ACCOUNT_ID: self._accountId,
                    PROJECT_ID: self._projectId,
                    SCHEMA_ID: self._deviceSchemaId,
                    DEVICE_ID: self._deviceId
                }

                logger.debug(f'resolveDeviceIdentifier: accountId: {self._accountId}')
                logger.debug(f'resolveDeviceIdentifier: projectId: {self._projectId}')
                logger.debug(f'resolveDeviceIdentifier: schemaId:  {self._deviceSchemaId}')
                logger.debug(f'resolveDeviceIdentifier: deviceId:  {self._deviceId}')

            return DeviceIdentifier(
                self._accountId, 
                self._projectId, 
                self._deviceSchemaId, 
                self._deviceId
            )

        except Exception as ex:
            logger.error(ex)
            raise Exception(ex)

from .model import DeviceIdentifier
from ..utility.logger import Logger
from .identifierStore import DeviceIdentifierStore

logger = Logger("DeviceManagement").set()

class DeviceManagement():

    def __init__(self, store: DeviceIdentifierStore) -> None:
        self._store = store

    @property
    def store(self):
        return self._store

    @store.setter
    def store(self, store: DeviceIdentifierStore):
        self._store = store

    @store.getter
    def store(self):
        return self._store

    def getDeviceIdentifier(self) -> DeviceIdentifier:
        """
        This function returns the device identifier of the device
        :return: The device identifier.
        """
        try:
            logger.debug(f'getDeviceIdentifier: {self._store.resolveDeviceIdentifier()}')
            return self._store.resolveDeviceIdentifier()
        except Exception as ex:
            logger.error(ex)
            raise Exception(ex)

    def getDeviceSchemaId(self) -> str:
        """
        Get the device schema id for the device
        :return: The device schema id
        """
        try:
            return self._store.getDeviceSchemaId()
        except Exception as ex:
            logger.error(ex)
            raise Exception(ex)

    @staticmethod
    def resolveDeviceUniqueId(deviceIdentifier: DeviceIdentifier) -> str:
        """
        Given a device identifier, return a unique device identifier
        
        :param deviceIdentifier: The device identifier
        :type deviceIdentifier: DeviceIdentifier
        :return: The device unique id.
        """
        return f'{deviceIdentifier.accountId}-{deviceIdentifier.projectId}-{deviceIdentifier.deviceId}'

    @staticmethod
    def resolveClientId(deviceIdentifier: DeviceIdentifier) -> str:
        """
        This function takes a DeviceIdentifier object and returns a string
        
        :param deviceIdentifier: The device identifier of the device you want to resolve
        :type deviceIdentifier: DeviceIdentifier
        :return: The device id
        """
        return DeviceManagement.resolveDeviceUniqueId(deviceIdentifier)
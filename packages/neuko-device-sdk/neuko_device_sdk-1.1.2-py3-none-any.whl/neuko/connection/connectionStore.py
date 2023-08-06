import logging
import socket
import inspect
from abc import ABC, abstractmethod
from ..utility.logger import Logger
from ..device.model import DeviceIdentifier

logger = Logger("ConnectionStore").set()

class ConnectionStore(ABC):

    def __new__(cls, *arg, **kwargs):
        # get all coros 
        parent_coros = inspect.getmembers(ConnectionStore, predicate=inspect.iscoroutinefunction)

        # check if parent's coros are still coros in a child
        for coro in parent_coros:
            child_method = getattr(cls, coro[0])
            if not inspect.iscoroutinefunction(child_method):
                raise RuntimeError('The method %s must be a coroutine' % (child_method,))

        return super(ConnectionStore, cls).__new__(cls, *arg, **kwargs)


    @abstractmethod
    async def getPerpetualConnectionSettings(self, deviceIdentifier: DeviceIdentifier) -> str:
        """
        Implementation as to return a string of connection settings
        @param deviceIdentifier Device properties
        """
        pass

    @abstractmethod
    async def savePerpetualConnectionSettings(self, deviceIdentifier: DeviceIdentifier, settings: str) -> bool:
        """
        Implementation as to save a string of connection settings
        @param deviceIdentifier Device properties
        @param settings JSON stringified connection settings
        """
        pass

    @abstractmethod
    async def deletePerpetualConnectionSettings(self, deviceIdentifier: DeviceIdentifier) -> None:
        """
        Implementation as to delete a saved string of connection settings
        @param deviceIdentifier Device properties
        """
        pass

    @abstractmethod
    async def isPerpetualConnectionSettingsExists(self, deviceIdentifier: DeviceIdentifier) -> bool:
        """
        Implementation as to check if a saved string of connection settings exists
        @param deviceIdentifier Device properties
        """
        pass


    async def isConnectedToInternet(self, host = "1.1.1.1", port = 53, timeout = 3) -> bool:
        """
        This function check the internet connection to DNS server (credit to https://stackoverflow.com/questions/3764291/how-can-i-see-if-theres-an-available-and-active-network-connection-in-python). 
        
        However, we'd encourage for you to override this method if there is anything that will block TCP checking as in default implementation.
        """
        try:
            socket.setdefaulttimeout(timeout)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
            sock.close()
            logger.debug("Resolved DNS")
            return True
        except socket.error as ex:
            logger.warning("Unable to connect to internet")
            logger.error(ex)
            return False
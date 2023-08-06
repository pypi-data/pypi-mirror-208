import inspect
from ..utility.logger import Logger
from ..device.model import DeviceIdentifier, Worker, WorkerFunction, TelemetricStateChangeParameter

logger = Logger("TelemetricWorker").set()

WILDCARD: str = '*'

class TelemetricWorker:

    def __init__(self) -> None:
        self.__workers: list = []

    def _resolveWorkerName(self, deviceIdentifier: DeviceIdentifier, stateName: str, attributeTree: str) -> str:
        """
        The function takes in a deviceIdentifier, stateName, and attributeTree and returns a string
        
        :param deviceIdentifier: The device identifier
        :type deviceIdentifier: DeviceIdentifier
        :param stateName: The name of the state
        :type stateName: str
        :param attributeTree: The path to the attribute in the device state
        :type attributeTree: str
        :return: The name of the worker.
        """
        logger.debug(f'_resolveWorkerName: deviceIdentifier: {deviceIdentifier}')
        return f'id::{deviceIdentifier.accountId}{deviceIdentifier.projectId}{deviceIdentifier.deviceId}::state::{stateName}/{attributeTree}'

    def _isWorkerExistsByName(self, name: str) -> bool:
        """
        Check if a worker with a given name exists in the list of workers
        
        :param name: The name of the worker
        :type name: str
        :return: A boolean value.
        """
        for item in self.__workers:
            worker: Worker = item
            logger.debug(f'_isWorkerExistsByName: worker.name {worker.name}')
            logger.debug(f'_isWorkerExistsByName: name        {name}')
            if worker.name == name: return True

        return False

    def _getWorkerIndexByName(self, name: str) -> int:
        for index, item in enumerate(self.__workers):
            worker: Worker = item
            if worker.name == name: return index

        return -1

    async def _executeWildcard(self, deviceIdentifier: DeviceIdentifier, stateName: str, attributeTree: str, value) -> bool:
        """
        If a wildcard is registered for the stateName, then execute the wildcard
        
        :param deviceIdentifier: The device identifier of the device that changed
        :type deviceIdentifier: DeviceIdentifier
        :param stateName: The name of the state that was changed
        :type stateName: str
        :param attributeTree: The attribute tree that was changed
        :type attributeTree: str
        :param value: The value of the attribute that was changed
        :return: The return value is a boolean.
        """
        try:
            name = self._resolveWorkerName(deviceIdentifier, stateName, WILDCARD)
            if self._isWorkerExistsByName(name):
                wildcard: Worker = self.__workers[self._getWorkerIndexByName(name)]
                logger.debug(f'_executeWildcard: A wildcard is registered for {stateName}')
                params = TelemetricStateChangeParameter(
                    wildcard.callbacks[0].context,
                    stateName,
                    deviceIdentifier,
                    attributeTree,
                    value,
                    wildcard.callbacks[0].signature
                )

                if inspect.iscoroutinefunction(wildcard.callbacks[0].execution):
                    result = await wildcard.callbacks[0].execution(params)
                else:
                    result = wildcard.callbacks[0].execution(params)

                if result: logger.debug(f'_executeWildcard: Success executed worker {name}')
                else: logger.debug(f'_executeWildcard: Failed in executing worker {name}')
                return result
            else:
                logger.debug(f'_executeWildcard: No wildcard registered for {stateName}')
                return True
        except Exception as ex:
            logger.error(ex)
            return False

    def add(self, context: object, deviceIdentifier: DeviceIdentifier, stateName: str, attributeTree: str = WILDCARD, listener = None) -> None:
        """
        Add a worker to the list of workers
        
        :param context: The context object that the callback function will use
        :type context: object
        :param deviceIdentifier: The device identifier
        :type deviceIdentifier: DeviceIdentifier
        :param stateName: The name of the state to be monitored
        :type stateName: str
        :param attributeTree: This is the attribute tree that will be used to resolve the attribute name
        :type attributeTree: str
        :param listener: The listener is a function that will be called when the worker is triggered
        """
        try:
            name = self._resolveWorkerName(deviceIdentifier, stateName, attributeTree)
            logger.debug(f'add: Adding a worker {name}')

            if self._isWorkerExistsByName(name):
                logger.warn(f'add: Worker {name} already added')
            else:
                callback = WorkerFunction(context, listener)
                worker = Worker(name, callback)
                self.__workers.append(worker) 
                logger.debug(f'add: Worker {name} added')

        except Exception as ex:
            logger.error(ex)
            raise Exception(ex)

    async def execute(self, deviceIdentifier: DeviceIdentifier, stateName: str, attributeTree: str, value) -> bool:
        """
        If the worker is registered, it will be executed
        
        :param deviceIdentifier: The device identifier
        :type deviceIdentifier: DeviceIdentifier
        :param stateName: The name of the state to be changed
        :type stateName: str
        :param attributeTree: The attribute tree that was changed
        :type attributeTree: str
        :param value: The value to be set
        :return: The return value is a boolean indicating whether the execution was successful or not.
        """
        try:
            wildcardRes = await self._executeWildcard(deviceIdentifier, stateName, attributeTree, value)
            if wildcardRes == False: return False
            
            name = self._resolveWorkerName(deviceIdentifier, stateName, attributeTree)
            if self._isWorkerExistsByName(name):
                worker: Worker = self.__workers[self._getWorkerIndexByName(name)]

                params = TelemetricStateChangeParameter(
                    worker.callbacks[0].context,
                    stateName,
                    deviceIdentifier,
                    attributeTree,
                    value,
                    worker.callbacks[0].signature
                )
                
                if inspect.iscoroutinefunction(worker.callbacks[0].execution):
                    logger.debug(f'execute: Execute a coroutine method')
                    result = await worker.callbacks[0].execution(params)
                else:
                    logger.debug(f'execute: Execute a normal method')
                    result = worker.callbacks[0].execution(params)

                if result: logger.debug(f'execute: Success executed worker {name}')
                else: logger.debug(f'execute: Failed in executing worker {name}')
                return result
            else:
                logger.debug(f'execute: No worker registered for {name}')
                return True
        except Exception as ex:
            logger.error(ex)
            return False

    
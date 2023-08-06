import collections
import json
import time
from enum import Enum
from pydash import get, set_, unset
from ..utility.logger import Logger

logger = Logger("TelemetricState").set()

class TelemetricStateType(str, Enum):
    Reported = "reported"
    Desired = "desired"
    Difference = "delta"

class TelemetricState:
    def __init__(self) -> None:
        self.version = 1
        self.lastPushTime = -1
        self.allStates: list = []
        self.states = {
            TelemetricStateType.Reported: {},
            TelemetricStateType.Desired: {},
            TelemetricStateType.Difference: {}
        }
        self.metadata = {
            TelemetricStateType.Reported: {},
            TelemetricStateType.Desired: {},
            TelemetricStateType.Difference: {}
        }

    def _isStateExists(self, stateName: str) -> bool:
        """
        Check if a state exists in the state machine
        
        :param stateName: The name of the state to check for
        :type stateName: str
        :return: The index of the state in the list of all states.
        """
        try:
            index = self.allStates.index(stateName)
            if index > -1: 
                logger.debug(f'_isStateExists: {stateName} exists')
                return True
            else: 
                logger.warning(f'_isStateExists: {stateName} does not exists')
                return False
        except ValueError:
            logger.warning(f'_isStateExists: {stateName} does not exists')
            return False

    def _createNewState(self, stateName: str) -> None:
        """
        If the state doesn't exist, create it
        
        :param stateName: The name of the state to create
        :type stateName: str
        """
        if self._isStateExists(stateName) == False:
            self.allStates.append(stateName)

        self.states[TelemetricStateType.Reported][stateName] = {}
        self.states[TelemetricStateType.Desired][stateName] = {}
        self.states[TelemetricStateType.Difference][stateName] = {}
        self.metadata[TelemetricStateType.Reported][stateName] = {}
        self.metadata[TelemetricStateType.Desired][stateName] = {}
        self.metadata[TelemetricStateType.Difference][stateName] = {}

    def _isVirtualAheadOfLocal(self, stateName: str, attributeTree: str, vTimestamp, dataType: TelemetricStateType = TelemetricStateType.Reported) -> bool:
        """
        If the virtual time is less than or equal to the local time, return False. Otherwise, return
        True
        
        :param stateName: the name of the state
        :type stateName: str
        :param attributeTree: The attribute tree of the attribute that is being compared
        :type attributeTree: str
        :param vTimestamp: The timestamp of the virtual state
        :param dataType: The type of data to check. Can be either REPORTED or ADMIN
        :type dataType: str
        :return: The return value is a boolean that indicates whether the virtual time is ahead of the
        local time.
        """
        if get(self.metadata[dataType][stateName], attributeTree) and vTimestamp <= get(self.metadata[dataType][stateName], attributeTree):
            logger.debug(f'_isVirtualAheadOfLocal: {stateName}/{attributeTree}: The virtual time < local time')
            return False
        else:
            logger.debug(f'_isVirtualAheadOfLocal: {stateName}/{attributeTree}: The virtual time > local time')
            return True

    def value(self, stateName: str, stateType: TelemetricStateType = TelemetricStateType.Reported, attributeTree: str = "*"):
        """
        It returns the value of a state, given the state name, state type, and attribute tree
        
        :param stateName: The name of the state you want to get the value of
        :type stateName: str
        :param stateType: TelemetricStateType = TelemetricStateType.Reported
        :type stateType: TelemetricStateType
        :param attributeTree: This is a string that represents the path to the attribute you want to
        get.  For example, if you want to get the value of the "temperature" attribute of the "sensor"
        attribute of the "device" attribute, you would pass in "device.sensor.temperature, defaults to *
        :type attributeTree: str (optional)
        :return: The value of the state.
        """
        try:
            if (attributeTree == "*"):
                return self.states[stateType][stateName]
            else:
                return get(self.states[stateType][stateName], attributeTree, None)
        except Exception as ex:
            logger.error(ex)
            raise Exception(ex)

    def report(self, stateName: str, attributeTree: str, value, vTimestamp) -> bool:
        """
        If the reported state is ahead of the desired state, then update the reported state and remove
        the desired state
        
        :param stateName: The name of the state
        :type stateName: str
        :param attributeTree: The attribute tree is a string that represents the path to the attribute.
        For example, if you have a state called "temperature" and you want to report the value of the
        "celsius" attribute, the attribute tree would be "temperature.celsius"
        :type attributeTree: str
        :param value: The value of the state
        :param vTimestamp: The timestamp of the state in the virtual twin
        :return: A boolean value.
        """
        try:
            logger.debug(f'report: {stateName} / {attributeTree} / {value} / {vTimestamp}')
            # now
            now = int(time.time())

            # check and create
            if self._isStateExists(stateName) == False: self._createNewState(stateName)

            if get(self.states[TelemetricStateType.Reported][stateName], attributeTree) == None:
                set_(self.states[TelemetricStateType.Reported][stateName], attributeTree, value)
                set_(self.metadata[TelemetricStateType.Reported][stateName], attributeTree, now)
                logger.debug(f'report: Created new reported state {stateName} attributes {attributeTree}')
            else:
                # check against desired
                if get(self.states[TelemetricStateType.Reported][stateName], attributeTree) == get(self.states[TelemetricStateType.Desired][stateName], attributeTree):
                    logger.debug(f'report: The new state {stateName} attribute {attributeTree} value is equal to desired state')
                else:
                    set_(self.states[TelemetricStateType.Reported][stateName], attributeTree, value)
                    set_(self.metadata[TelemetricStateType.Reported][stateName], attributeTree, now)
                    logger.debug(f'report: Updated new reported state {stateName} attributes {attributeTree}')

            # remove desired
            unset(self.states[TelemetricStateType.Desired][stateName], attributeTree)
            unset(self.metadata[TelemetricStateType.Desired][stateName], attributeTree)
            logger.debug(f'report: Removed desired state {stateName} attributes {attributeTree}')
            return True

            # # only update if virtual timestamp ahead of local
            # if self._isVirtualAheadOfLocal(stateName, attributeTree, vTimestamp, TelemetricStateType.Reported):
            #     if get(self.states[TelemetricStateType.Reported][stateName], attributeTree) == None:
            #         set_(self.states[TelemetricStateType.Reported][stateName], attributeTree, value)
            #         set_(self.metadata[TelemetricStateType.Reported][stateName], attributeTree, now)
            #         logger.debug(f'report: Created new reported state {stateName} attributes {attributeTree}')
            #     else:
            #         # check against desired
            #         if get(self.states[TelemetricStateType.Reported][stateName], attributeTree) == get(self.states[TelemetricStateType.Desired][stateName], attributeTree):
            #             logger.debug(f'report: The new state {stateName} attribute {attributeTree} value is equal to desired state')
            #         else:
            #             set_(self.states[TelemetricStateType.Reported][stateName], attributeTree, value)
            #             set_(self.metadata[TelemetricStateType.Reported][stateName], attributeTree, now)
            #             logger.debug(f'report: Updated new reported state {stateName} attributes {attributeTree}')

            #     # remove desired
            #     unset(self.states[TelemetricStateType.Desired][stateName], attributeTree)
            #     unset(self.metadata[TelemetricStateType.Desired][stateName], attributeTree)
            #     logger.debug(f'report: Removed desired state {stateName} attributes {attributeTree}')
            #     return True
            # else:
            #     logger.debug(f'report: Timestamp in local for state {stateName} ({vTimestamp}) attributes {attributeTree} is ahead of its Virtual Twin ({get(self.metadata[TelemetricStateType.Reported][stateName], attributeTree)})')
            #     return False
        except Exception as ex:
            logger.warning(ex)
            return False

    def desire(self, stateName: str, attributeTree: str, value, vTimestamp) -> bool:
        """
        Create a new desired state
        
        :param stateName: The name of the state to be created
        :type stateName: str
        :param attributeTree: The name of the attribute tree
        :type attributeTree: str
        :param value: The value of the attribute
        :param vTimestamp: The time the desired state was set
        :return: The return value is a boolean.
        """
        try:
            # now
            now = int(time.time())

            # check and create
            if self._isStateExists(stateName) == False: self._createNewState(stateName)

            set_(self.states[TelemetricStateType.Desired][stateName], attributeTree, value)
            set_(self.metadata[TelemetricStateType.Desired][stateName], attributeTree, now)
            logger.debug(f'report: Created new desired state {stateName} attributes {attributeTree}')
            return True
        except Exception as ex:
            logger.warning(ex)
            return False

    def getPendingDesire(self, stateName: str):
        """
        Get the pending desire for a given state
        
        :param stateName: The name of the state to get the pending desire for
        :type stateName: str
        :return: A dictionary with the attributeTree and value.
        """
        flat = TelemetricState.flattening(self.states[TelemetricStateType.Desired][stateName])
        for key in flat:
            logger.debug(f'getPendingDesire: Pending {key}')
            return {
                'attributeTree': key,
                'value': get(self.states[TelemetricStateType.Desired][stateName], key)
            }

    def snapshot(self, stateName: str, attributesOnly: bool = False, withDesire: bool = False) -> object:
        """
        This function returns a snapshot of the current state of an object, including reported and
        desired attributes if specified.
        
        :param stateName: The name of the state for which a snapshot is being taken
        :type stateName: str
        :param attributesOnly: A boolean parameter that determines whether to return the entire state or
        just the attributes of the state, defaults to False
        :type attributesOnly: bool (optional)
        :param withDesire: `withDesire` is a boolean parameter that determines whether the returned
        object should include the desired state in addition to the reported state. If `withDesire` is
        `True`, the returned object will have a `state` key with both `reported` and `desired` keys. If
        `, defaults to False
        :type withDesire: bool (optional)
        :return: an object that contains a snapshot of the current state of the device. The contents of
        the object depend on the values of the parameters passed to the function. If `attributesOnly` is
        `False`, the object will contain the reported state of the device, and if `withDesire` is
        `True`, it will also contain the desired state. If `attributesOnly` is `
        """
        latest = get(self.states[TelemetricStateType.Reported], stateName)
        logger.debug(f'snapshot: Value for {stateName} = {json.dumps(latest)}')
        if attributesOnly == False:

            if withDesire:
                return {
                    'state': {
                        'reported': latest,
                        'desired': get(self.states[TelemetricStateType.Desired], stateName)
                    }
                }
            else:
                return {
                    'state': {
                        'reported': latest
                    }
                }
        else:
            return latest

    def getLastTime(self):
        """
        Return the last time the push button was pressed
        :return: The last time the button was pushed.
        """
        return self.lastPushTime

    def updateNewTime(self):
        """
        This function updates the lastPushTime variable to the current time
        """
        self.lastPushTime = int(time.time() * 1000)

    @staticmethod
    def flattening(dictionary, parent_key=False, separator='.'):
        """
        It takes a dictionary, and returns a dictionary with all the keys flattened
        
        :param dictionary: The dictionary to flatten
        :param parent_key: This is the key of the parent dictionary, defaults to False (optional)
        :param separator: The separator to use between the keys, defaults to . (optional)
        :return: A dictionary with the keys being the parent_key + separator + key and the values being
        the value.
        """
        items = []
        for key, value in dictionary.items():
            new_key = str(parent_key) + separator + key if parent_key else key
            if isinstance(value, collections.MutableMapping):
                items.extend(TelemetricState.flattening(value, new_key, separator).items())
            else:
                items.append((new_key, value))
        return dict(items)
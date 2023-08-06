from enum import Enum
from typing import Union
from ..device.model import DeviceIdentifier

class Provider(str, Enum):
    BOOTSTRAP = "BOOTSTRAP"
    NEUKO = "NEUKO"

class AwsUpdateDelta:
    def __init__(self, state: object, metadata: object, timestamp: Union[int, float, str], version: Union[str, int] = None, clientToken: str = None) -> None:
        self.state = state
        self.metadata = metadata
        self.timestamp = timestamp
        self.version = version
        self.clientToken = clientToken

class UpdateDelta:
    def __init__(self, deviceIdentifier: DeviceIdentifier, stateName: str, delta: object) -> None:
        self.deviceIdentifier = deviceIdentifier
        self.stateName = stateName
        self.delta = delta



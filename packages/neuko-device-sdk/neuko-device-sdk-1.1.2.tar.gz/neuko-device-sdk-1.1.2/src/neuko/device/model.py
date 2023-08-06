import uuid

class DeviceIdentifier:
    def __init__(self, accountId, projectId, deviceSchemaId, deviceId) -> None:
        self.accountId      = accountId
        self.projectId      = projectId
        self.deviceSchemaId = deviceSchemaId
        self.deviceId       = deviceId

class WorkerFunction:
    def __init__(self, context: object, callback, signature: str = None) -> None:
        self.context = context
        self.execution = callback
        if signature == None: self.signature = uuid.uuid4().hex
        else: self.signature = signature

class Worker:
    def __init__(self, name: str, callback: WorkerFunction) -> None:
        self.name = name
        self.callbacks = [callback]

class TelemetricStateChangeParameter:
    def __init__(self, context, stateName: str, deviceIdentifier: DeviceIdentifier, attributeTree: str, value, signature: str) -> None:
        self.context = context
        self.stateName = stateName
        self.deviceIdentifier = deviceIdentifier
        self.signature = signature
        self.attributeTree = attributeTree
        self.value = value

class FeatureInterval(dict):
    def __init__(self, version: int, value: int) -> None:
        dict.__init__(self, version=version, value=value)

class FeatureTimestreamStorage(dict):
    def __init__(self, version: int, value: list) -> None:
        dict.__init__(self, version=version, value=value)

class FeatureBackupStorage(dict):
    def __init__(self, version: int, value: list) -> None:
        dict.__init__(self, version=version, value=value)

class FeatureRelay(dict):
    def __init__(self, version: int, value: list) -> None:
        dict.__init__(self, version=version, value=value)

class Features(dict):
    def __init__(self, interval: FeatureInterval, timestreamStorage: FeatureTimestreamStorage, backupStorage: FeatureBackupStorage, relay: FeatureRelay) -> None:
        dict.__init__(self, interval=interval, timestreamStorage=timestreamStorage, backupStorage=backupStorage, relay=relay)

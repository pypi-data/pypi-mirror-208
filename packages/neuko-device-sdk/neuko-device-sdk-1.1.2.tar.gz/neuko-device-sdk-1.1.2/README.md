# Device SDK for Python

This document provides information about the Neuko SDK that can be installed as a dependency in an IoT device.

## Pre-requisites

1. Neuko account (sign up [here](https://auth.neuko.io/signup?client_id=30qirvopvpabg1njrdp4mt54tl&response_type=code&scope=email+openid+profile&redirect_uri=https://app.neuko.io/oauth))
2. Defined device type schema (refer [documentation](https://neuko.io/docs/schema/))
3. Bootstrap certificates that can downloaded after define a device type schema (step 2)


## Device State

Device state is the condition of the hardware at any moment. Typically, the state will be watched, executed and updated under certain circumstances. You can imagine the state of a digital board as below:

```json
{
    "digital_input": {
        "pin_0": true,
        "pin_1": false
    },
    "digital_output": {
        "pin_0": true,
        "pin_1": true
    }
}
```

The above example tells us that the digital board has 2 states:
1. digital input
2. digital output

Also, each state has 2 attributes - pin 0 and pin 1.

The Neuko Python SDK works by managing the state's attributes of the device between actual physical and its virtual representation in cloud. 

Prior to that, the SDK supports provisioning of a new device during 1st time connection.


## Installation

### Checking minimum requirement
The SDK requires Python 3.6 and above.

```python
python --version
```

### Installation

```python
pip install neuko-device-sdk
```

## Usage

### Import package

```python
from neuko.device.device import Device
from neuko.iot.bootstrap import BootstrapClient
from neuko.iot.neuko import NeukoClient
```

### Extend DeviceIdentifierStore class

```python
class DeviceIdentifierStoreObject(DeviceIdentifierStore):
    def getAccountId(self) -> str:
        return "<Neuko Account Id>"

    def getProjectId(self) -> str:
        return "<Neuko Project Id>"

    def getDeviceSchemaId(self) -> str:
        return "<Device Serial Number / Id>"

    def getDeviceId(self) -> str:
        return "<Neuko Device Type Schema Id>"
```

### Extend ConnectionStore class

```python
class ConnectionStoreObject(ConnectionStore):
    async def getPerpetualConnectionSettings(self, deviceIdentifier: DeviceIdentifier) -> str:
        fd = open("./my-secure-directory/neuko-device-connection-settings.json", mode="r")
        raw = json.load(fd)
        fd.close()
        return raw

    async def savePerpetualConnectionSettings(self, deviceIdentifier: DeviceIdentifier, settings: str) -> bool:
        fd = open("./my-secure-directory/neuko-device-connection-settings.json", mode="w")
        json.dump(settings, fd)
        fd.close()
        return True

    async def deletePerpetualConnectionSettings(self, deviceIdentifier: DeviceIdentifier) -> bool:
        return True

    async def isPerpetualConnectionSettingsExists(self, deviceIdentifier: DeviceIdentifier) -> bool:
        return False
}
```

### Extend CertificateStore class

```python
class CertificateStoreObject(CertificateStore):

    async def getBootstrapCertificateAuthority(self, deviceIdentifier: DeviceIdentifier) -> str:
        return "./my-secure-directory/certificates/cert.ca.pem"

    async def getBootstrapChainCertificate(self, deviceIdentifier: DeviceIdentifier) -> str:
        return "./my-secure-directory/certificates/bootstrap-certificate.pem.crt"

    async def getBootstrapPrivateKey(self, deviceIdentifier: DeviceIdentifier) -> str:
        return "./my-secure-directory/certificates/bootstrap-private.pem.key"

    async def getPerpetualCertificateAuthority(self, deviceIdentifier: DeviceIdentifier) -> str:
        fd = open("./my-secure-directory/certificates/cert.ca.pem", mode="r")
        raw = fd.read()
        fd.close()
        return raw

    async def getPerpetualChainCertificate(self, deviceIdentifier: DeviceIdentifier) -> str:
        fd = open("./my-secure-directory/certificates/certificate.pem.crt", mode="r")
        raw = fd.read()
        fd.close()
        return raw

    async def getPerpetualPrivateKey(self, deviceIdentifier: DeviceIdentifier) -> str:
        fd = open("./my-secure-directory/certificates/cert.ca.pem", mode="r")
        raw = fd.read()
        fd.close()
        return raw

    async def savePerpetualCertificateAuthority(self, deviceIdentifier: DeviceIdentifier, certificate: str) -> None:
        fd = open("./my-secure-directory/certificates/cert.ca.pem", mode="w")
        fd.write(certificate)
        fd.close()

    async def savePerpetualChainCertificate(self, deviceIdentifier: DeviceIdentifier, certificate: str) -> None:
        fd = open("./my-secure-directory/certificates/certificate.pem.crt"", mode="w")
        fd.write(certificate)
        fd.close()

    async def savePerpetualPrivateKey(self, deviceIdentifier: DeviceIdentifier, certificate: str) -> None:
        fd = open("./my-secure-directory/certificates/cert.ca.pem", mode="w")
        fd.write(certificate)
        fd.close()
```

### Create Device class instance

```python
device = Device(DeviceIdentifierStoreObject(), ConnectionStoreObject(), CertificateStoreObject())
device.start_threadsafe()
```

## Methods

### start()
This function start the SDK or in other words starts the virtual/twin of the device. The function also provisions the device with Neuko registry if it is yet to be registered.
A provisioned device will stay in its perpetual state.

**Important**
Only called this function after you have registered (by useEffect method) the handler to be invoked when any of the telemetric state has any changed request.

### useEffect(context, listener, stateName: str, attributeTree: str = "*")
Use effect attaches a listener or function handler to any state's attributes. The parameters details are as below:

1. context - Class or any object of context. (eg. this)

2. Function that will be invoked when the value of interest attribute changed. The function must return true if the process success. Otherwise return false.

3. stateName - the name of the state.

4. attributeTree - Dot notation representing state attribute. For example, if you have state as below

```json
{
    "state_name_1": {
        "attr_0": true,
        "attr_1": {
            "deep_attr_0": false
        }
    }
}
```

The *deep_attr_0* tree is **attr_1.deep_attr_0**


Example

```python
def callback(data: TelemetricStateChangeParameter):
    logging.debug(f'data: {data}')
    return True

device.useEffect(self, callback, "digital_input", "pin_0")
device.useEffect(self, callback, "digital_input", "pin_1")

// or use wildcard to invoke the listener for any attribute
device.useEffect(self, callback, "digital_input", "*");
```

### updateTelemetricState(stateName: string, value: object)
Call this function when the state of actual device changed. The function will synchronize with its virtual/twin on cloud.

Example

```python
device.updateTelemetricState("digital_output", {
    "pin_0": false,
    "pin_1": false,
})
```




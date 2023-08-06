import ssl
import paho.mqtt.client as Mqtt
import aiohttp
import uuid
import json
import asyncio
import inspect
import threading
from datetime import datetime, timezone
from paho.mqtt.client import MQTTMessage
from .iot import IoT
from .model import AwsUpdateDelta, UpdateDelta
from ..utility.logger import Logger
from ..connection.model import ConfigurationProtocol, Certificate
from ..device.deviceManagement import DeviceManagement
from ..connection.certificateManagement import CertificateManagement
from ..connection.connectionManagement import ConnectionManagement
from ..device.model import DeviceIdentifier

from os.path import exists

#  config and const
logger = Logger("NeukoClient").set()
HTTPS_PROTOCOL: str     = "https://"
AWS_PREFIX:     str     = '$aws'
RULES_PREFIX:   str     = 'rules'
THING_PREFIX:   str     = 'things'
TIMESTREAMRULE: str     = 'DataTimestream'
ALLSHADOWNAMES: str     = '+'
SLEEP_DURATION: float   = 100e-3

class NeukoClient(IoT):

    def __init__(self, deviceIdentifier: DeviceIdentifier, connectionManager: ConnectionManagement, certificateManager: CertificateManagement) -> None:
        super().__init__(deviceIdentifier, connectionManager, certificateManager)
        self.__publishResponseBuffer: list = []

    def __registerPublishResponseBuffer(self, id: str = None, flag: bool = False, value: str = None) -> str:
        if id == None: 
            id = uuid.uuid4().hex
            logger.debug(f"__registerPublishResponseBuffer: Register new buffer id {id}")
        self.__publishResponseBuffer += [[id, flag, value]]
        return id

    def __findIndexPublishResponseBuffer(self, id) -> int:
        index = 0
        for buff in self.__publishResponseBuffer:
            if buff[0] == id:
                logger.debug(f"__findIndexPublishResponseBuffer: Found buffer at index {index}")
                return index
            else:
                index += 1
        raise Exception("MissingPublishBuffer")

    def __removePublishResponseBuffer(self, id) -> str:
        index = self.__findIndexPublishResponseBuffer(id)
        del self.__publishResponseBuffer[index]
        logger.debug(f"__removePublishResponseBuffer: Removed {id} at index {index}")

    def __updatePublishResponseBuffer(self, id: str, value: str) -> None:
        index = self.__findIndexPublishResponseBuffer(id)
        self.__publishResponseBuffer[index][2] = value
        self.__publishResponseBuffer[index][1] = True
        logger.debug(f"__updatePublishResponseBuffer: Updated {id} at index {index}")

    def _awsShadowNameConstructor(self, deviceId: str, stateName: str, operation: str) -> str:
        return '/'.join([AWS_PREFIX, THING_PREFIX, deviceId, "shadow", "name", stateName, operation])

    def _resolveListNamesShadowForThingPath(self, deviceId: str) -> str:
        return f'/api/things/shadow/ListNamedShadowsForThing/{deviceId}'

    def _onUpdateDelta(self, topic: str, deltaData):
        pass

    def _ssl_mqtt_context(self, configurationProtocol: ConfigurationProtocol, connectionCertificates: Certificate):
        """
        Creates an SSL context for the MQTT connection
        
        :param configurationProtocol: The configuration protocol to use
        :type configurationProtocol: ConfigurationProtocol
        :param connectionCertificates: The certificates used to connect to the IoT Hub
        :type connectionCertificates: Certificate
        :return: The SSL context.
        """
        sslContext = ssl.create_default_context()
        sslContext.set_alpn_protocols(configurationProtocol["mqtt"]["options"]["ALPNProtocols"])
        sslContext.load_verify_locations(cafile=connectionCertificates.certificateAuthority)
        sslContext.load_cert_chain(
            certfile=connectionCertificates.chainCertificate,
            keyfile=connectionCertificates.privateKey
        )
        return sslContext

    def _ssl_http_context(self, configurationProtocol: ConfigurationProtocol, connectionCertificates: Certificate):
        """
        Create a SSL context with the correct protocols and certificates
        
        :param configurationProtocol: The configuration protocol to use
        :type configurationProtocol: ConfigurationProtocol
        :param connectionCertificates: The certificates used to establish the connection
        :type connectionCertificates: Certificate
        :return: A SSL context.
        """
        sslContext = ssl.create_default_context()
        sslContext.set_alpn_protocols(configurationProtocol["http"]["options"]["ALPNProtocols"])
        sslContext.load_verify_locations(cafile=connectionCertificates.certificateAuthority)
        sslContext.load_cert_chain(
            certfile=connectionCertificates.chainCertificate,
            keyfile=connectionCertificates.privateKey
        )
        return sslContext

    async def connectMqttClient(self, configurationProtocol: ConfigurationProtocol, connectionCertificates: Certificate) -> None:
        try:
            logger.debug(f'connectMqttClient: connectionCertificates: {connectionCertificates}')
            self._mqttClient = Mqtt.Client(
                client_id=DeviceManagement.resolveClientId(self._deviceIdentifier),
                clean_session=True
            )
            logger.debug("connectMqttClient: Created MQTT client instance")
            logger.debug(f'connectMqttClient: ca files exists: {exists(connectionCertificates.certificateAuthority)}')
            self._mqttClient.tls_set_context(context=self._ssl_mqtt_context(configurationProtocol, connectionCertificates))
            logger.debug("connectMqttClient: Setup TLS context")
            self._mqttClient.connect_async(
                host=f'{configurationProtocol["mqtt"]["endpoint"]}',
                port=configurationProtocol["mqtt"]["port"]
            )
            logger.debug("connectMqttClient: Establishing MQTT connection to broker")
        except Exception as ex:
            logger.error(ex)
            raise Exception("OperationError")

    async def connectHttpClient(self, configurationProtocol: ConfigurationProtocol, connectionCertificates: Certificate) -> None:
        try:
            connector = aiohttp.TCPConnector(
                limit=None,
                ssl_context=self._ssl_http_context(configurationProtocol, connectionCertificates)
            )
            logger.debug("connectHttpClient: Created TCP secure transport")
            self._httpClient = aiohttp.ClientSession(
                base_url=f'https://{configurationProtocol["http"]["endpoint"]}:{configurationProtocol["http"]["port"]}',
                read_timeout=30,
                conn_timeout=30,
                connector=connector
            )
            logger.debug("connectHttpClient: Created Http client session")
        except:
            logger.error("Error establishing Http session")
            raise Exception("OperationError")

    async def fetchAllTelemetricStateNames(self) -> list:
        try:
            # init var
            deviceId = DeviceManagement.resolveDeviceUniqueId(self._deviceIdentifier)
            nextToken = None
            hasMoreNames = True
            stateNames = []

            while hasMoreNames:
                # build parameters
                params = {'pageSize': 10}
                if nextToken != None: params["nextToken"] = nextToken
                logger.debug(f'fetchAllTelemetricStateNames: parameters = {params}')
                
                # make request
                async with self._httpClient.get(
                    url=self._resolveListNamesShadowForThingPath(deviceId),
                    params=params
                ) as response:
                    logger.debug(f'fetchAllTelemetricStateNames: status: {response.status}; reason: {response.reason}')
                    if response.status != 200: raise Exception(response.reason)
                    data = await response.json()
                    logger.debug(f'fetchAllTelemetricStateNames: result: {data}')
                    stateNames += data['results']
                    if "nextToken" in data:
                        logger.debug(f'fetchAllTelemetricStateNames: More names available in registry')
                        nextToken = data['nextToken']
                        hasMoreNames = True
                    else:
                        logger.debug(f'fetchAllTelemetricStateNames: No more names available in registry')
                        hasMoreNames = False

            return stateNames

        except Exception as ex:
            logger.error(ex)
            raise Exception("OperationError")

    async def pullTelemetricState(self, stateName: str) -> object:
        try:
            # init var
            deviceId = DeviceManagement.resolveDeviceUniqueId(self._deviceIdentifier)
            operationName = self._awsShadowNameConstructor(deviceId, stateName, 'get')
            listenerAccepted = self._awsShadowNameConstructor(deviceId, stateName, 'get/accepted')
            listenerRejected = self._awsShadowNameConstructor(deviceId, stateName, 'get/rejected')
            bufferId = self.__registerPublishResponseBuffer()

            def callback(context: NeukoClient, bufferId, isError: bool, client, userdata, message: MQTTMessage):
                logger.debug(f'pullTelemetricState: Return message from topic {message.topic} - {message.mid}')
                if isError:
                    self.__updatePublishResponseBuffer(bufferId, json.dumps({
                        'result': False,
                        'topic': message.topic,
                        'payload': json.loads(message.payload)
                    }))
                else:
                    self.__updatePublishResponseBuffer(bufferId, json.dumps({
                        'result': True,
                        'topic': message.topic,
                        'payload': json.loads(message.payload)
                    }))
            
            await self.subscribe(listenerAccepted, lambda client, userdata, message: callback(self, bufferId, False, client, userdata, message))
            await self.subscribe(listenerRejected, lambda client, userdata, message: callback(self, bufferId, True, client, userdata, message))
            await self.publish(operationName, None)
            
            # loop until response
            waitFor = 0
            while waitFor < 5:
                index = self.__findIndexPublishResponseBuffer(bufferId)
                if self.__publishResponseBuffer[index][1]:
                    await self.unsubscribe(listenerAccepted)
                    await self.unsubscribe(listenerRejected)
                    logger.debug(f'pullTelemetricState: Callback returned')
                    data = json.loads(self.__publishResponseBuffer[index][2])
                    logger.info(f'pullTelemetricState: Topic {data["topic"]} responded')
                    self.__removePublishResponseBuffer(bufferId)
                    if data['result']:
                        return data['payload']
                    else:
                        raise Exception('NotFound')
                else:
                    logger.debug(f'pullTelemetricState: Wait callback... {waitFor}')
                    await asyncio.sleep(SLEEP_DURATION)
                    waitFor += SLEEP_DURATION

            await self.unsubscribe(listenerAccepted)
            await self.unsubscribe(listenerRejected)
            raise Exception('TimeoutError')
        except Exception as ex:
            logger.error(ex)
            raise Exception(ex)

    async def pushTelemetricState(self, stateName: str, state: object) -> None:
        try:
            # init var
            deviceId = DeviceManagement.resolveDeviceUniqueId(self._deviceIdentifier)
            operationName = self._awsShadowNameConstructor(deviceId, stateName, 'update')
            listenerAccepted = self._awsShadowNameConstructor(deviceId, stateName, 'update/accepted')
            listenerRejected = self._awsShadowNameConstructor(deviceId, stateName, 'update/rejected')
            bufferId = self.__registerPublishResponseBuffer()

            def callback(context: NeukoClient, bufferId, isError: bool, client, userdata, message: MQTTMessage):
                logger.debug(f'pushTelemetricState: Return message from topic {message.topic} - {message.mid}')
                if isError:
                    self.__updatePublishResponseBuffer(bufferId, json.dumps({
                        'result': False,
                        'topic': message.topic,
                        'payload': json.loads(message.payload)
                    }))
                else:
                    self.__updatePublishResponseBuffer(bufferId, json.dumps({
                        'result': True,
                        'topic': message.topic,
                        'payload': json.loads(message.payload)
                    }))
            
            await self.subscribe(listenerAccepted, lambda client, userdata, message: callback(self, bufferId, False, client, userdata, message))
            await self.subscribe(listenerRejected, lambda client, userdata, message: callback(self, bufferId, True, client, userdata, message))
            await self.publish(operationName, json.dumps(state))
            
            # loop until response
            waitFor = 0
            while waitFor < 5:
                index = self.__findIndexPublishResponseBuffer(bufferId)
                if self.__publishResponseBuffer[index][1]:
                    await self.unsubscribe(listenerAccepted)
                    await self.unsubscribe(listenerRejected)
                    logger.debug(f'pushTelemetricState: Callback returned')
                    data = json.loads(self.__publishResponseBuffer[index][2])
                    logger.info(f'pushTelemetricState: Topic {data["topic"]} responded')
                    self.__removePublishResponseBuffer(bufferId)
                    if data['result']:
                        return data['payload']
                    else:
                        logger.warn(f'pushTelemetricState: Error payload {json.dumps(data["payload"])}')
                        await self.unsubscribe(listenerAccepted)
                        await self.unsubscribe(listenerRejected)
                        raise Exception('Forbidden')
                else:
                    logger.debug(f'pushTelemetricState: Wait callback... {waitFor}')
                    await asyncio.sleep(SLEEP_DURATION)
                    waitFor += SLEEP_DURATION

            await self.unsubscribe(listenerAccepted)
            await self.unsubscribe(listenerRejected)
            raise Exception('TimeoutError')
        except Exception as ex:
            logger.error(ex)
            raise Exception(ex)

    async def timestreamStorage(self, stateName: str, state: object) -> None:
        try:
            # init var
            deviceId = DeviceManagement.resolveDeviceUniqueId(self._deviceIdentifier)
            now = datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
            payload = {
                'device_id': deviceId,
                'state_name': stateName,
                'timestamp': now,
                'data': state
            }
            logger.debug(f'timestreamStorage: payload = {payload}')

            await self.publish(
                f'{AWS_PREFIX}/{RULES_PREFIX}/{TIMESTREAMRULE}/{deviceId}',
                json.dumps(payload)
            )
        except Exception as ex:
            logger.error(ex)
            raise Exception(ex)

    async def onTelemetricStateChangedRequest(self, context, listener) -> None:
        try:
            # init var
            deviceId = DeviceManagement.resolveDeviceUniqueId(self._deviceIdentifier)
            operationName = self._awsShadowNameConstructor(deviceId, ALLSHADOWNAMES, 'update/delta')

            def callbackasync(context, updateDelta: UpdateDelta):
                if inspect.iscoroutinefunction(listener):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                    loop.run_until_complete(listener(context, updateDelta))
                    loop.close()
                else:
                    listener(context, updateDelta)

            def callback(client, userdata, message: MQTTMessage):
                # get info from topic
                topic = message.topic
                deviceId = topic.split('/')[2]
                stateName = topic.split('/')[5]
                # by default the value will follow sdk test unit
                acc = 'neuko'
                pro = 'device-sdk'
                dev = 'test'
                if (deviceId != "neuko-device-sdk-test"):
                    arr = deviceId.split('-', 1) # produces [accountid, projectId-deviceId]
                    acc = arr[0] 
                    arr = arr[1].split('-', 1) # produces [projectid, deviceId]
                    pro = arr[0]
                    dev = arr[1]

                # The payload is an AWS update/delta
                payload = json.loads(message.payload)

                # clientToken is an optional, so better parse if it exists
                clientToken = None
                if 'clientToken' in payload: clientToken = payload['clientToken']

                data = AwsUpdateDelta(
                    payload['state'],
                    payload['metadata'],
                    payload['timestamp'],
                    payload['version'],
                    clientToken
                )

                # create standardize delta object
                updateDelta = UpdateDelta(
                    DeviceIdentifier(acc, pro, None, dev),
                    stateName,
                    data.state
                )

                logger.debug(f'onTelemetricStateChangedRequest: Delta callback from topic {message.topic} - {message.mid}')
                # if inspect.iscoroutinefunction(listener): await listener(context, updateDelta)
                # listener(context, updateDelta)
                threading.Thread(target=callbackasync, args=(context, updateDelta), daemon=True).start()

            await self.subscribe(operationName, callback)
        except Exception as ex:
            logger.error(ex)
            raise Exception(ex)
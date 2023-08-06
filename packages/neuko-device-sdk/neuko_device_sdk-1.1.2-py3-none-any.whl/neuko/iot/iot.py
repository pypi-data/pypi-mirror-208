
import paho.mqtt.client as Mqtt
from paho.mqtt.client import MQTTMessage
import aiohttp
import asyncio
import threading
import inspect
from abc import ABC, abstractmethod
from ..utility.logger import Logger
from .model import Provider
from ..device.model import DeviceIdentifier
from ..connection.model import Certificate, Configuration, ConfigurationProtocol
from ..connection.certificateManagement import CertificateManagement
from ..connection.connectionManagement import ConnectionManagement

logger = Logger("IoT").set()
SLEEP_DURATION: float   = 100e-3

class IoT(ABC):

    # def __new__(cls, *arg, **kwargs):
    #     # get all coros 
    #     parent_coros = inspect.getmembers(IoT, predicate=inspect.iscoroutinefunction)

    #     # check if parent's coros are still coros in a child
    #     for coro in parent_coros:
    #         child_method = getattr(cls, coro[0])
    #         if not inspect.iscoroutinefunction(child_method):
    #             raise RuntimeError('The method %s must be a coroutine' % (child_method,))

    #     return super(IoT, cls).__new__(cls, *arg, **kwargs)

    def __init__(self, deviceIdentifier: DeviceIdentifier, connectionManager: ConnectionManagement, certificateManager: CertificateManagement) -> None:
        self._deviceIdentifier: DeviceIdentifier = deviceIdentifier
        self._certificateManager: CertificateManagement = certificateManager
        self._connectionManager: ConnectionManagement = connectionManager
        self._contextCertificate: Certificate = None
        self._contextConfiguration: Configuration = None
        self._connecting = False
        self._mqttClient: Mqtt.Client = None
        self._httpClient: aiohttp.ClientSession = None
        self._topics: list = []

    @property
    def connected(self):
        if self._mqttClient == None: return False
        else: return self._mqttClient.is_connected()

    @abstractmethod
    async def connectMqttClient(self, configurationProtocol: ConfigurationProtocol, connectionCertificates: Certificate) -> Mqtt.Client:
        """
        This function connects to the MQTT broker and returns the MQTT client. It is very important to use non-blocking connection in manner
        
        :param configurationProtocol: The protocol that defines the connection to the MQTT broker
        :type configurationProtocol: ConfigurationProtocol
        :param connectionCertificates: The certificates used to connect to the MQTT broker
        :type connectionCertificates: Certificate
        """
        pass

    @abstractmethod
    async def connectHttpClient(self, configurationProtocol: ConfigurationProtocol, connectionCertificates: Certificate) -> aiohttp.ClientSession:
        """
        It takes a ConfigurationProtocol and a Certificate and returns an HttpClient. It is very important to use non-blocking connection in manner
        
        :param configurationProtocol: The protocol that will be used to configure the HttpClient
        :type configurationProtocol: ConfigurationProtocol
        :param connectionCertificates: The certificates used to connect to the server
        :type connectionCertificates: Certificate
        """
        pass

    @abstractmethod
    async def fetchAllTelemetricStateNames(self) -> list:
        """
        This function returns an array of strings that represent the names of all the telemetric states
        that are available for the device with the given identifier
        """
        pass

    @abstractmethod
    async def pullTelemetricState(self, stateName: str) -> object:
        """
        This function pulls the telemetric state from the device

        :param stateName: The name of the state to pull
        :type stateName: str
        """
        pass

    @abstractmethod
    async def pushTelemetricState(self, stateName: str, state: object) -> None:
        """
        Push a telemetric state to the device
        
        :param stateName: The name of the state to push
        :type stateName: str
        :param state: The state object to be pushed
        :type state: object
        """
        pass

    @abstractmethod
    async def timestreamStorage(self, stateName: str, state: object) -> None:
        """
        This function is called by the device whenever a state is updated
        
        :param stateName: The name of the state you want to store
        :type stateName: str
        :param state: The state object to be stored
        :type state: object
        """
        pass

    @abstractmethod
    async def onTelemetricStateChangedRequest(self, context, listener) -> None:
        """
        This function is called when the telemetric state of a device changes
        
        :param context: The context object that was passed to the request handler
        :param listener: The listener is a function that will be called when the telemetric state
        changes
        :type listener: function
        """
        pass

    def _onMqttConnect(self, client, userdata, flags, rc) -> None:
        """
        This function is called when the MQTT client is connected
        """
        logger.debug(f'_onMqttConnect: flags = {flags} ; Rc = {rc};')
        self._connecting = False

    def _onMqttDisconnected(self, client, userdata, rc) -> None:
        """
        When the Mqtt client disconnects, log a message
        
        :param client: the client instance for this callback
        :param userdata: user data of any type
        :param rc: The connection result
        """
        if rc != 0:
            logger.error("_onMqttDisconnected: Unexpected disconnection")
        else:
            logger.debug("_onMqttDisconnected: Mqtt client disconnected")

    def _onMqttMessage(self, client, userdata, message: MQTTMessage) -> None:
        # message is a class of MQTTMessage
        # - topic, payload, qos, retain
        logger.debug("_onMqttMessage: Received message from topic %s", message.topic)

    def _onMqttLog(client, userdata, level, buf):
        logger.debug(f'_onMqttLog: {str(buf)}')

    def _onMqttSubscribe(self, client, userdata, mid, granted_qos):
        logger.debug(f'_onMqttSubscribe: userdata = {userdata} ; mid = {mid} ; granter_qos = {granted_qos}')
    
    def _onMqttPublish(context, client, userdata, mid):
        logger.debug(f'_onMqttPublish: {userdata}')

    async def loadContextCertificate(self, clientProvider: Provider) -> None:
        """
        Load the context certificate from the certificate manager
        
        :param clientProvider: Provider.BOOTSTRAP or Provider.PERPETUAL
        :type clientProvider: Provider
        """
        try:
            if clientProvider == Provider.BOOTSTRAP:
                logger.debug("loadContextCertificate: Loading bootstrap certificates")
                self._contextCertificate = await self._certificateManager.getBootstrapCertificates(self._deviceIdentifier)
            else:
                logger.debug("loadContextCertificate: Loading perpetual certificates")
                self._contextCertificate = await self._certificateManager.getPerpetualCertificates(self._deviceIdentifier)
        except:
            logger.error("loadContextCertificate: Error loading context certificates")
            raise Exception("OperationError")

    async def loadContextConfiguration(self, clientProvider: Provider) -> None:
        """
        The function is responsible for loading the context configuration.
        
        :param clientProvider: Provider.BOOTSTRAP or Provider.PERPETUAL
        :type clientProvider: Provider
        """
        try:
            if clientProvider == Provider.BOOTSTRAP:
                logger.debug("loadContextConfiguration: Loading bootstrap certificates")
                self._contextConfiguration = self._connectionManager.getBootstrapConnectionConfiguration()
            else:
                logger.debug("loadContextConfiguration: Loading perpetual certificates")
                self._contextConfiguration = await self._connectionManager.getPerpetualConnectionConfiguration(self._deviceIdentifier)
                # logger.debug(f'loadContextConfiguration: {json.dumps(self._contextConfiguration)}')
        except:
            logger.error("loadContextConfiguration: Error loading context configuration")
            raise Exception("OperationError")

    async def connect(self) -> bool:
        """
        This function is used to connect to the broker
        :return: The return value is a coroutine object.
        """
        try:
            logger.debug(self._contextConfiguration)
            if self._connecting ==  False:
                await self.connectMqttClient(self._contextConfiguration["connection"]["protocols"], self._contextCertificate)
                await self.connectHttpClient(self._contextConfiguration["connection"]["protocols"], self._contextCertificate)
                logger.info("connect: Http session established")

                # loop
                self._mqttClient.enable_logger(logger=logger)
                self._mqttClient.on_connect = self._onMqttConnect
                self._mqttClient.on_message = self._onMqttMessage
                self._mqttClient.on_disconnect = self._onMqttDisconnected
                self._mqttClient.on_log = self._onMqttLog
                self._mqttClient.on_subscribe = self._onMqttSubscribe
                self._mqttClient.on_publish = self._onMqttPublish
                self._mqttClient.loop_start()
                
                # try to connect
                trial = 0
                while trial < 30:
                    await asyncio.sleep(1)
                    if self._mqttClient.is_connected():
                        trial = 100
                        logger.debug("connect: MQTT connection established")
                        return True
                    else:
                        trial += 1
                        logger.debug("connect: Establishing MQTT connection...")

                raise Exception("MqttConnectError")
            else:
                logger.debug("connect: Connection to broker is establishing")
                return False
        except Exception as ex:
            logger.error("connect: Error connecting to broker")
            raise Exception("ex")

    async def disconnect(self) -> None:
        """
        It disconnects from the broker and cleans up the MQTT client
        """
        for topic in self._topics[:]:
            logger.debug(f'disconnect: Unsubscribing topic {topic}')
            await self.unsubscribe(topic)

        if self.connected:
            self._mqttClient.disconnect()
            self._mqttClient.loop_stop()

        if self._httpClient != None: await self._httpClient.close()
        logger.info("disconnect: Disconnected from broker & cleaned")

    async def subscribe(self, topic: str, listener = None) -> None:
        """
        Subscribe to a topic
        
        :param topic: The topic string to which the client subscribes
        :type topic: str
        :param listener: The callback function that will be called when a message is received
        """
        try:
            if topic not in self._topics:
                if listener != None:

                    def callback(client, userdata, message):
                        logger.debug("subscribe#callback: Spawn a new thread to run listener")

                        def invokeListener():

                            if inspect.iscoroutinefunction(listener):
                                loop = asyncio.new_event_loop()
                                asyncio.set_event_loop(loop)

                                loop.run_until_complete(listener(client, userdata, message))
                                loop.close()
                            else:
                                listener(client, userdata, message)
                            
                        threading.Thread(target=invokeListener, daemon=True).start()

                    self._mqttClient.message_callback_add(f'{topic}', callback)
                    logger.debug("subscribe: Listener is attached to topic %s", topic)
                resSub = self._mqttClient.subscribe(topic)
                await asyncio.sleep(1)
                logger.debug(f'subscribe: resSub = {resSub}')
                if resSub[0] != Mqtt.MQTT_ERR_SUCCESS:
                    raise Exception("MqttSubscribeError")
                logger.info("subscribe: Topic %s is subscribed", topic)
                self._topics.append(topic)
            else:
                logger.debug(f'subscribe: {topic} is already subscribed')
        except Exception as ex:
            logger.error(ex)
            raise Exception(ex)

    async def unsubscribe(self, topic: str) -> None:
        """
        Remove the listener from the topic and unsubscribe from the topic
        
        :param topic: The topic to which the listener is subscribed
        :type topic: str
        """
        self._mqttClient.message_callback_remove(topic)
        logger.debug("unsubscribe: Listener has been removed from topic %s", topic)
        self._mqttClient.unsubscribe(topic)
        logger.info("unsubscribe: Topic %s is unsubscribed", topic)
        try:
            self._topics.remove(topic)
        except ValueError:
            pass

    async def publish(self, topic: str, message: str) -> None:
        """
        It publishes a message to a topic.
        
        :param topic: The topic of the message
        :type topic: str
        :param message: The message to be published
        :type message: str
        """
        try:
            resPub = self._mqttClient.publish(topic, message, qos=1, retain=False)
            logger.debug(f'publish: resPub = {resPub}')
            loop = 0
            while loop < 5:
                await asyncio.sleep(SLEEP_DURATION)
                if resPub.is_published():
                    logger.info(f"publish: Published to {topic}")
                    loop = 100
                    return None
                else:
                    logger.debug("publish: Pending publish message")
                    loop += SLEEP_DURATION
            raise Exception('TimeoutError')
        except Exception as ex:
            logger.error(f'publish: {ex}')
            raise Exception(ex)
        

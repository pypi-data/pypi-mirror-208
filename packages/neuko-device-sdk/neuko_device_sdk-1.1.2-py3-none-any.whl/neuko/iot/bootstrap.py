import ssl
import paho.mqtt.client as Mqtt
import aiohttp
from .iot import IoT
from ..utility.logger import Logger
from ..connection.model import ConfigurationProtocol, Certificate
from ..device.deviceManagement import DeviceManagement
from ..connection.certificateManagement import CertificateManagement
from ..connection.connectionManagement import ConnectionManagement
from ..device.model import DeviceIdentifier

logger = Logger("BootstrapClient").set()

class BootstrapClient(IoT):

    def __init__(self, deviceIdentifier: DeviceIdentifier, connectionManager: ConnectionManagement, certificateManager: CertificateManagement) -> None:
        super().__init__(deviceIdentifier, connectionManager, certificateManager)

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
            self._mqttClient = Mqtt.Client(
                client_id=DeviceManagement.resolveClientId(self._deviceIdentifier),
                clean_session=True
            )
            logger.debug("connectMqttClient: Created MQTT client instance")
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
        raise Exception("IllegalMethod")

    async def pullTelemetricState(self, stateName: str) -> object:
        raise Exception("IllegalMethod")

    async def pushTelemetricState(self, stateName: str, state: object) -> None:
        raise Exception("IllegalMethod")

    async def timestreamStorage(self, stateName: str, state: object) -> None:
        raise Exception("IllegalMethod")

    async def onTelemetricStateChangedRequest(self, context, listener) -> None:
        raise Exception("IllegalMethod")
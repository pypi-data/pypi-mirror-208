from ..iot.model import Provider

class Certificate:
    def __init__(self, certificateAuthority: str, chainCertificate: str, privateKey: str) -> None:
        self.certificateAuthority = certificateAuthority
        self.chainCertificate = chainCertificate
        self.privateKey = privateKey

class MqttOptions(dict):
    def __init__(self, rejectUnauthorized: bool, ALPNProtocols: list) -> None:
        dict.__init__(self, rejectUnauthorized=rejectUnauthorized, ALPNProtocols=ALPNProtocols)

class MqttConfiguration(dict):
    def __init__(self, endpoint: str, port: int, options: MqttOptions) -> None:
        dict.__init__(self, endpoint=endpoint, port=port, options=options)

class HttpOptions(dict):
    def __init__(self, keepAlive: bool, rejectUnauthorized: bool, ALPNProtocols: list) -> None:
        dict.__init__(self, keepAlive=keepAlive, rejectUnauthorized=rejectUnauthorized, ALPNProtocols=ALPNProtocols)

class HttpConfiguration(dict):
    def __init__(self, endpoint: str, port: int, options: HttpOptions) -> None:
        dict.__init__(self, endpoint=endpoint, port=port, options=options)

class ConfigurationProtocol(dict):
    def __init__(self, mqtt: MqttConfiguration, http: HttpConfiguration) -> None:
        dict.__init__(self, mqtt=mqtt, http=http)

class Connection(dict):
    def __init__(self, provider: Provider, protocols: ConfigurationProtocol) -> None:
        dict.__init__(self, provider=provider, protocols=protocols)

class LocalConnection(dict):
    def __init__(self, ownershipToken: str) -> None:
        dict.__init__(self, ownershipToken=ownershipToken)

class Configuration(dict):
    def __init__(self, tier: str, localConnection: LocalConnection, connection: Connection) -> None:
        dict.__init__(self, tier=tier, localConnection=localConnection, connection=connection)
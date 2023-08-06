import pika.spec
from pika import PlainCredentials, ConnectionParameters, BasicProperties
from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection
import json

class AmqpImageRepository():
    def __init__(self,
                 user: str,
                 password: str,
                 dns: str,
                 exchange: str,
                 port: int = 5672,
                 path: str = '/',
                 heartbeat: int = 0,
                 blocked_connection_timeout: int = None
                 ):
        self.user = user
        self.password = password
        self.dns = dns
        self.exchange = exchange
        self.port = port
        self.path = path
        self.heartbeat = heartbeat
        self.blocked_connection_timeout = blocked_connection_timeout
        self._connection: BlockingConnection
        self._channel: BlockingChannel

        self._connectToChannel()

    def _connectToChannel(self) -> BlockingChannel:

        credentials = PlainCredentials(
            username=self.user,
            password=self.password
        )
        parameters = ConnectionParameters(
                host=self.dns,
                port=self.port,
                virtual_host='/',
                credentials=credentials,
                heartbeat=self.heartbeat,
                blocked_connection_timeout=self.blocked_connection_timeout,
            )
        self._connection = BlockingConnection(
            parameters=parameters
        )

        self._channel = self._connection.channel()

    def _testIfConnectIsClose(self) -> bool:
        return self._connection is None or self._connection.is_closed

    def sendMessageToChannel(self, message: str, routing_key: str = ''):
        if self._testIfConnectIsClose():
            self._connectToChannel()

        self._channel.basic_publish(
            exchange=self.exchange,
            routing_key=routing_key,
            body=json.dumps(message),
            properties=BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            )
        )

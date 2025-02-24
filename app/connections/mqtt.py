from paho.mqtt.client import Client
from paho.mqtt.enums import CallbackAPIVersion

class MQTTClient:
    broker: str = None
    port: int = None
    username: str = None
    password: str = None
    client: Client = None

    def __init__(self, client_id, broker, port, username, password):
        self.broker = broker
        self.port = port
        self.username = username
        self.password = password

        self.client = Client(CallbackAPIVersion.VERSION2, client_id)
    
    def connect(self):
        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)
        self.client.connect(self.broker, self.port)

    def publish(self, topic, payload):
        self.client.publish(topic, payload)

    def start(self):
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()


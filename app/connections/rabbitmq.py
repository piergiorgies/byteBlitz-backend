import pika
import json
from app.config import settings

class RabbitMQConnection:
    host: str
    port: int
    user: str
    password: str

    connection: pika.BlockingConnection | None

    def __init__(self, host: str, port: int, user: str, password: str):
        self.host = host
        self.port = port
        self.user = user
        self.password = password

        self.connection = None

    def try_connection(self):
        if self.connection != None and self.connection.is_open:
            return
        
        try:
            credentials = pika.PlainCredentials(self.user, self.password) 
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host, credentials=credentials))
        except Exception as ex:
            print(f'Error while connecting to RabbitMQ: {ex}')

    def try_send_to_queue(self, queue_name: str, body):
        connection_open = True
        if self.connection == None or self.connection.is_closed:
            connection_open = False
            for _ in range(3):
                self.try_connection()

                if self.connection != None and self.connection.is_open:
                    connection_open = True
                    break

        if not connection_open:
            return

        try:
            channel = self.connection.channel()
            channel.queue_declare(queue=queue_name, durable=True)
            channel.basic_publish(exchange='', routing_key=queue_name, body=json.dumps(body))
        except Exception as ex:
            print(f'Error while sending the message to the queue: {ex}')

rabbitmq_connection = RabbitMQConnection(
    settings.RABBITMQ_HOST, 
    settings.RABBITMQ_PORT, 
    settings.RABBITMQ_USER, 
    settings.RABBITMQ_PASS
)
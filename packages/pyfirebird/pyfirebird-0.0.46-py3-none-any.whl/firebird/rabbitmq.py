import pika
import json
from copy import copy

def get_connection( *, username, password, host, port, heartbeat):
    credentials = pika.PlainCredentials(username, password)
    return pika.BlockingConnection(pika.ConnectionParameters(
        host=host,
        port=port,
        credentials=credentials,
        heartbeat=heartbeat
    ))


class RabbitMQ:
    def __init__(self, *, connection, topic):
        self.topic = topic
        self.error_topic = f"{topic}-error"

        self.stop_requested = False  # has the client asked to stop consuming data?
        self.connection = connection
        self.channel = self.connection.channel()
        self.channel.basic_qos(prefetch_count=1)

    def stop_consume(self):
        self.stop_consume = True
    
    def close(self):
        if self.channel is not None:
            self.channel.close()
            self.channel = None
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def initialize(self):
        self.channel.queue_declare(queue=self.topic, durable=True)
        self.channel.queue_declare(queue=self.error_topic, durable=True)

    def produce(self, json_body):
        body = json.dumps(json_body).encode('utf-8')
        self.channel.basic_publish(
            exchange='', 
            routing_key=self.topic, 
            body=body,
            properties=pika.BasicProperties(
                delivery_mode = 2, # make message persistent
            )
        )

    def produce_error(self, json_body, exception):
        effective_json_body = copy(json_body)
        if "failed_reason" not in effective_json_body:
            effective_json_body["failed_reason"] = []
        
        effective_json_body["failed_reason"].append(str(exception))
        body = json.dumps(effective_json_body).encode('utf-8')

        self.channel.basic_publish(
            exchange='', 
            routing_key=self.error_topic, 
            body=body,
            properties=pika.BasicProperties(
                delivery_mode = 2, # make message persistent
            )
        )
    
    def consume(self, on_message, quit_requested):
        # on_message: called when there is a message coming
        for method_frame, properties, body in self.channel.consume(
            self.topic, auto_ack=False, exclusive=False,
            inactivity_timeout = 10
        ):
            if quit_requested.value:
                # we are not acking the message so it will not be lost
                break
            
            if method_frame is None:
                # no message
                continue

            json_body = json.loads(body.decode('utf-8'))

            try:
                on_message(json_body)
            except Exception as e:
                # on failure, put in the error queue
                self.produce_error(json_body, e)
            finally:
                self.channel.basic_ack(method_frame.delivery_tag)


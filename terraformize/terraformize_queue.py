import pika
import os
import sys
import json


def extract_params_from_queue_json(message_json: bytes) -> dict:
    """
    Checks if auth is enabled by making sure if there is a username & password pair or a token configured

    Arguments:
        :param message_json: the json message as read from the rabbit queue to filter down to params

    Returns:
        :return decoded_dict: the name of the folder where the module is used
    """
    decoded_dict = json.loads(message_json.decode())
    return decoded_dict


class RabbitWorker:

    def __init__(self, rabbit_url_connection_string: str, read_queue: str = "terraformize_read_queue",
                 reply_queue: str = "terraformize_reply_queue"):
        """
        Checks if auth is enabled by making sure if there is a username & password pair or a token configured

        Arguments:
            :param username: the possible username for authentication
            :param password: the possible password for authentication
            :param token: the possible token for authentication

        Returns:
            :return auth_required: True if auth is enabled, False otherwise
        """
        self.read_queue = read_queue
        self.reply_queue = reply_queue
        self.consume_connection = pika.BlockingConnection(pika.connection.URLParameters(rabbit_url_connection_string))
        self.publish_connection = pika.BlockingConnection(pika.connection.URLParameters(rabbit_url_connection_string))
        self.consume_channel = self.consume_connection.channel()
        self.consume_channel.queue_declare(queue=read_queue, durable=True)
        self.publish_channel = self.publish_connection.channel()
        self.publish_channel.queue_declare(queue=reply_queue, durable=True)

    def callback(self, ch, method, properties, body: bytes):
        """
        the callback that actually reads & process a message read from the queue then publishes the run result to the
        reply_queue

        Arguments:
            :param ch: the channel the callback is using, taken internally from pika
            :param method: the method the callback is using, taken internally from pika
            :param properties: the queue properties, taken internally from pika
            :param body: the json body in bytes form of the message read from the the queue

        Exceptions:
            :except Exception: will print the error and exit the container with exit code 2
        """
        try:
            # TODO actual code here that reads the 'body' of the message and runs the proper terraformize command then
            #  publishes the run result to the reply_queue
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print("RabbitMQ read from queue related issues - dropping container")
            print(e, file=sys.stderr)
            os._exit(2)

    def read_from_queue(self):
        """
        Will start consuming messages from a queue

        Exceptions:
            :except Exception: will print the error and exit the container with exit code 2
        """
        try:
            self.consume_channel.basic_qos(prefetch_count=1)
            self.consume_channel.basic_consume(queue=self.read_queue, on_message_callback=self.callback)
        except Exception as e:
            print("RabbitMQ read from queue related issues - dropping container")
            print(e, file=sys.stderr)
            os._exit(2)

    def respond_to_queue(self, message: bytes):
        """
        Will publish the run response to the reply queue

        Arguments:
            :param message: the message to publish to the reply queue
        """
        self.publish_channel.basic_publish(
            exchange='',
            routing_key=self.reply_queue,
            body=bytes(json.dumps(message)),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            )
        )

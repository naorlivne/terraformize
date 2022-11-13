import pika
import os
import sys
import json
from terraformize.terraformize_configure import *
from terraformize.terraformize_terraform_wrapper import *


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
            :param rabbit_url_connection_string: url connection string to connect to RabbitMQ
            :param read_queue: queue name to read from
            :param reply_queue: queue name to reply the terraform run results to

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
            body_json = extract_params_from_queue_json(body)
            if body_json["run_type"] == "apply":
                terraform_object = Terraformize(body_json["workspace"],
                                                configuration["terraform_modules_path"] + "/" +
                                                body_json["module_folder"],
                                                terraform_bin_path=configuration["terraform_binary_path"])
                terraform_return_code, terraform_stdout, terraform_stderr = \
                    terraform_object.apply(body_json["run_variables"], configuration["parallelism"])
                return_body = {
                    "init_stdout": terraform_object.init_stdout,
                    "init_stderr": terraform_object.init_stderr,
                    "stdout": terraform_stdout,
                    "stderr": terraform_stderr,
                    "uuid": body_json["uuid"],
                    "exit_code": terraform_return_code
                }
            elif body_json["run_type"] == "destroy":
                terraform_object = Terraformize(body_json["workspace"],
                                                configuration["terraform_modules_path"] + "/" +
                                                body_json["module_folder"],
                                                terraform_bin_path=configuration["terraform_binary_path"])
                terraform_return_code, terraform_stdout, terraform_stderr = \
                    terraform_object.destroy(body_json["run_variables"], configuration["parallelism"])
                return_body = {
                    "init_stdout": terraform_object.init_stdout,
                    "init_stderr": terraform_object.init_stderr,
                    "stdout": terraform_stdout,
                    "stderr": terraform_stderr,
                    "uuid": body_json["uuid"],
                    "exit_code": terraform_return_code
                }
            elif body_json["run_type"] == "plan":
                terraform_object = Terraformize(body_json["workspace"],
                                                configuration["terraform_modules_path"] + "/" +
                                                body_json["module_folder"],
                                                terraform_bin_path=configuration["terraform_binary_path"])
                terraform_return_code, terraform_stdout, terraform_stderr = \
                    terraform_object.plan(body_json["run_variables"], configuration["parallelism"])
                return_body = {
                    "init_stdout": terraform_object.init_stdout,
                    "init_stderr": terraform_object.init_stderr,
                    "stdout": terraform_stdout,
                    "stderr": terraform_stderr,
                    "uuid": body_json["uuid"],
                    "exit_code": terraform_return_code
                }
            else:
                print("run_type must be one of apply/destory/plan, current value is " + str(body_json["run_type"]))
                raise ValueError
            self.respond_to_queue(return_body)
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

    def respond_to_queue(self, message: dict):
        """
        Will publish the run response to the reply queue

        Arguments:
            :param message: the message to publish to the reply queue
        """
        self.publish_channel.basic_publish(
            exchange='',
            routing_key=self.reply_queue,
            body=json.dumps(message).encode(),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            )
        )

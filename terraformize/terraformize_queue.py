import pika


class RabbitWorker:

    def __init__(self, rabbit_url_connection_string: str, read_queue: str = "terraformize_read_queue",
                 reply_queue: str = "terraformize_reply_queue"):
        """
        Will create a rabbit connection & declare it's queues

        Arguments:
            :param rabbit_url_connection_string: the URL connection string to RabbitMQ, for more info look at
            https://pika.readthedocs.io/en/stable/modules/parameters.html#urlparameters
            :param read_queue: the queue to read from
            :param reply_queue: the queue to respond with the results of the run to
        """
        self.read_queue = read_queue
        self.reply_queue = reply_queue
        self.consume_connection = pika.BlockingConnection(pika.connection.URLParameters(rabbit_url_connection_string))
        self.publish_connection = pika.BlockingConnection(pika.connection.URLParameters(rabbit_url_connection_string))
        self.consume_channel = self.consume_connection.channel()
        self.consume_channel.queue_declare(queue=read_queue, durable=True)
        self.publish_channel = self.publish_connection.channel()
        self.publish_channel.queue_declare(queue=reply_queue, durable=True)

    def callback(self, ch, method, properties, body: str):
        """
        the callback that actually reads & process a message read from the queue then publishes the run result to the
        reply_queue

        Arguments:
            :param ch: the channel the callback is using, taken internally from pika
            :param method: the method the callback is using, taken internally from pika
            :param properties: the queue properties, taken internally from pika
            :param body: the json body in string form of the message read from the the queue
        """
        # TODO actual code here that reads the 'body' of the message and runs the proper terraformize command then
        #  publishes the run result to the reply_queue
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def read_from_queue(self):
        """
        Will read a message from a queue
        """
        self.consume_channel.basic_qos(prefetch_count=1)
        self.consume_channel.basic_consume(queue=self.read_queue, on_message_callback=self.callback)

    def respond_to_queue(self, message: bytes):
        """
        Will publish the run response to the reply queue

        Arguments:
            :param message: the message to publish to the reply queue
        """
        self.publish_channel.basic_publish(
            exchange='',
            routing_key=self.reply_queue,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            )
        )

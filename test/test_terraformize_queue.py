from unittest import TestCase
from terraformize.terraformize_queue import *
import os


# this will run all tests in relation to the location of this file so that the test_terraform folder will catch
# the correct path
test_files_location = os.getenv("TEST_FILES_LOCATION", os.path.realpath(__file__).rsplit("/", 1)[0]) + "/test_terraform"
test_bin_location = os.getenv("TEST_BIN_LOCATION", "/usr/bin/terraform")
rabbit_url_connection_string = os.getenv("TEST_RABBIT_URL_CONNECTION_STRING", "amqp://rabbit")


class BaseTests(TestCase):
    def test_extract_params_from_queue_json(self):
        test_message = """
        {
            "test_key": "test_value"
        }
        """
        test_message = test_message.encode()
        extracted_message = extract_params_from_queue_json(test_message)
        self.assertEqual(extracted_message, {"test_key": "test_value"})

    def test_rabbit_worker_init_sane_defaults(self):
        rabbit_init_test = RabbitWorker(rabbit_url_connection_string)
        self.assertEqual(rabbit_init_test.read_queue, "terraformize_read_queue")
        self.assertEqual(rabbit_init_test.reply_queue, "terraformize_reply_queue")
        self.assertTrue(rabbit_init_test.consume_channel.is_open)
        self.assertTrue(rabbit_init_test.publish_channel.is_open)
        self.assertTrue(rabbit_init_test.publish_connection.is_open)
        self.assertTrue(rabbit_init_test.consume_connection.is_open)
        self.assertEqual(rabbit_init_test.declared_read_queue.method.queue, "terraformize_read_queue")
        self.assertEqual(rabbit_init_test.declared_reply_queue.method.queue, "terraformize_reply_queue")
        self.assertTrue(rabbit_init_test.declared_reply_queue.method.NAME, "Queue.DeclareOk")
        self.assertTrue(rabbit_init_test.declared_read_queue.method.NAME, "Queue.DeclareOk")

    def test_rabbit_worker_init_custom_queue_names(self):
        rabbit_init_test = RabbitWorker(rabbit_url_connection_string, "terraformize_read_queue_test",
                                        "terraformize_reply_queue_test")
        self.assertEqual(rabbit_init_test.read_queue, "terraformize_read_queue_test")
        self.assertEqual(rabbit_init_test.reply_queue, "terraformize_reply_queue_test")
        self.assertEqual(rabbit_init_test.declared_read_queue.method.queue, "terraformize_read_queue_test")
        self.assertEqual(rabbit_init_test.declared_reply_queue.method.queue, "terraformize_reply_queue_test")
        self.assertTrue(rabbit_init_test.declared_reply_queue.method.NAME, "Queue.DeclareOk")
        self.assertTrue(rabbit_init_test.declared_read_queue.method.NAME, "Queue.DeclareOk")

    def test_rabbit_worker_callback_apply(self):
        pass

    def test_rabbit_worker_callback_destroy(self):
        pass

    def test_rabbit_worker_callback_plan(self):
        pass

    def test_rabbit_worker_callback_raise_error_on_wrong_run_type(self):
        pass

    def test_rabbit_worker_callback_raise_error_on_connection_issue(self):
        pass

    def test_rabbit_worker_read_from_queue(self):
        pass

    def test_rabbit_worker_read_from_queue_raise_error_on_connection_issue(self):
        pass

    def test_rabbit_worker_respond_to_queue(self):
        test_message = {
            "test_key": "test_value"
        }
        rabbit_init_test = RabbitWorker(rabbit_url_connection_string, reply_queue="reply_queue_test")
        rabbit_init_test.respond_to_queue(test_message)
        method_frame, header_frame, body = rabbit_init_test.publish_channel.basic_get("reply_queue_test")
        if method_frame:
            rabbit_init_test.publish_channel.basic_ack(method_frame.delivery_tag)
        self.assertEqual(body, b'{"test_key": "test_value"}')

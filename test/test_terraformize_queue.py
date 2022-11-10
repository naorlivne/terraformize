from unittest import TestCase
from terraformize.terraformize_queue import *
import os
from flask import request
import httpretty


# this will run all tests in relation to the location of this file so that the test_terraform folder will catch
# the correct path
test_files_location = os.getenv("TEST_FILES_LOCATION", os.path.realpath(__file__).rsplit("/", 1)[0]) + "/test_terraform"
test_bin_location = os.getenv("TEST_BIN_LOCATION", "/usr/bin/terraform")


class BaseTests(TestCase):
    def test_extract_params_from_queue_json(self):
        pass

    def test_rabbit_worker_init(self):
        pass

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

    def test_rabbit_worker_callback_read_from_queue(self):
        pass

    def test_rabbit_worker_callback_read_from_queue_raise_error_on_connection_issue(self):
        pass

    def test_rabbit_worker_callback_respond_to_queue(self):
        pass

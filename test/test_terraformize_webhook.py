from unittest import TestCase
from terraformize.terraformize_webhook import *
import uuid
import json
import requests_mock


class BaseTests(TestCase):

    def test_terraformize_webhook_check_return_proper_uuid_and_json(self):
        test_uuid_str, test_uuid_json = create_request_uuid()
        test_uuid = uuid.UUID(str(test_uuid_str))
        expected_json = json.dumps({
            'request_uuid': str(test_uuid)
        })
        self.assertEqual(str(test_uuid), test_uuid_str)
        self.assertEqual(test_uuid_json, expected_json)

    def test_terraformize_webhook_check_send_webhook_result(self):
        with requests_mock.Mocker() as request_mocker:
            request_mocker.post('https://my_total_real_webhook_url/whatever',
                                status_code=200)
            send_webhook_result("https://my_total_real_webhook_url/whatever", "test1", "test2", "test3", "test4", 0,
                                "ec743bc4-0724-4f44-9ad3-5814071faddf")
            webhook_history = request_mocker.request_history
            webhook_request_body = webhook_history[0].body
            self.assertTrue(request_mocker.called)
            self.assertEqual(request_mocker.call_count, 1)
            self.assertEqual('{"init_stdout": "test1", "init_stderr": "test2", "stdout": "test3", "stderr": "test4", '
                             '"terraform_return_code": 0, "request_uuid": "ec743bc4-0724-4f44-9ad3-5814071faddf"}',
                             webhook_request_body)

from unittest import TestCase, mock
from terraformize.terraformize_configure import *


class BaseTests(TestCase):

    def test_terraformize_configure_sane_defaults(self):
        reply = read_configurations()
        expected_reply = {
            'auth_enabled': False,
            'basic_auth_user': None,
            'basic_auth_password': None,
            'parallelism': 10,
            'auth_token': None,
            'terraform_binary_path': None,
            'terraform_modules_path': '/www/terraform_modules'
        }
        self.assertEqual(reply, expected_reply)

    def test_terraformize_configure_read_envar(self):
        with mock.patch('os.environ', {"AUTH_TOKEN": "my_super_secret_token123"}):
            reply = read_configurations()
            expected_reply = {
                'auth_enabled': True,
                'basic_auth_user': None,
                'basic_auth_password': None,
                'parallelism': 10,
                'auth_token': "my_super_secret_token123",
                'terraform_binary_path': None,
                'terraform_modules_path': '/www/terraform_modules'
            }
            self.assertEqual(reply, expected_reply)

    def test_terraformize_configure_read_custom_config_folder(self):
        reply = read_configurations(config_folder="test/test_config")
        expected_reply = {
            'auth_enabled': True,
            'basic_auth_user': None,
            'basic_auth_password': None,
            'parallelism': 10,
            'auth_token': "my_super_secret_token",
            'terraform_binary_path': None,
            'terraform_modules_path': '/www/terraform_modules123'
        }
        self.assertEqual(reply, expected_reply)

    def test_terraformize_auth_enabled_false_all(self):
        reply = auth_enabled(None, None, None)
        self.assertFalse(reply)

    def test_terraformize_auth_enabled_false_username_only(self):
        reply = auth_enabled(None, "test", None)
        self.assertFalse(reply)

    def test_terraformize_auth_enabled_false_pass_only(self):
        reply = auth_enabled("test", None, None)
        self.assertFalse(reply)

    def test_terraformize_auth_enabled_true_token(self):
        reply = auth_enabled(None, None, "test")
        self.assertTrue(reply)

    def test_terraformize_auth_enabled_true_basic_auth(self):
        reply = auth_enabled("test", "test", None)
        self.assertTrue(reply)

    def test_terraformize_auth_enabled_true_all(self):
        reply = auth_enabled("test", "test", "test")
        self.assertTrue(reply)

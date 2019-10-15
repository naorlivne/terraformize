from unittest import TestCase, mock
from terraformize.terraformize_configure import *


class BaseTests(TestCase):

    def test_terrformize_configure_sane_defaults(self):
        reply = read_configurations()
        expected_reply = {
            'basic_auth_user': None,
            'basic_auth_password': None,
            'auth_token': None,
            'max_timeout': 600,
            'terraform_binary_path': None,
            'terraform_modules_path': '/www/terraform_modules'
        }
        self.assertEqual(reply, expected_reply)

    def test_terrformize_configure_read_envar(self):
        with mock.patch('os.environ', {"MAX_TIMEOUT": "300", "AUTH_TOKEN": "my_super_secret_token"}):
            reply = read_configurations()
            expected_reply = {
                'basic_auth_user': None,
                'basic_auth_password': None,
                'auth_token': "my_super_secret_token",
                'max_timeout': 300,
                'terraform_binary_path': None,
                'terraform_modules_path': '/www/terraform_modules'
            }
            self.assertEqual(reply, expected_reply)

    def test_terrformize_configure_read_custom_config_folder(self):
        reply = read_configurations(config_folder="test/test_config")
        expected_reply = {
            'basic_auth_user': None,
            'basic_auth_password': None,
            'auth_token': "my_super_secret_token",
            'max_timeout': 450,
            'terraform_binary_path': None,
            'terraform_modules_path': '/www/terraform_modules'
        }
        self.assertEqual(reply, expected_reply)

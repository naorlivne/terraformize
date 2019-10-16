from unittest import TestCase, mock
from terraformize.terraformize_endpoint import *


class BaseTests(TestCase):

    def test_terraformize_endpoint_terraform_return_code_to_http_code_0_to_200(self):
        reply = terraform_return_code_to_http_code(0)
        self.assertEqual(reply, 200)

    def test_terraformize_endpoint_terraform_return_code_to_http_code_non_0_to_400(self):
        reply = terraform_return_code_to_http_code(1)
        self.assertEqual(reply, 400)

    def test_terraformize_endpoint_verify_password_auth_enabled_is_false(self):
        configuration["auth_enabled"] = False
        reply = verify_password("test_user", "test_pass")
        self.assertTrue(reply)

    def test_terraformize_endpoint_verify_password_user_pass_ok(self):
        configuration["auth_enabled"] = True
        configuration["basic_auth_user"] = "test_user"
        configuration["basic_auth_password"] = "test_pass"
        reply = verify_password("test_user", "test_pass")
        self.assertTrue(reply)

    def test_terraformize_endpoint_verify_password_user_wrong(self):
        configuration["auth_enabled"] = True
        configuration["basic_auth_user"] = "test_user"
        configuration["basic_auth_password"] = "test_pass"
        reply = verify_password("wrong_user", "test_pass")
        self.assertFalse(reply)

    def test_terraformize_endpoint_verify_password_pass_wrong(self):
        configuration["auth_enabled"] = True
        configuration["basic_auth_user"] = "test_user"
        configuration["basic_auth_password"] = "test_pass"
        reply = verify_password("test_user", "wrong_pass")
        self.assertFalse(reply)

    def test_terraformize_endpoint_verify_token_auth_enabled_is_false(self):
        configuration["auth_enabled"] = False
        reply = verify_token("test_token")
        self.assertTrue(reply)

    def test_terraformize_endpoint_verify_token_ok(self):
        configuration["auth_enabled"] = True
        configuration["auth_token"] = "test_token"
        reply = verify_token("test_token")
        self.assertTrue(reply)

    def test_terraformize_endpoint_verify_token_wrong(self):
        configuration["auth_enabled"] = True
        configuration["auth_token"] = "test_token"
        reply = verify_token("wrong_token")
        self.assertFalse(reply)

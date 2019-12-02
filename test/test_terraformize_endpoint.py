from unittest import TestCase
from terraformize.terraformize_endpoint import *
import os
from flask import request


# this will run all tests in relation to the location of this file so that the test_terraform folder will catch
# the correct path
test_files_location = os.getenv("TEST_FILES_LOCATION", os.path.realpath(__file__).rsplit("/", 1)[0]) + "/test_terraform"
test_bin_location = os.getenv("TEST_BIN_LOCATION", "/usr/bin/terraform")


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

    def test_terraformize_endpoint_apply_missing_module(self):
        configuration["terraform_modules_path"] = test_files_location
        configuration["terraform_binary_path"] = test_bin_location
        expected_body = {
            'error': "[Errno 2] No such file or directory: '" +
                     test_files_location + "/fake_test_module'"
        }
        with app.test_request_context('/v1/fake_test_module/test_workspace', method='POST'):
            self.assertEqual(request.path, '/v1/fake_test_module/test_workspace')
            return_body, terraform_return_code = apply_terraform("fake_test_module", "test_workspace")
            self.assertEqual(terraform_return_code, 404)
            self.assertEqual(return_body.json, expected_body)

    def test_terraformize_endpoint_destroy_missing_module(self):
        configuration["terraform_modules_path"] = test_files_location
        configuration["terraform_binary_path"] = test_bin_location
        expected_body = {
            'error': "[Errno 2] No such file or directory: '" +
                     test_files_location + "/fake_test_module'"
        }
        with app.test_request_context('/v1/fake_test_module/test_workspace', method='DELETE'):
            self.assertEqual(request.path, '/v1/fake_test_module/test_workspace')
            return_body, terraform_return_code = destroy_terraform("fake_test_module", "test_workspace")
            self.assertEqual(terraform_return_code, 404)
            self.assertEqual(return_body.json, expected_body)

    def test_terraformize_endpoint_apply_run(self):
        configuration["terraform_modules_path"] = test_files_location
        configuration["terraform_binary_path"] = test_bin_location
        with app.test_request_context('/v1/working_test/test_workspace', method='POST'):
            self.assertEqual(request.path, '/v1/working_test/test_workspace')
            return_body, terraform_return_code = apply_terraform("working_test", "test_workspace")
            self.assertEqual(terraform_return_code, 200)

    def test_terraformize_endpoint_destroy_run(self):
        configuration["terraform_modules_path"] = test_files_location
        configuration["terraform_binary_path"] = test_bin_location
        self.test_terraformize_endpoint_apply_run()
        with app.test_request_context('/v1/working_test/test_workspace', method='DELETE'):
            self.assertEqual(request.path, '/v1/working_test/test_workspace')
            return_body, terraform_return_code = destroy_terraform("working_test", "test_workspace")
            self.assertEqual(terraform_return_code, 200)

    def test_terraformize_endpoint_apply_raise_exception(self):
        configuration["terraform_modules_path"] = test_files_location
        configuration["terraform_binary_path"] = test_bin_location
        with app.test_request_context('/v1/non_runnable_test/test_workspace', method='POST'):
            self.assertEqual(request.path, '/v1/non_runnable_test/test_workspace')
            return_body, terraform_return_code = apply_terraform("non_runnable_test", "test_workspace")
            self.assertEqual(terraform_return_code, 400)

    def test_terraformize_endpoint_destroy_raise_exception(self):
        configuration["terraform_modules_path"] = test_files_location
        configuration["terraform_binary_path"] = test_bin_location
        with app.test_request_context('/v1/non_runnable_test/test_workspace', method='DELETE'):
            self.assertEqual(request.path, '/v1/non_runnable_test/test_workspace')
            return_body, terraform_return_code = destroy_terraform("non_runnable_test", "test_workspace")
            self.assertEqual(terraform_return_code, 400)

    def test_terraformize_endpoint_health_check_get(self):
        configuration["terraform_modules_path"] = test_files_location
        configuration["terraform_binary_path"] = test_bin_location
        with app.test_request_context('/v1/health', method='GET'):
            self.assertEqual(request.path, '/v1/health')
            return_body, terraform_return_code = health_check()
            self.assertEqual(terraform_return_code, 200)
            self.assertEqual(return_body.json, {"healthy": True})

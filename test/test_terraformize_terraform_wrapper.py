from unittest import TestCase
from terraformize.terraformize_terraform_wrapper import *
import os


# this will run all tests in relation to the location of this file so that the test_terraform folder will catch
# the correct path
test_files_location = os.getenv("TEST_FILES_LOCATION", str(os.path.realpath(__file__).rsplit("/", 1)[0]) +
                                "/test_terraform/working_test")
test_bin_location = os.getenv("TEST_BIN_LOCATION", "/usr/bin/terraform")


class BaseTests(TestCase):

    def test_terraformize_terraform_wrapper_init_create_and_use_new_workspace(self):
        terraform_object = Terraformize("test_workspace", "/tmp/", terraform_bin_path=test_bin_location)
        self.assertEqual(terraform_object.init_return_code, 0)
        self.assertEqual(terraform_object.workspace_return_code, 0)

    def test_terraformize_terraform_wrapper_init_use_preexisting_workspace(self):
        Terraformize("test_workspace", "/tmp/", terraform_bin_path=test_bin_location)
        terraform_object = Terraformize("test_workspace", "/tmp/", terraform_bin_path=test_bin_location)
        self.assertEqual(terraform_object.init_return_code, 0)
        self.assertEqual(terraform_object.workspace_return_code, 0)

    def test_terraformize_terraform_wrapper_apply_no_vars(self):
        terraform_object = Terraformize("test_workspace", test_files_location, terraform_bin_path=test_bin_location)
        return_code, stdout, stderr = terraform_object.apply()
        self.assertEqual(return_code, 0)
        self.assertIn("Apply complete!", stdout.replace('"', ''))
        self.assertIn("test = not_set", stdout.replace('"', ''))
        self.assertEqual(stderr.replace('"', ''), "")

    def test_terraformize_terraform_wrapper_parallelism(self):
        terraform_object = Terraformize("test_workspace", test_files_location, terraform_bin_path=test_bin_location)
        return_code, stdout, stderr = terraform_object.apply(None, 5)
        self.assertEqual(return_code, 0)
        self.assertIn("Apply complete!", stdout.replace('"', ''))
        self.assertIn("test = not_set", stdout.replace('"', ''))
        self.assertEqual(stderr.replace('"', ''), "")

    def test_terraformize_terraform_wrapper_apply_with_vars(self):
        terraform_object = Terraformize("test_workspace", test_files_location, terraform_bin_path=test_bin_location)
        return_code, stdout, stderr = terraform_object.apply({"test": "set"})
        self.assertEqual(return_code, 0)
        self.assertIn("Apply complete!", stdout.replace('"', ''))
        self.assertIn("test = set", stdout.replace('"', ''))
        self.assertEqual(stderr.replace('"', ''), "")

    def test_terraformize_terraform_wrapper_destroy_no_vars(self):
        terraform_object = Terraformize("test_workspace", test_files_location, terraform_bin_path=test_bin_location)
        return_code, stdout, stderr = terraform_object.destroy()
        self.assertEqual(return_code, 0)
        self.assertIn("Destroy complete!", stdout)
        self.assertEqual(stderr, "")

    def test_terraformize_terraform_wrapper_destroy_parallelism(self):
        terraform_object = Terraformize("test_workspace", test_files_location, terraform_bin_path=test_bin_location)
        return_code, stdout, stderr = terraform_object.destroy(None, 5)
        self.assertEqual(return_code, 0)
        self.assertIn("Destroy complete!", stdout)
        self.assertEqual(stderr, "")

    def test_terraformize_terraform_wrapper_destroy_with_vars(self):
        terraform_object = Terraformize("test_workspace", test_files_location, terraform_bin_path=test_bin_location)
        return_code, stdout, stderr = terraform_object.destroy({"test": "set"})
        self.assertEqual(return_code, 0)
        self.assertIn("Destroy complete!", stdout)
        self.assertEqual(stderr, "")

from python_terraform import *
from typing import Tuple, Optional
import tempfile
import shutil


class Terraformize:

    def __init__(self, remote_backend: bool, workspace: str, folder_path: str, \
                 terraform_bin_path: Optional[str] = None):
        """
        Will create a terraform object, create a workspace & init the terraform directory

        Arguments:
            :param remote_backend: if terraform is running with a remote state backend
            :param workspace: the workspace terraform will be executed in
            :param folder_path: the full path of the folder to run the terraform in
            :param terraform_bin_path: the full path of the terraform binary to use, defaults to using $PATH if unset
        """
        self.terraform_bin_path = terraform_bin_path

        if remote_backend is True:
            self.working_path = tempfile.mkdtemp(prefix="tfize-")
            self.tf = Terraform(working_dir=self.working_path, terraform_bin_path=self.terraform_bin_path)
            # using an envvar is the only way to prevent terraform from creating
            # a default.tfstate during init on a remote backend (which causes locking)
            os.environ["TF_WORKSPACE"] = workspace
            self.init_return_code, self.init_stdout, self.init_stderr = \
                self.tf.init(from_module=folder_path, dir_or_plan=self.working_path)
        else:
            self.tf = Terraform(working_dir=folder_path, terraform_bin_path=self.terraform_bin_path)
            self.init_return_code, self.init_stdout, self.init_stderr = self.tf.init(dir_or_plan=folder_path)
            # create workspace and if failed we assume it already exists
            self.tf.create_workspace(workspace=workspace)
            self.workspace_return_code, self.workspace_stdout, self.workspace_stderr = \
                self.tf.set_workspace(workspace=workspace)

    def apply(self, variables: Optional[dict] = None, parallelism: int = 10) -> Tuple[str, str, str]:
        """
        Will run a terraform apply on a workspace & will pass all variables to the terraform apply as terraform
        variables

        Arguments:
            :param variables: the variables to pass to the terraform apply command
            :param parallelism: the number of parallel resource operations

        Returns:
            :return return_code: the return code of the terraform apply
            :return stdout: the stdout stream of the terraform apply
            :return stderr: the stderr stream of the terraform apply
        """
        if variables is None:
            variables = {}

        return_code, stdout, stderr = self.tf.apply(no_color=IsFlagged, var=variables, skip_plan=True,
                                                    parallelism=parallelism)
        return return_code, stdout, stderr

    def destroy(self, variables: Optional[dict] = None, parallelism: int = 10) -> Tuple[str, str, str]:
        """
        Will run a terraform destroy on a workspace will pass all variables to the terraform destroy as terraform
        variables, not deleting the workspace as one might want to keep historical data or have multiple modules under
        the same workspace name

        Arguments:
            :param variables: the variables to pass to the terraform destroy command
            :param parallelism: the number of parallel resource operations

        Returns:
            :return return_code: the return code of the terraform destroy
            :return stdout: the stdout stream of the terraform destroy
            :return stderr: the stderr stream of the terraform destroy
        """
        if variables is None:
            variables = {}

        return_code, stdout, stderr = self.tf.destroy(no_color=IsFlagged, var=variables, auto_approve=True,
                                                      parallelism=parallelism)
        return return_code, stdout, stderr

    def cleanup(self, remote_backend: bool):
        """
        Will clean up the temporary directory created when using a remote state

        Arguments:
            :param remote_backend: if terraform is running with a remote state backend
        """
        if remote_backend is True:
            shutil.rmtree(self.working_path)

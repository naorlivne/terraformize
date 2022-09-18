from python_terraform import *
from typing import Tuple, Optional
import time


class Terraformize:

    def __init__(self, workspace: str, folder_path: str, terraform_bin_path: Optional[str] = None):
        """
        Will create a terraform object, create a workspace & init the terraform directory

        Arguments:
            :param workspace: the workspace terraform will be executed in
            :param folder_path: the full path of the folder to run the terraform in
            :param terraform_bin_path: the full path of the terraform binary to use, will try to use the one at the path
            if not set
        """
        self.terraform_bin_path = terraform_bin_path
        self.tf = Terraform(working_dir=folder_path, terraform_bin_path=self.terraform_bin_path)

        # we need to init for a remote backend before we can create a workspace
        # due to https://github.com/beelit94/python-terraform/issues/116 the line below is replaced with a temp
        # workaround and will be returned once everything is back to working order
        # self.init_return_code, self.init_stdout, self.init_stderr = self.tf.init(dir_or_plan=folder_path)
        self.init_return_code, self.init_stdout, self.init_stderr = self.tf.cmd("-chdir=" + folder_path +
                                                                                " init -reconfigure -backend=true")
        # self.init_return_code, self.init_stdout, self.init_stderr = self.tf.init(dir_or_plan=folder_path)

        # create the workspace if it does not exist, using while not if due to weird bug of it not always catching
        # again using workaround due to the 0.14 version of python-terraform not yet published to pypi and not wanting
        # to complicate endusers with package install nightmares, this should be set to the following once new ver is
        # in pypi: `while workspace not in self.tf.list_workspace():`
        # this should work as create_workspace can fail silently without breaking anything
        # also adding sleep for a second because it seems like running this commands too quickly sometimes let terraform
        # use it before the lock has been fully created and fail as a result
        if self.tf.show_workspace()[1].rstrip('\n') != workspace:
            self.tf.create_workspace(workspace=workspace)
            time.sleep(1)

        # set the workspace if it is not being used currently, using while not if due to weird bug of it not always
        # catching, commenting it out due to the workaround above, once the line above is configured to run if
        # `while workspace not in self.tf.list_workspace():` this line should be commented out to seperate the create
        # and set steps of the workspace part
        # while self.tf.show_workspace()[1].rstrip('\n') != workspace:
        # also adding sleep for a second because it seems like running this commands too quickly sometimes let terraform
        # use it before the lock has been fully created and fail as a result
            self.workspace_return_code, self.workspace_stdout, self.workspace_stderr = \
                self.tf.set_workspace(workspace=workspace)
            time.sleep(1)

    def apply(self, variables: Optional[dict] = None, parallelism: int = 10) -> Tuple[int, str, str]:
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

    def destroy(self, variables: Optional[dict] = None, parallelism: int = 10) -> Tuple[int, str, str]:
        """

        Arguments:
            :param variables: the variables to pass to the terraform destroy command
            :param parallelism: the number of parallel resource operations

        Will run a terraform destroy on a workspace will pass all variables to the terraform destroy as terraform
        variables, not deleting the workspace as one might want to keep historical data or have multiple modules under
        the same workspace name

        Arguments:

        Returns:
            :return return_code: the return code of the terraform destroy
            :return stdout: the stdout stream of the terraform destroy
            :return stderr: the stderr stream of the terraform destroy
        """
        # due to https://github.com/beelit94/python-terraform/issues/116 the line below is replaced with a temp
        # workaround and will be returned once everything is back to working order
        # return_code, stdout, stderr = self.tf.destroy(no_color=IsFlagged, var=variables, auto_approve=True,
        #                                              parallelism=parallelism)
        return_code, stdout, stderr = self.tf.apply(no_color=IsFlagged, var=variables, skip_plan=True,
                                                    parallelism=parallelism, destroy=True)
        return return_code, stdout, stderr

    def plan(self, variables: Optional[dict] = None, parallelism: int = 10) -> Tuple[int, str, str]:
        """
        Will run a terraform plan on a workspace & will pass all variables to the terraform plan as terraform
        variables

        Arguments:
            :param variables: the variables to pass to the terraform plan command
            :param parallelism: the number of parallel resource operations

        Returns:
            :return return_code: the return code of the terraform plan
            :return stdout: the stdout stream of the terraform plan
            :return stderr: the stderr stream of the terraform plan
        """
        if variables is None:
            variables = {}

        return_code, stdout, stderr = self.tf.plan(no_color=IsFlagged, var=variables, parallelism=parallelism)
        return return_code, stdout, stderr

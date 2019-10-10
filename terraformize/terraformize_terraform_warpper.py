from python_terraform import *
from typing import Tuple, Optional


class Terraformize:

    def __init__(self, workspace: str, folder_path: str):
        """
        Will create a terraform object, create a workspace & init the terraform directory

        Arguments:
            :param workspace: the workspace terraform will be executed in
            :param folder_path: the folder to run the terraform in
        """
        self.tf = Terraform(working_dir=folder_path)

        # always create the workspace and switch to it, if workspace already created carries on when it failed creating
        # it again
        self.tf.create_workspace(workspace=workspace)
        self.tf.set_workspace(workspace=workspace)

        # always init the directory
        self.tf.init(dir_or_plan=folder_path)

    def apply(self, variables: Optional[dict] = None) -> Tuple[str, str, str]:
        """
        Will run a terraform apply on a workspace & will pass all variables to the terraform apply as terraform
        variables

        Arguments:
            :param variables: the variables to pass to the terraform apply command

        Returns:
            :return return_code: the return code of the terraform apply
            :return stdout: the stdout stream of the terraform apply
            :return stderr: the stderr stream of the terraform apply
        """

        if variables is None:
            variables = {}

        return_code, stdout, stderr = self.tf.apply(no_color=IsFlagged, var=variables, auto_approve=True)
        return return_code, stdout, stderr

    def destory(self):
        """
        Will run a terraform destroy on a workspace will pass all variables to the terraform apply as terraform
        variables

        Arguments:

        Returns:
            :return return_code: the return code of the terraform destroy
            :return stdout: the stdout stream of the terraform destroy
            :return stderr: the stderr stream of the terraform destroy
        """
        return_code, stdout, stderr = self.tf.destroy(no_color=IsFlagged, auto_approve=True)
        return return_code, stdout, stderr

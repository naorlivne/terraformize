from python_terraform import *
from typing import Tuple, Optional

class terraform:

    def __init__(self):
        # just a template that still needs work
        self.tf = Terraform()

    def apply(self, workspace: str, folder_path: str, variables: Optional[dict] = None) -> Tuple[str, str, str]:
        """
        Will run a terraform apply on a workspace (creating said workspace if needed with the given folder_path & will
        pass all variables to the terraform apply as terraform variables

        :param workspace:
        :param folder_path:
        :param variables:
        :return:


        """

        if variables is None:
            variables = {}

        self._ensure_workspace_exist_and_used(workspace)
        return_code, stdout, stderr = self.tf.apply(folder_path, no_color=IsFlagged, var=variables, auto_approve=True,
                                                    skip_plan=True)

        return return_code, stdout, stderr

    def destory(self,  workspace, folder_path):
        self.tf.destroy()

    def _check_workspace_exist(self, workspace):
        pass

    def _create_workspace(self, workspace):
        pass

    def _delete_workspace(self, workspace):
        pass

    def _ensure_workspace_exist_and_used(self, workspace):
        pass

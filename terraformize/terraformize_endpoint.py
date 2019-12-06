from terraformize.terraformize_terraform_wrapper import *
from terraformize.terraformize_configure import *
from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth, MultiAuth
from typing import Optional, Tuple
import os


API_VERSION = "v1"


app = Flask(__name__)
basic_auth = HTTPBasicAuth(realm='terraformize')
token_auth = HTTPTokenAuth('Bearer')
multi_auth = MultiAuth(basic_auth, token_auth)
configuration = read_configurations(os.getenv("CONFIG_DIR", "config"))


def terraform_return_code_to_http_code(terraform_return_code: int) -> int:
    """
    Converts the exit code given by terraform to HTTP return code

    Arguments:
        :param terraform_return_code: the exit code given by terraform

    Returns:
        :return return_code: 200 if terraform exit code was 0, 400 otherwise
    """
    if terraform_return_code == 0:
        return_code = 200
    else:
        return_code = 400
    return return_code


@basic_auth.verify_password
def verify_password(username: Optional[str], password: Optional[str]) -> bool:
    """
    Authenticate the basic_auth user & password given by the end-user

    Arguments:
        :param username: the username to check
        :param password: the password to check

    Returns:
        :return: True if the user&pass is correct or auth is disabled, False otherwise
    """
    # if auth_enabled is set to false then always allow access
    if configuration["auth_enabled"] is False:
        return True
    # else if username and password matches the admin user set in the manager config allow access
    elif username == configuration["basic_auth_user"] and password == configuration["basic_auth_password"]:
        return True
    # in any other case return false
    else:
        return False


# this function checks token based auth to allow access to authenticated users.
@token_auth.verify_token
def verify_token(token: Optional[str]) -> bool:
    """
    Authenticate the bearer token given by the end-user

    Arguments:
        :param token: the token to check

    Returns:
        :return: True if the token is correct or auth is disabled, False otherwise
    """
    # if auth_enabled is set to false then always allow access
    if configuration["auth_enabled"] is False:
        return True
    # else if the token matches the admin user set in the manager config allow access
    elif configuration["auth_token"] == token:
        return True
    # in any other case return false
    else:
        return False


@app.route('/' + API_VERSION + '/<module_path>/<workspace_name>', methods=["POST"])
@multi_auth.login_required
def apply_terraform(module_path: str, workspace_name: str) -> Tuple[str, int]:
    """
    A REST endpoint to apply terraform modules at a given module path inside the main module directory path at a given
    workspace

    Arguments:
        :param module_path:  the name of the subdirectory for the module inside the "terraform_modules_path" to run
        "terraform apply" at
        :param workspace_name: the name of the workspace to run "terraform apply" at

    Returns:
        :return return_body: a JSON of the stdout & stderr from the terraform run
        :return terraform_return_code: the terraform return code

    Exceptions:
        :except FileNotFoundError: will return HTTP 404 with a JSON of the stderr it catch from "terraform init" or
        "terraform apply"
    """
    try:
        terraform_object = Terraformize(workspace_name, configuration["terraform_modules_path"] + "/" + module_path,
                                        terraform_bin_path=configuration["terraform_binary_path"])
        terraform_return_code, terraform_stdout, terraform_stderr = terraform_object.apply(
            request.json, configuration["parallelism"]
        )
        return_body = jsonify({
            "init_stdout": terraform_object.init_stdout,
            "init_stderr": terraform_object.init_stderr,
            "stdout": terraform_stdout,
            "stderr": terraform_stderr
        })
        terraform_return_code = terraform_return_code_to_http_code(int(terraform_return_code))
        return return_body, terraform_return_code
    except FileNotFoundError as error_log:
        return jsonify({"error": str(error_log)}), 404


@app.route('/' + API_VERSION + '/<module_path>/<workspace_name>', methods=["DELETE"])
@multi_auth.login_required
def destroy_terraform(module_path: str, workspace_name: str) -> Tuple[str, int]:
    """
    A REST endpoint to destroy terraform modules at a given module path inside the main module directory path at a given
    workspace

    Arguments:
        :param module_path:  the name of the subdirectory for the module inside the "terraform_modules_path" to run
        "terraform destroy" at
        :param workspace_name: the name of the workspace to run "terraform destroy" at

    Returns:
        :return return_body: a JSON of the stdout & stderr from the terraform run
        :return terraform_return_code: the terraform return code

    Exceptions:
        :except FileNotFoundError: will return HTTP 404 with a JSON of the stderr it catch from "terraform init" or
        "terraform destroy"
    """
    try:
        terraform_object = Terraformize(workspace_name, configuration["terraform_modules_path"] + "/" + module_path,
                                        terraform_bin_path=configuration["terraform_binary_path"])
        terraform_return_code, terraform_stdout, terraform_stderr = terraform_object.destroy(
            request.json, configuration["parallelism"]
        )
        return_body = jsonify({
            "init_stdout": terraform_object.init_stdout,
            "init_stderr": terraform_object.init_stderr,
            "stdout": terraform_stdout,
            "stderr": terraform_stderr
        })
        return return_body, terraform_return_code_to_http_code(int(terraform_return_code))
    except FileNotFoundError as error_log:
        return jsonify({"error": str(error_log)}), 404


@app.route('/' + API_VERSION + '/health', methods=["GET"])
def health_check() -> Tuple[str, int]:
    """
    A REST endpoint to make sure that terraformize is working

    Returns:
        :return return_body: a JSON of {"healthy": true}
        :return terraform_return_code: 200

    """
    return jsonify({"healthy": True}), 200

from terraformize.terraformize_terraform_wrapper import *
from terraformize.terraformize_configure import *
from terraformize.terraformize_webhook import *
from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth, MultiAuth
from typing import Optional, Tuple
import os
from threading import Thread


API_VERSION = "v1"


app = Flask(__name__)
basic_auth = HTTPBasicAuth(realm='terraformize')
token_auth = HTTPTokenAuth('Bearer')
multi_auth = MultiAuth(basic_auth, token_auth)
configuration = read_configurations(os.getenv("CONFIG_DIR", "config"))


# TODO - finish this! (unit tests)
def long_running_task(**kwargs):
    """
    Used in threading option to run the terraform apply/plan/destroy commands on in it's own thread and return the
    response to a webhook

    Arguments:
        :param command: plan/destory/apply - the terraform command to run
        :param variables: the body of the variables to pass to the terraform command
        :param module_path: the path to the module to run
        :param workspace_name: name of terraform workspace
        :param terraform_request_uuid: the uuid of the long running request
        :param webhook_url: url to return the results of the terraform run once it completes
    """
    command = kwargs.get('command', {})
    variables = kwargs.get('variables', {})
    module_path = kwargs.get('module_path', {})
    workspace_name = kwargs.get('workspace_name', {})
    terraform_request_uuid = kwargs.get('terraform_request_uuid', {})
    webhook_url = kwargs.get('webhook_url', {})
    terraform_object = Terraformize(workspace_name, configuration["terraform_modules_path"] + "/" + module_path,
                                    terraform_bin_path=configuration["terraform_binary_path"])
    if command == "plan":
        terraform_return_code, terraform_stdout, terraform_stderr = terraform_object.plan(
            variables, configuration["parallelism"]
        )
    elif command == "apply":
        terraform_return_code, terraform_stdout, terraform_stderr = terraform_object.apply(
            variables, configuration["parallelism"]
        )
    elif command == "destroy":
        terraform_return_code, terraform_stdout, terraform_stderr = terraform_object.destroy(
            variables, configuration["parallelism"]
        )
    send_webhook_result(webhook_url, terraform_object.init_stdout, terraform_object.init_stderr, terraform_stdout,
                        terraform_stderr, terraform_return_code, terraform_request_uuid)


def terraform_return_code_to_http_code(terraform_return_code: int, plan_mode=False) -> int:
    """
    Converts the exit code given by terraform to HTTP return code

    Arguments:
        :param terraform_return_code: the exit code given by terraform
        :param plan_mode: default to False, if True will assume the result is exit code from "terraform plan" which is
        a bit different the standard TF exit codes

    Returns:
        :return return_code: 200 if terraform exit code was 0 (or 2 in plan mode), 400 otherwise
    """
    if terraform_return_code == 0 or (plan_mode is True and terraform_return_code == 2):
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


# TODO - finish this! (thread plan unit tests & documentation)
@app.route('/' + API_VERSION + '/<module_path>/<workspace_name>/plan', methods=["POST"])
@multi_auth.login_required
def plan_terraform(module_path: str, workspace_name: str) -> Tuple[str, int]:
    """
    A REST endpoint to plan terraform modules at a given module path inside the main module directory path at a given
    workspace, if the "webhook" is set to a URL the function will work in a threaded format and return only the request
    UUID then will return the full request response once that completes in a non blocking format

    Arguments:
        :param module_path:  the name of the subdirectory for the module inside the "terraform_modules_path" to run
        "terraform plan" at
        :param workspace_name: the name of the workspace to run "terraform plan" at

    Returns:
        :return return_body: a JSON of the terraform exit code, stdout & stderr from the terraform run, if a arg of
        "webhook" is  passed will only return the UUID of the request
        :return terraform_return_code: the terraform return code

    Exceptions:
        :except FileNotFoundError: will return HTTP 404 with a JSON of the stderr it catch from "terraform init" or
        "terraform plan"
    """
    try:
        webhook = request.args.get('webhook', None)
        if webhook is None:
            terraform_object = Terraformize(workspace_name, configuration["terraform_modules_path"] + "/" + module_path,
                                            terraform_bin_path=configuration["terraform_binary_path"])
            terraform_return_code, terraform_stdout, terraform_stderr = terraform_object.plan(
                request.get_json(silent=True), configuration["parallelism"]
            )
            return_body = jsonify({
                "init_stdout": terraform_object.init_stdout,
                "init_stderr": terraform_object.init_stderr,
                "stdout": terraform_stdout,
                "stderr": terraform_stderr,
                "exit_code": terraform_return_code
            })
            terraform_return_code = terraform_return_code_to_http_code(int(terraform_return_code), plan_mode=True)
            return return_body, terraform_return_code
        else:
            terraform_request_uuid, terraform_request_uuid_json = create_request_uuid()
            thread = Thread(target=long_running_task, kwargs={'command': "plan",
                                                              'variables': request.get_json(silent=True),
                                                              'workspace_name': workspace_name,
                                                              'module_path': module_path,
                                                              'terraform_request_uuid': terraform_request_uuid,
                                                              'webhook_url': webhook})
            thread.start()
            return terraform_request_uuid_json, 202

    except FileNotFoundError as error_log:
        return jsonify({"error": str(error_log)}), 404


# TODO - finish this! (thread unit tests & documentation)
@app.route('/' + API_VERSION + '/<module_path>/<workspace_name>', methods=["POST"])
@multi_auth.login_required
def apply_terraform(module_path: str, workspace_name: str) -> Tuple[str, int]:
    """
    A REST endpoint to apply terraform modules at a given module path inside the main module directory path at a given
    workspace, if the "webhook" is set to a URL the function will work in a threaded format and return only the request
    UUID then will return the full request response once that completes in a non blocking format

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
        webhook = request.args.get('webhook', None)
        if webhook is None:
            terraform_object = Terraformize(workspace_name, configuration["terraform_modules_path"] + "/" + module_path,
                                            terraform_bin_path=configuration["terraform_binary_path"])
            terraform_return_code, terraform_stdout, terraform_stderr = terraform_object.apply(
                request.get_json(silent=True), configuration["parallelism"]
            )
            return_body = jsonify({
                "init_stdout": terraform_object.init_stdout,
                "init_stderr": terraform_object.init_stderr,
                "stdout": terraform_stdout,
                "stderr": terraform_stderr
            })
            terraform_return_code = terraform_return_code_to_http_code(int(terraform_return_code))
            return return_body, terraform_return_code
        else:
            terraform_request_uuid, terraform_request_uuid_json = create_request_uuid()
            thread = Thread(target=long_running_task, kwargs={'command': "apply",
                                                              'variables': request.get_json(silent=True),
                                                              'workspace_name': workspace_name,
                                                              'module_path': module_path,
                                                              'terraform_request_uuid': terraform_request_uuid,
                                                              'webhook_url': webhook})
            thread.start()
            return terraform_request_uuid_json, 202
    except FileNotFoundError as error_log:
        return jsonify({"error": str(error_log)}), 404


# TODO - finish this! (thread unit tests & documentation)
@app.route('/' + API_VERSION + '/<module_path>/<workspace_name>', methods=["DELETE"])
@multi_auth.login_required
def destroy_terraform(module_path: str, workspace_name: str) -> Tuple[str, int]:
    """
    A REST endpoint to destroy terraform modules at a given module path inside the main module directory path at a given
    workspace, if the "webhook" is set to a URL the function will work in a threaded format and return only the request
    UUID then will return the full request response once that completes in a non blocking format

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
        webhook = request.args.get('webhook', None)
        if webhook is None:
            terraform_object = Terraformize(workspace_name, configuration["terraform_modules_path"] + "/" + module_path,
                                            terraform_bin_path=configuration["terraform_binary_path"])
            terraform_return_code, terraform_stdout, terraform_stderr = terraform_object.destroy(
                request.get_json(silent=True), configuration["parallelism"]
            )
            return_body = jsonify({
                "init_stdout": terraform_object.init_stdout,
                "init_stderr": terraform_object.init_stderr,
                "stdout": terraform_stdout,
                "stderr": terraform_stderr
            })
            terraform_return_code = terraform_return_code_to_http_code(int(terraform_return_code))
            return return_body, terraform_return_code
        else:
            terraform_request_uuid, terraform_request_uuid_json = create_request_uuid()
            thread = Thread(target=long_running_task, kwargs={'command': "destroy",
                                                              'variables': request.get_json(silent=True),
                                                              'workspace_name': workspace_name,
                                                              'module_path': module_path,
                                                              'terraform_request_uuid': terraform_request_uuid,
                                                              'webhook_url': webhook})
            thread.start()
            return terraform_request_uuid_json, 202
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

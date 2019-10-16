from terraformize.terraformize_terraform_warpper import *
from terraformize.terraformize_configure import *
from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth, MultiAuth
import os


API_VERSION = "v1"


app = Flask(__name__)
basic_auth = HTTPBasicAuth(realm='terraformize')
token_auth = HTTPTokenAuth('Bearer')
multi_auth = MultiAuth(basic_auth, token_auth)
configuration = read_configurations(os.getenv("CONFIG_DIR", "config"))


def terraform_return_code_to_http_code(terraform_return_code):
    if terraform_return_code == 0:
        return 200
    else:
        return 400


# this function checks basic_auth to allow access to authenticated users.
@basic_auth.verify_password
def verify_password(username, password):
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
def verify_token(token):
    # if auth_enabled is set to false then always allow access
    if configuration["auth_enabled"] is False:
        return True
    # else if the token matches the admin user set in the manager config allow access
    elif configuration["auth_token"] == token:
        return True
    # in any other case return false
    else:
        return False


@multi_auth.login_required
@app.route('/' + API_VERSION + '/<module_path>/<workspace_name>', methods=["POST"])
def apply_terraform(module_path, workspace_name):
    terraform_object = Terraformize(workspace_name, configuration["terraform_modules_path"] + "/" + module_path,
                                    terraform_bin_path=configuration["terraform_binary_path"])
    terraform_return_code, terraform_stdout, terraform_stderr = terraform_object.apply(request.json)
    return_body = {
        "stdout": terraform_stdout,
        "stderr": terraform_stderr
    }
    return jsonify(return_body), terraform_return_code_to_http_code(terraform_return_code)


@multi_auth.login_required
@app.route('/' + API_VERSION + '/<module_path>/<workspace_name>', methods=["DELETE"])
def destroy_terraform(module_path, workspace_name):
    terraform_object = Terraformize(workspace_name, configuration["terraform_modules_path"] + "/" + module_path,
                                    terraform_bin_path=configuration["terraform_binary_path"])
    terraform_return_code, terraform_stdout, terraform_stderr = terraform_object.destroy()
    return_body = {
        "stdout": terraform_stdout,
        "stderr": terraform_stderr
    }
    return jsonify(return_body), terraform_return_code_to_http_code(terraform_return_code)


if __name__ == "__main__":
    try:
        app.run(host="127.0.0.1", port=5000, threaded=True)
    except Exception as e:
        print("Flask connection failure - dropping container")
        print(e, file=sys.stderr)
        exit(2)

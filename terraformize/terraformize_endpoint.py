from terraformize.terraformize_terraform_warpper import *
from flask import Flask
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth, MultiAuth


API_VERSION = "v1"


def init():
    pass


# open waiting connection
try:
    app = Flask(__name__)
    # basic auth for api
    basic_auth = HTTPBasicAuth(realm='terraformize')
    token_auth = HTTPTokenAuth('Bearer')
    multi_auth = MultiAuth(basic_auth, token_auth)
    print("startup completed - now waiting for connections")
except Exception as e:
    print("Flask connection configuration failure - dropping container")
    print(e, file=sys.stderr)
    os._exit(2)

# this function checks basic_auth to allow access to authenticated users.
@basic_auth.verify_password
def verify_password(username, password):
    # if auth_enabled is set to false then always allow access
    if username is None or password is None:
        return True
    # else if username and password matches the admin user set in the manager config allow access
    elif username == basic_auth_user and password == basic_auth_password:
        g.user = username
        g.user_type = "local"
        return True
    # else if the user and password matches any in the DB allow access
    elif mongo_connection.mongo_check_user_exists(username) is True:
        user_exists, user_json = mongo_connection.mongo_get_user(username)
        if check_secret_matches(password, user_json["password"]) is True:
            g.user = username
            g.user_type = "db"
            return True
        else:
            return False
    # on any other case deny access:
    else:
        return False


# this function checks token based auth to allow access to authenticated users.
@token_auth.verify_token
def verify_token(token):
    # if auth_enabled is set to false then always allow access
    if auth_enabled is False:
        return True
    # else if the token matches the admin user set in the manager config allow access
    elif auth_token == token:
        g.user_type = "local"
        return True
    # else if the token matches any in the DB allow access or deny access if not
    else:
        allow_access = False
        user_list = mongo_connection.mongo_list_users()
        for user in user_list:
            user_exists, user_json = mongo_connection.mongo_get_user(user)
            if check_secret_matches(token, user_json["token"]) is True:
                g.user = user
                g.user_type = "db"
                allow_access = True
        return allow_access

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

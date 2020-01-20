from parse_it import ParseIt
from typing import Optional


def read_configurations(config_folder: str = "config") -> dict:
    """
    Will create a config dict that includes all of the configurations for terraformize by aggregating from all valid
    config sources (files, envvars, cli args, etc) & using sane defaults on config params that are not declared

    Arguments:
        :param config_folder: the folder which all configuration file will be read from recursively

    Returns:
        :return config: a dict of all configurations needed for terraformize to work
    """
    print("reading config variables")

    config = {}
    parser = ParseIt(config_location=config_folder, recurse=True)

    config["basic_auth_user"] = parser.read_configuration_variable("basic_auth_user", default_value=None)
    config["basic_auth_password"] = parser.read_configuration_variable("basic_auth_password", default_value=None)
    config["auth_token"] = parser.read_configuration_variable("auth_token",  default_value=None)
    config["terraform_binary_path"] = parser.read_configuration_variable("terraform_binary_path", default_value=None)
    config["terraform_modules_path"] = parser.read_configuration_variable("terraform_modules_path",
                                                                          default_value="/www/terraform_modules")
    config["auth_enabled"] = auth_enabled(config["basic_auth_user"], config["basic_auth_password"],
                                          config["auth_token"])
    config["parallelism"] = parser.read_configuration_variable("parallelism", default_value=10)
    return config


def auth_enabled(username: Optional[str], password: Optional[str], token: Optional[str]) -> bool:
    """
    Checks if auth is enabled by making sure if there is a username & password pair or a token configured

    Arguments:
        :param username: the possible username for authentication
        :param password: the possible password for authentication
        :param token: the possible token for authentication

    Returns:
        :return auth_required: True if auth is enabled, False otherwise
    """
    if token is None and (username is None or password is None):
        return False
    else:
        return True

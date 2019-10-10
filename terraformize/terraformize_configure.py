from parse_it import ParseIt

# read config file at startup
print("reading config variables")
parser = ParseIt(config_location="config", recurse=True)

print("reading config variables")
basic_auth_user = parser.read_configuration_variable("basic_auth_user",  default_value=None)
basic_auth_password = parser.read_configuration_variable("basic_auth_password",  default_value=None)
auth_token = parser.read_configuration_variable("auth_token",  default_value=None)
max_timeout = parser.read_configuration_variable("max_timeout",  default_value=600)
terraform_binary_path = parser.read_configuration_variable("terraform_binary_path",  default_value=None)
terraform_modules_path = parser.read_configuration_variable("terraform_modules_path",
                                                            default_value="/www/terraform_modules")

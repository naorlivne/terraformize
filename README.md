# Terraformize

Apply\Destory Terraform modules via a simple REST API endpoint.

Drone.io CI/CD unit tests & auto push status: [![Build Status](https://cloud.drone.io/api/badges/naorlivne/terraformize/status.svg)](https://cloud.drone.io/naorlivne/terraformize)

Code coverage: [![codecov](https://codecov.io/gh/naorlivne/terraformize/branch/master/graph/badge.svg)](https://codecov.io/gh/naorlivne/terraformize)

# Features

* REST API to run:
    * `terraform apply`
    * `terraform destroy`
* No code changes needed, supports 100% of all terraform modules unmodified
* Built in support for multiple terraform workspaces
* Can pass variables to the terraform run via the request body (passed as a -var arg to the `terraform apply` or `terraform destroy` command)
* Supports multiple module directories
* Automatically runs terraform init before changes
* Returned response includes all the logs of stdout & stderr of terraform for easy debugging
* Stateless (requires you use a non local terraform backend)
* Containerized
* Health check endpoint included
* support all terraform backends that support multiple workspaces
* No DB needed, all data stored at the terraform backend of your choosing
* terraformize scales out as much as you need risk free (requires you use a backend that support state locking)
* AMD64, Arm & Arm64 support

# Possible use cases

* Setting up SaaS clusters\products\etc for clients in a fully automatic way
    * Each customer gets his own workspace and you just run the needed modules to create that customer products
    * Devs don't have to know how the terraform module works, they just point to a rest API & know it creates everything they need
* CI/CD integration
    * You can consider it as a terraform worker that is very easy to turn on via your CI/CD tool as it's just a REST request away
* Automatic system creation and\or scaling
    * Easy to intergrate to autoscalers as it can run the same module with diffrent variables passed to the `terraform apply` command via the request body to scale services up\down as needed
    * Easy to give your company employees a self-service endpoint and have them create and\or remove infrastracutre themselves when it's just an API request away
* Seperate who writes the terraform modules to who use them easily

# Running

Running Terraformize is as simple as running a docker container

```docker
docker run -d -p 80:80 -v /path/to/my/terraform/module/dir:/www/terraform_modules/ naorlivne/terraformize
```

Feel free to skip to the end of the document for a working example that will explain how to use Terraformize

# Configuration options

Terraformize uses sane defaults but they can all be easily changed:

| value                  | envvar                 | default value          | notes                                                                                                  |
|------------------------|------------------------|------------------------|--------------------------------------------------------------------------------------------------------|
| basic_auth_user        | BASIC_AUTH_USER        | None                   | Basic auth username to use                                                                             |
| basic_auth_password    | BASIC_AUTH_PASSWORD    | None                   | Basic auth password to use                                                                             |
| auth_token             | AUTH_TOKEN             | None                   | bearer token to use                                                                                    |
| terraform_binary_path  | TERRAFORM_BINARY_PATH  | None                   | The path to the terraform binary, if None will use the default OS PATH to find it                      |
| terraform_modules_path | TERRAFORM_MODULES_PATH | /www/terraform_modules | The path to the parent directory where all terraform module directories will be stored at as subdirs   |
| parallelism            | PARALLELISM            | 10                     | The number of parallel resource operations                                                             |
|                        | CONFIG_DIR             | /www/config            | The path to the directory where configuration files are stored at                                      |
|                        | HOST                   | 0.0.0.0                | The IP for gunicorn to bind to                                                                         |
|                        | PORT                   | 80                     | The port for gunicorn to bind to                                                                       |
|                        | WORKER_CLASS           | sync                   | The gunicorn class to use                                                                              |
|                        | WORKERS                | 1                      | Number of gunicorn workers                                                                             |
|                        | THREADS                | 1                      | Number of gunicorn threads                                                                             |
|                        | PRELOAD                | False                  | If gunicorn should preload the code                                                                    |
|                        | LOG_LEVEL              | error                  | The log level for gunicorn                                                                             |
|                        | TIMEOUT                | 600                    | The timeout for gunicorn, if your terraform run takes longer you will need to increase it              |


The easiest way to change a default value is to pass the envvar key\value to the docker container with the `-e` cli arg but if you want you can also create a configuration file with the settings you wish (in whatever of the standard format you desire) & place it in the /www/config folder inside the container.

Most providers also allow setting their configuration access_keys\etc via envvars use `-e` cli args to configure them is ideal as well but should you wish to configure a file you can also easily mount\copy it into the container as well.

## Authentication 

Terraformize supports 3 authentication methods:

* Basic auth - will require you to pass a `Authorization Basic your_user_pass_base64_combo` header with your_user_pass_base64_combo being the same as `basic_auth_user` & `basic_auth_password` configured in Terraformize 
* Bearer auth - will require you to pass a `Authorization Bearer your_token` header with your_token being the same as the `auth_token` configured in Terraformize
* No auth - will be used if both the Basic auth & Bearer auth are disabled, note that the /v1/health health-check point never requires authentication

# Endpoints

* POST /v1/module_folder_name/workspace_name
    * runs `terraform apply` for you
    * takes care of auto approval of the run, auto init & workspace switching as needed
    * takes variables which are passed to `terraform apply` as a JSON in the body of the message in the format of `{"var_key1": "var_value1", "var_key2": "var_value2"}`
    * Returns 200 HTTP status code if everything is ok, 404 if you gave it a non existing module_folder_name path & 400 if the `terraform apply` ran but failed to make all needed modifications
    * Also returns a JSON body of `{"init_stdout": "...", "init_stderr": "...", "stderr": "...", "stdout": "..."}` with the stderr & stdout of the `terraform apply` & `terraform init` run
* DELETE /v1/module_folder_name/workspace_name
    * runs `terraform destroy` for you
    * takes care of auto approval of the run, auto init & workspace switching as needed
    * takes variables which are passed to `terraform destroy` as a JSON in the body of the message in the format of `{"var_key1": "var_value1", "var_key2": "var_value2"}`
    * Returns 200 HTTP status code if everything is ok, 404 if you gave it a non existing module_folder_name path & 400 if the `terraform destroy` ran but failed to make all needed modifications
    * Also returns a JSON body of `{"init_stdout": "...", "init_stderr": "...", "stderr": "...", "stdout": "..."}` with the stderr & stdout of the `terraform destroy` & `terraform init` run
    * In order to preserve the history of terraform runs in your backend the workspace is not deleted automatically, only the infrastructure is destroyed
* GET /v1/health
    * Returns 200 HTTP status code
    * Also returns a JSON body of {"healthy": true}
    * Never needs auth
    * Useful to monitoring the health of Terraformize service

# Example

1. First we will need a terraform module so create a folder named terraformize_test:
    ```shell script
    mkdir terraformize_test
    ```
   Make sure **not** to `cd` into the folder as we will be mounting it into the container from the parent folder in a couple of steps
2. Now we need a valid terraform configuration in it, if it works in terraform it will work with terraformize but for this example we will keep it simple with a single `terraformize_test/test.tf` file:
    ```hcl-terraform
    resource "null_resource" "test" {
      count   = 1
    }
    
    variable "test_var" {
      description = "an example variable"
      default = "my_variable_default_value"
    }
    
    output "test" {
      value = var.test_var
    }
    ```
3. We will also need to add the folder we created into the Terraformize container, this can be done by many different way (for example creating a container that copies our modules into a new image with the FROM base image being Terraformize base image) but for this example we will simply mount the folder path into the container as we run it:
    ```docker
    docker run -d -p 80:80 -v `pwd`:/www/terraform_modules naorlivne/terraformize
    ```
4. Now we can run the terraform module by simply calling it which will run `terraform apply` for us (notice how we are passing variables in the body):
    ```shell script
    curl -X POST \
      http://127.0.0.1/v1/terraformize_test/my_workspace \
      -H 'Content-Type: application/json' \
      -H 'cache-control: no-cache' \
      -d '{
        "test_var": "hello-world"
    }'
    ```
5. And lets create another copy infra of the same module in another workspace:
    ```shell script
    curl -X POST \
      http://127.0.0.1/v1/terraformize_test/my_other_workspace \
      -H 'Content-Type: application/json' \
      -H 'cache-control: no-cache' \
      -d '{
        "test_var": "hello-world"
    }'
    ```
6. Now that we are done let's delete them both (this will run `terrafrom destroy` for us):
    ```shell script
   curl -X DELETE \
      http://127.0.0.1/v1/terraformize_test/my_workspace \
      -H 'Content-Type: application/json' \
      -H 'cache-control: no-cache' \
      -d '{
        "test_var": "hello-world"
    }' 
   curl -X DELETE \
      http://127.0.0.1/v1/terraformize_test/my_other_workspace \
      -H 'Content-Type: application/json' \
      -H 'cache-control: no-cache' \
      -d '{
        "test_var": "hello-world"
    }'
    ```

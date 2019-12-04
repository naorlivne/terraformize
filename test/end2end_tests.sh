#!/bin/sh
######################################################################################################################
#
# end2end tests that are designed to run on the completed container and simulate real world usage of the terraformize
# service in order to provide safty againt issues that are somehow missed in unit tests (for example issues with
# container versions).
#
######################################################################################################################

# exit on any failure with a non zero exit code of the line below in order to fail the e2e test
set -e

# as tests runs inside the container but the service is not started let's start it
# not worried about it dieing as the entire test will only take seconds
gunicorn --config /etc/gunicorn/config.py terraformize_runner:app &

# we will also need curl, using the -f flag on all of them to return a bash error on any non 2xx response code
apk add --no-cache curl

# checking health endpoint
curl -f -X GET http://127.0.0.1/v1/health


# checking a terraform apply
curl -f -X POST \
  http://127.0.0.1/v1/working_test/my_workspace \
  -H 'Content-Type: application/json' \
  -H 'cache-control: no-cache' \
  -d '{
    "test_var": "hello-world"
}'

# checking a terraform apply on a 2nd workspace
curl -f -X POST \
  http://127.0.0.1/v1/working_test/my_other_workspace \
  -H 'Content-Type: application/json' \
  -H 'cache-control: no-cache' \
  -d '{
    "test_var": "hello-world"
}'

# checking terraform destroy
curl -f -X DELETE \
  http://127.0.0.1/v1/working_test/my_workspace \
  -H 'Content-Type: application/json' \
  -H 'cache-control: no-cache' \
  -d '{
    "test_var": "hello-world"
}'

# checking terraform destroy on a 2nd workspace
curl -f -X DELETE \
  http://127.0.0.1/v1/terraformize_test/my_other_workspace \
  -H 'Content-Type: application/json' \
  -H 'cache-control: no-cache' \
  -d '{
    "test_var": "hello-world"
}'

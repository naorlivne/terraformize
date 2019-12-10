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

# wait until the endpoint becomes active
until $(curl --output /dev/null --silent --head --fail -H 'cache-control: no-cache' http://run_end2end_tests_terraformize_service/v1/health); do
    echo "Waiting on Terraformize API to become available..."
    sleep 1
done

# checking health endpoint
curl -f -X GET http://run_end2end_tests_terraformize_service/v1/health


# checking a terraform apply
curl -f -X POST \
  http://run_end2end_tests_terraformize_service/v1/working_test_remote_backend/my_workspace \
  -H 'Content-Type: application/json' \
  -H 'cache-control: no-cache' \
  -d '{
    "test": "hello-world"
}'

# checking a terraform apply on a 2nd workspace
curl -f -X POST \
  http://run_end2end_tests_terraformize_service/v1/working_test_remote_backend/my_other_workspace \
  -H 'Content-Type: application/json' \
  -H 'cache-control: no-cache' \
  -d '{
    "test": "hello-world"
}'

# checking terraform destroy
curl -f -X DELETE \
  http://run_end2end_tests_terraformize_service/v1/working_test_remote_backend/my_workspace \
  -H 'Content-Type: application/json' \
  -H 'cache-control: no-cache' \
  -d '{
    "test": "hello-world"
}'

# checking terraform destroy on a 2nd workspace
curl -f -X DELETE \
  http://run_end2end_tests_terraformize_service/v1/working_test_remote_backend/my_other_workspace \
  -H 'Content-Type: application/json' \
  -H 'cache-control: no-cache' \
  -d '{
    "test": "hello-world"
}'

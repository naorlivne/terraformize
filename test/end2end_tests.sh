#!/bin/sh
######################################################################################################################
#
# end2end tests that are designed to run on the completed container and simulate real world usage of the terraformize
# service in order to provide safety against issues that are somehow missed in unit tests (for example issues with
# container versions).
#
######################################################################################################################

# exit on any failure with a non zero exit code of the line below in order to fail the e2e test
set -e

# wait until the endpoint becomes active
until $(curl --output /dev/null --silent --head --fail-with-body -H 'cache-control: no-cache' http://run_end2end_tests_terraformize_service/v1/health); do
    echo "Waiting on Terraformize API to become available..."
    sleep 1
done

# checking health endpoint
curl --fail-with-body -X GET http://run_end2end_tests_terraformize_service/v1/health

# checking a terraform plan
curl --fail-with-body -X POST \
  http://run_end2end_tests_terraformize_service/v1/working_test_remote_backend/my_workspace/plan \
  -H 'Content-Type: application/json' \
  -H 'cache-control: no-cache' \
  -d '{
    "test": "hello-world"
}'

# checking a terraform apply
curl --fail-with-body -X POST \
  http://run_end2end_tests_terraformize_service/v1/working_test_remote_backend/my_workspace \
  -H 'Content-Type: application/json' \
  -H 'cache-control: no-cache' \
  -d '{
    "test": "hello-world"
}'

# checking a terraform apply on a 2nd workspace
curl --fail-with-body -X POST \
  http://run_end2end_tests_terraformize_service/v1/working_test_remote_backend/my_other_workspace \
  -H 'Content-Type: application/json' \
  -H 'cache-control: no-cache' \
  -d '{
    "test": "hello-world"
}'

# checking a terraform plan on a 2nd workspace after apply
curl --fail-with-body -X POST \
  http://run_end2end_tests_terraformize_service/v1/working_test_remote_backend/my_other_workspace/plan \
  -H 'Content-Type: application/json' \
  -H 'cache-control: no-cache' \
  -d '{
    "test": "hello-world"
}'

# checking terraform destroy
curl --fail-with-body -X DELETE \
  http://run_end2end_tests_terraformize_service/v1/working_test_remote_backend/my_workspace \
  -H 'Content-Type: application/json' \
  -H 'cache-control: no-cache' \
  -d '{
    "test": "hello-world"
}'

# checking terraform destroy on a 2nd workspace
curl --fail-with-body -X DELETE \
  http://run_end2end_tests_terraformize_service/v1/working_test_remote_backend/my_other_workspace \
  -H 'Content-Type: application/json' \
  -H 'cache-control: no-cache' \
  -d '{
    "test": "hello-world"
}'

# checking non blocking webhook response
curl --fail-with-body -X POST \
  http://run_end2end_tests_terraformize_service/v1/working_test_remote_backend/my_other_workspace/plan?webhook=http://httpbin.org/anything \
  -H 'Content-Type: application/json' \
  -H 'cache-control: no-cache' \
  -d '{
    "test": "hello-world"
}'

# checking with rabbitmq
# TODO - need to change to work with curl rather then rabbitmqadmin due to python3 requirement which I don't want installed in the e2e bash container
curl --fail-with-body -u guest:guest -i -H "content-type:application/json" -X POST \
http://localhost:15672/api/exchanges/%2Fvhost/exchange/publish -d'{"properties":{},"routing_key":"e2e_test_queue","payload": "{\"module_folder\": \"working_test_remote_backend\",\"workspace\": \"my_rabbitmq_e2e_workspace\",\"uuid\": \"1234567890\",\"run_type\": \"plan\",\"run_variables\": {\"test\": \"hello-world\"}}","payload_encoding":"string"}'

import uuid
from typing import Tuple
import json
import requests
from retrying import retry


def create_request_uuid() -> Tuple[str, str]:
    """
    Will create a json of {"request_uuid": random_uuid} and return that and the random_uuid

    Returns:
        :return request_uuid: the request uuid
        :return request_uuid_json: A json of the request uuid
    """
    request_uuid = str(uuid.uuid4())
    request_uuid_json = json.dumps({
        'request_uuid': request_uuid
    })
    return request_uuid, request_uuid_json


@retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=100)
def send_webhook_result(webhook_url: str, init_stdout: str, init_stderr: str, terraform_stdout: str,
                        terraform_stderr: str, return_code: int, request_uuid: str):
    """
    Sends the results of terraform operations to a specified webhook URL

        Arguments:
        :param webhook_url: the URL the webhook will be sent to
        :param init_stdout: init stdout of the terraformize command to forward to the webhook URL
        :param init_stderr: init stderr of the terraformize command to forward to the webhook URL
        :param terraform_stdout: terraform stdout of the terraformize command to forward to the webhook URL
        :param terraform_stderr: terraform stderr of the terraformize command to forward to the webhook URL
        :param return_code: The return code of the terraform operation
        :param request_uuid: the terraform operation random UUID assigned to this operation
    """
    headers = {
        'Content-Type': 'application/json'
    }
    payload = json.dumps({
        "init_stdout": init_stdout,
        "init_stderr": init_stderr,
        "stdout": terraform_stdout,
        "stderr": terraform_stderr,
        "terraform_return_code": return_code,
        "request_uuid": request_uuid
    })
    requests.request("POST", webhook_url, headers=headers, data=payload)

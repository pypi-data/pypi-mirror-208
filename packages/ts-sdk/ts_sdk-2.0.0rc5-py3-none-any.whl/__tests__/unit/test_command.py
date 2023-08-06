import os
from unittest.mock import MagicMock, patch

import pytest

from ts_sdk.task.__util_adapters.communication_format import (
    COMMUNICATION_FORMAT_ENV_KEY,
    CommunicationFormat,
)
from ts_sdk.task.__util_command import run_command


org_slug = "org_slug"

input_file = {
    "type": "s3",
    "bucket": "bucket",
    "fileKey": "some/fileKey",
    "fileId": "11111111-eeee-4444-bbbb-222222222222",
    "orgSlug": org_slug,
}
command_args = [
    {
        "inputFile": input_file,
        "pipelineConfig": {"ts_secret_name_password": "some/kms/path"},
    },
    org_slug,
    "target_id",
    "action",
    {"meta1": "v1"},
    "payload",
    300,
]


def test_format_unsupported():
    os.environ.update({COMMUNICATION_FORMAT_ENV_KEY: "unknown"})

    with pytest.raises(NotImplementedError):
        run_command(*command_args)


@patch("requests.get")
@patch("requests.post")
def test_run_command_v0(post_mock, get_mock):
    command_endpoint = "http://command.local"
    os.environ.update(
        {
            "COMMAND_ENDPOINT": command_endpoint,
            COMMUNICATION_FORMAT_ENV_KEY: CommunicationFormat.V0.value,
        }
    )

    response_mock = MagicMock()
    response_mock.status_code = 200
    response_mock.text = '{"id": "id"}'
    post_mock.return_value = response_mock

    get_response_mock = MagicMock()
    get_response_mock.status_code = 200
    get_response_mock.text = '{"status": "SUCCESS", "responseBody": "foo"}'
    get_mock.return_value = get_response_mock

    run_command(*command_args)

    args, kwargs = post_mock.call_args
    url: str = args[0]
    assert url == (command_endpoint + "/internal")


@patch("requests.get")
@patch("requests.post")
def test_run_command_v1(post_mock, get_mock):
    kernel_endpoint = "https://localhost:443"
    os.environ.update(
        {
            "KERNEL_ENDPOINT": kernel_endpoint,
            COMMUNICATION_FORMAT_ENV_KEY: CommunicationFormat.V1.value,
        }
    )

    response_mock = MagicMock()
    response_mock.status_code = 200
    response_mock.text = '{"id": "id"}'
    post_mock.return_value = response_mock

    get_response_mock = MagicMock()
    get_response_mock.status_code = 200
    get_response_mock.text = '{"status": "SUCCESS", "responseBody": "foo"}'
    get_mock.return_value = get_response_mock

    run_command(*command_args)

    args, kwargs = post_mock.call_args
    url: str = args[0]
    assert url == (kernel_endpoint + "/api/v1/commands")

import os
from unittest.mock import MagicMock

import pytest

from ts_sdk.task.__util_adapters.communication_format import (
    COMMUNICATION_FORMAT_ENV_KEY,
    CommunicationFormat,
)
from ts_sdk.task.__util_task import (
    extend_task_timeout,
    update_task_status,
    poll_task,
)

dummy_task = {
    "id": "taskId",
    "context": {},
    "input": {},
    "secrets": {},
    "func": "func",
    "workflow_id": "workflowId",
    "correlation_id": "taskId",
    "func_dir": "./func",
}
dummy_result = {
    "status": "failed",
    "result": {
        "error": {
            "message": {
                "text": "Invalid exit code 0",
                "oomError": True,
            }
        }
    },
}


def test_version_unsupported():
    os.environ.update({COMMUNICATION_FORMAT_ENV_KEY: "unknown"})

    with pytest.raises(NotImplementedError):
        poll_task()

    with pytest.raises(NotImplementedError):
        update_task_status(dummy_task, dummy_result)

    with pytest.raises(NotImplementedError):
        extend_task_timeout(dummy_task)


def test_version_poll_task_v0(mocker):
    orchestrator_endpoint = "http://orchestrator.local"
    os.environ.update(
        {
            "ORCHESTRATOR_ENDPOINT": orchestrator_endpoint,
            COMMUNICATION_FORMAT_ENV_KEY: CommunicationFormat.V0.value,
        }
    )

    post_mock = mocker.patch("requests.post")
    response_mock = MagicMock()
    response_mock.status_code = 200
    post_mock.json = lambda: False
    post_mock.return_value = response_mock

    poll_task()

    args, kwargs = post_mock.call_args
    url: str = args[0]
    assert url == (orchestrator_endpoint + "/task/poll")


def test_update_task_status_v0(mocker):
    orchestrator_endpoint = "http://orchestrator.local"
    os.environ.update(
        {
            "ORCHESTRATOR_ENDPOINT": orchestrator_endpoint,
            COMMUNICATION_FORMAT_ENV_KEY: CommunicationFormat.V0.value,
        }
    )

    post_mock = mocker.patch("requests.post")
    response_mock = MagicMock()
    response_mock.status_code = 200
    post_mock.json = lambda: False
    post_mock.return_value = response_mock

    update_task_status(dummy_task, dummy_result)

    args, kwargs = post_mock.call_args
    url: str = args[0]
    assert url == (orchestrator_endpoint + "/task/taskId/update-status")


def test_extend_task_timeout_v0(mocker):
    orchestrator_endpoint = "http://orchestrator.local"
    os.environ.update(
        {
            "ORCHESTRATOR_ENDPOINT": orchestrator_endpoint,
            COMMUNICATION_FORMAT_ENV_KEY: CommunicationFormat.V0.value,
        }
    )

    post_mock = mocker.patch("requests.post")
    response_mock = MagicMock()
    response_mock.status_code = 200
    post_mock.json = lambda: False
    post_mock.return_value = response_mock

    extend_task_timeout(dummy_task)

    args, kwargs = post_mock.call_args
    url: str = args[0]
    assert url == (orchestrator_endpoint + "/task/taskId/extend-timeout")


def test_version_poll_task_v1(mocker):
    kernel_endpoint = "https://localhost:443"
    os.environ.update(
        {
            "KERNEL_ENDPOINT": kernel_endpoint,
            COMMUNICATION_FORMAT_ENV_KEY: CommunicationFormat.V1.value,
        }
    )

    post_mock = mocker.patch("requests.post")
    response_mock = MagicMock()
    response_mock.status_code = 200
    post_mock.json = lambda: False
    post_mock.return_value = response_mock

    poll_task()

    args, kwargs = post_mock.call_args
    url: str = args[0]
    assert url == (kernel_endpoint + "/task/poll")

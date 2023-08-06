import os
from unittest.mock import MagicMock, patch

import pytest

from ts_sdk.task.__util_adapters.communication_format import (
    COMMUNICATION_FORMAT_ENV_KEY,
    CommunicationFormat,
)
from ts_sdk.task.__util_es_datalake import (
    es_datalake_search_eql,
    es_hit_to_file_pointer,
)

dummy_payload = ({"size": 1, "query": {"term": {"fileId": {"value": "fileId"}}}},)


def test_format_unsupported():
    os.environ.update({COMMUNICATION_FORMAT_ENV_KEY: "unknown"})

    with pytest.raises(NotImplementedError):
        es_datalake_search_eql(dummy_payload)


@patch("requests.post")
def test_es_datalake_search_eql_v0(post_mock):
    orchestrator_endpoint = "http://orchestrator.local"
    os.environ.update(
        {
            "ORCHESTRATOR_ENDPOINT": orchestrator_endpoint,
            COMMUNICATION_FORMAT_ENV_KEY: CommunicationFormat.V0.value,
        }
    )

    response_mock = MagicMock()
    response_mock.status_code = 200
    post_mock.json = lambda: False
    post_mock.return_value = response_mock

    es_datalake_search_eql(dummy_payload)

    args, kwargs = post_mock.call_args
    url: str = args[0]
    assert url == (orchestrator_endpoint + "/datalake/searchEql")


@patch("requests.post")
def test_es_datalake_search_eql_v1(post_mock):
    kernel_endpoint = "https://localhost:443"
    os.environ.update(
        {
            "KERNEL_ENDPOINT": kernel_endpoint,
            COMMUNICATION_FORMAT_ENV_KEY: CommunicationFormat.V1.value,
        }
    )

    response_mock = MagicMock()
    response_mock.status_code = 200
    post_mock.json = lambda: False
    post_mock.return_value = response_mock

    es_datalake_search_eql(dummy_payload)

    args, kwargs = post_mock.call_args
    url: str = args[0]
    assert url == (kernel_endpoint + "/api/v1/datalake/searchEql")


def test_es_hit_to_file_pointer():
    es_file = {"bucket": "b", "path": "p", "version": "v"}
    hit = {"_source": {"file": es_file, "fileId": "f"}}
    file_pointer = es_hit_to_file_pointer(hit)
    assert file_pointer == {
        "type": "s3file",
        "bucket": "b",
        "fileKey": "p",
        "version": "v",
        "fileId": "f",
    }

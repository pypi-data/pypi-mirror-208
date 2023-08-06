import argparse
import io
import os

import json
import pytest

from ts_sdk.cli.__put_cmd import __ensure_args, __namespace_type


@pytest.mark.parametrize(
    "args,cfg,envs,expected",
    [
        (
            {"org": "arg-org", "api_url": "arg-api-url", "ignore_ssl": False},
            {
                "org": "cfg-org",
                "auth_token": "cfg-token",
                "ignore_ssl": True,
                "api_url": "cfg-api-url",
            },
            {"TS_ORG": "env-org", "TS_API_URL": "env-api-url"},
            {
                "org": "arg-org",
                "api_url": "arg-api-url",
                "auth_token": "cfg-token",
                "ignore_ssl": True,
            },
        ),
        (
            {"org": "arg-org", "ignore_ssl": False},
            None,
            {"TS_ORG": "env-org", "TS_API_URL": "env-api-url"},
            {
                "org": "arg-org",
                "api_url": "env-api-url",
                "auth_token": None,
                "ignore_ssl": False,
            },
        ),
        (
            {},
            {
                "org": "cfg-org",
                "auth_token": "cfg-token",
                "ignore_ssl": True,
                "api_url": "cfg-api-url",
            },
            {"TS_ORG": "env-org", "TS_API_URL": "env-api-url"},
            {
                "org": "cfg-org",
                "api_url": "cfg-api-url",
                "auth_token": "cfg-token",
                "ignore_ssl": True,
            },
        ),
    ],
)
def test_ensure_args(args, cfg, envs, expected):
    os.environ.clear()
    os.environ.update(envs)
    if cfg:
        args["config"] = io.StringIO(json.dumps(cfg))
    parsed_args = argparse.Namespace(**args)
    __ensure_args(parsed_args)
    assert getattr(parsed_args, "api_url", None) == expected["api_url"]
    assert getattr(parsed_args, "org", None) == expected["org"]
    assert getattr(parsed_args, "auth_token", None) == expected["auth_token"]
    assert getattr(parsed_args, "ignore_ssl", None) == expected["ignore_ssl"]


@pytest.mark.parametrize(
    "namespace",
    [
        # valid namespaces
        "private-123",
        "private-a-b-c-1",
        "private-my-namespace-123",
        "private-Test-Namespace",
        "private-my-123-namespace",
    ],
)
def test_namespace_type_valid(namespace):
    validated_namespace = __namespace_type(namespace)
    assert validated_namespace == namespace


@pytest.mark.parametrize(
    "namespace",
    [
        # invalid namespaces
        "nonprivate-test-namespace",
        "common-org-123",
        "private-t3st-n@m3sp@ce",
        "private-a-b-c-",
        "private---a-b",
        "private-my--namespace",
        "-private-namespace",
        "private-my-123-namespace-" "-private-namespace-",
    ],
)
def test_namespace_type_invalid(namespace):
    with pytest.raises(argparse.ArgumentTypeError):
        __namespace_type(namespace)

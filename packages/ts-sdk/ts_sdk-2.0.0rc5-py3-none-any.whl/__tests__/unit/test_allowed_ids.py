import json
from importlib.resources import path
from pathlib import Path
from typing import List
from unittest.mock import patch

import pytest

from ts_sdk.task.__util_config import (
    IDS,
    MISSING_ALLOWED_IDS,
    AllowedIDS,
    FunctionConfig,
    IDSInvalidWrite,
    IDSNotAllowed,
)


def test_allowed_ids_when_allowedIds_is_a_dict():
    # Arrange
    ids = {"namespace": "common", "slug": "example", "version": "v1.0.0"}
    allowed_ids_str = "common/example:v1.0.0"
    non_allowed_ids_str = "common/non-allowed-ids:v1.0.0"
    allowed_ids = AllowedIDS.from_allowedIds(ids)

    # Act and Assert
    assert isinstance(allowed_ids.allowed_ids, list)
    assert len(allowed_ids.allowed_ids) == 1
    assert isinstance(allowed_ids.allowed_ids[0], IDS)
    assert (
        allowed_ids.get_ids_to_be_written("common/example:v1.0.0")
        == "common/example:v1.0.0"
    )
    assert allowed_ids.get_ids_to_be_written(None) == "common/example:v1.0.0"

    with pytest.raises(IDSNotAllowed):
        allowed_ids.get_ids_to_be_written(non_allowed_ids_str)

    # Test is_reconcilable
    assert allowed_ids.is_reconcilable(allowed_ids_str)
    assert allowed_ids.is_reconcilable(None)
    with pytest.raises(IDSNotAllowed):
        allowed_ids.is_reconcilable(non_allowed_ids_str)


def test_allowed_ids_when_allowedIds_is_a_list_dict():
    # Arrange
    ids = [
        {"namespace": "common", "slug": "example", "version": "v1.0.0"},
        {"namespace": "common", "slug": "example", "version": "v1.2.0"},
    ]
    allowed_ids = AllowedIDS.from_allowedIds(ids)
    allowed_ids_str = "common/example:v1.0.0"
    non_allowed_ids_str = "common/non-allowed-ids:v1.0.0"

    # Act and Assert
    assert isinstance(allowed_ids.allowed_ids, List)
    assert allowed_ids.get_ids_to_be_written(allowed_ids_str) == "common/example:v1.0.0"

    with pytest.raises(IDSInvalidWrite):
        allowed_ids.get_ids_to_be_written(None)

    with pytest.raises(IDSNotAllowed):
        allowed_ids.get_ids_to_be_written(non_allowed_ids_str)

    # Test is_reconcilable
    assert allowed_ids.is_reconcilable(allowed_ids_str)
    with pytest.raises(IDSNotAllowed):
        allowed_ids.is_reconcilable(non_allowed_ids_str)


def test_allowed_ids_when_allowedIds_is_a_list_of_single_dict():
    # Arrange
    ids = [
        {"namespace": "common", "slug": "example", "version": "v1.0.0"},
    ]
    allowed_ids = AllowedIDS.from_allowedIds(ids)
    allowed_ids_str = "common/example:v1.0.0"
    non_allowed_ids_str = "common/non-allowed-ids:v1.0.0"

    # Act and Assert
    assert isinstance(allowed_ids.allowed_ids, List)
    assert allowed_ids.get_ids_to_be_written(allowed_ids_str) == allowed_ids_str

    allowed_ids.get_ids_to_be_written(None) == allowed_ids_str

    with pytest.raises(IDSNotAllowed):
        allowed_ids.get_ids_to_be_written(non_allowed_ids_str)

    assert allowed_ids.is_reconcilable(allowed_ids_str)
    with pytest.raises(IDSNotAllowed):
        allowed_ids.is_reconcilable(non_allowed_ids_str)


def test_allowed_ids_when_allowedIds_is_null():
    ids = None

    allowed_ids = AllowedIDS(ids)

    with pytest.raises(IDSInvalidWrite):
        allowed_ids.get_ids_to_be_written("common/example:v1.0.0")

    with pytest.raises(IDSInvalidWrite):
        allowed_ids.get_ids_to_be_written(None)

    with pytest.raises(IDSInvalidWrite):
        allowed_ids.is_reconcilable("common/example:v1.0.0")


def test_function_config_when_task_script_config_is_empty():
    task_script_config = {}

    func_config = FunctionConfig.from_task_script_config(task_script_config, "slug")

    assert func_config.allowed_ids == MISSING_ALLOWED_IDS


def test_function_config_when_config_for_function_slug_exist():
    allowed_ids = {"namespace": "common", "slug": "my-ids", "version": "v1.0.0"}
    task_script_config = {
        "functions": [
            {
                "slug": "generates-ids",
                "function": "main.generate_ids",
                "allowedIds": allowed_ids,
            },
        ]
    }
    allowed_ids_obj = AllowedIDS.from_allowedIds(allowed_ids)

    func_config = FunctionConfig.from_task_script_config(
        task_script_config, "generates-ids"
    )

    assert func_config.allowed_ids == allowed_ids_obj


def test_function_config_when_config_for_function_slug_does_not_exist():
    allowed_ids = {"namespace": "common", "slug": "my-ids", "version": "v1.0.0"}
    task_script_config = {
        "functions": [
            {
                "slug": "generates-ids",
                "function": "main.generate_ids",
                "allowedIds": allowed_ids,
            },
        ]
    }

    func_config = FunctionConfig.from_task_script_config(
        task_script_config, "other_slug"
    )

    assert func_config.allowed_ids == MISSING_ALLOWED_IDS

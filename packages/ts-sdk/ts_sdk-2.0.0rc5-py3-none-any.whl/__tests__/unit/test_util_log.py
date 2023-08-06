import datetime
from unittest.mock import patch

import pytest
import simplejson as json
from freezegun import freeze_time

from ts_sdk.task.__util_log import Log, LogLevel
from ts_sdk.task.log_codes.log_code import LogCode
from ts_sdk.task.log_codes.log_code_collection import LogCodeCollection

ANY_CONTEXT = {"workflowId": "unitANY_LOG_DICT_id"}
ANY_LOG_DICT = {"key1": 1, "key2": 1, "key3": "jacob"}


@pytest.mark.parametrize(
    "input_, expected_message",
    [
        (("Test 1",), "Test 1"),
        (("1A", type(ANY_LOG_DICT)), "1A <class 'dict'>"),
        (("1B", type(ANY_LOG_DICT).__name__), "1B dict"),
        (("1C", ANY_LOG_DICT.keys()), "1C dict_keys(['key1', 'key2', 'key3'])"),
        (("1D", ANY_LOG_DICT), "1D {'key1': 1, 'key2': 1, 'key3': 'jacob'}"),
        (("1E", list(ANY_LOG_DICT.keys())[0]), "1E key1"),
        (("1F", list(ANY_LOG_DICT.keys())), "1F ['key1', 'key2', 'key3']"),
    ],
)
def test_log(input_, expected_message):
    """Test log function"""
    with patch("builtins.default_print") as default_print_mock:
        with freeze_time("2022-01-18"):
            # Arrange
            logger = Log(ANY_CONTEXT)

            # Act
            logger.log(*input_)
            actual = json.loads(default_print_mock.call_args[0][0])

            # Assert
            expected = {
                "message": expected_message,
                **ANY_CONTEXT,
                "level": "info",
                "timestamp": datetime.datetime.now().isoformat(),
            }
            default_print_mock.assert_called_once()
            assert actual == expected


@pytest.mark.parametrize("log_level", [LogLevel.DEBUG, LogLevel.INFO])
def test_log_with_level_returns_message_and_log_level(log_level):
    """Test that log_with_level call contains unedited message and correct log_level when passed"""
    with patch("builtins.default_print") as default_print_mock:
        # Arrange
        msg = "This is a log message"
        logger = Log(ANY_CONTEXT)

        # Act
        logger._log_with_level(msg, log_level)
        actual = json.loads(default_print_mock.call_args[0][0])

        # Assert
        default_print_mock.assert_called_once()
        assert msg == actual["message"]
        assert log_level == actual["level"]


@pytest.mark.parametrize("log_level", [LogLevel.WARNING, LogLevel.ERROR])
def test_log_with_level_returns_message_log_level_and_code(log_level):
    """Test that log_with_level call contains unedited message, correct log_level and correct code

    Unlike DEBUG and INFO log levels, WARNING and ERROR levels also require a code"""
    with patch("builtins.default_print") as default_print_mock:
        # Arrange
        msg = "This is a log message"
        logger = Log(ANY_CONTEXT)
        code = LogCodeCollection.generic

        # Act
        logger._log_with_level(msg, log_level, code)
        actual = json.loads(default_print_mock.call_args[0][0])

        # Assert
        default_print_mock.assert_called_once()
        assert msg == actual["message"]
        assert log_level == actual["level"]
        assert code.code == actual["code"]
        assert code.code_message == actual["codeMessage"]


def test_log_with_level_returns_empty_extra_field_and_empty_code():
    """Test that log_with_level call contains empty "extra" field + no code when no "extra" field
    or code is passed"""
    with patch("builtins.default_print") as default_print_mock:
        # Arrange
        msg = "This message will not be checked"
        logger = Log(ANY_CONTEXT)

        # Act
        logger._log_with_level(msg, LogLevel.DEBUG)
        actual = json.loads(default_print_mock.call_args[0][0])

        # Assert
        default_print_mock.assert_called_once()
        assert {} == actual["extra"]
        assert "code" not in actual
        assert "codeMessage" not in actual


def test_log_with_level_returns_dictionary_in_extra_field():
    """Test that log_with_level call contains dictionary when dictionary is passed in extra
    field"""
    with patch("builtins.default_print") as default_print_mock:
        # Arrange
        msg = "This message will not be checked"
        extra = {
            "key1": 1,
            "key2": "I'm a key",
            "key3": 2.0,
        }
        logger = Log(ANY_CONTEXT)

        # Act
        logger._log_with_level(msg, LogLevel.DEBUG, extra=extra)
        actual = json.loads(default_print_mock.call_args[0][0])

        # Assert
        default_print_mock.assert_called_once()
        assert extra == actual["extra"]


@pytest.mark.parametrize(
    "extra",
    [
        ("a", "b", "c"),
        ["a", "b", "c"],
    ],
)
def test_log_with_level_returns_object_in_data_field(extra):
    """Test that log_with_level call contains object in 'data' field when an object is passed"""
    with patch("builtins.default_print") as default_print_mock:
        # Arrange
        msg = "This message will not be checked"
        logger = Log(ANY_CONTEXT)

        # Act
        logger._log_with_level(msg, LogLevel.DEBUG, extra=extra)
        actual = json.loads(default_print_mock.call_args[0][0])

        # Assert
        default_print_mock.assert_called_once()
        assert {"data": json.loads(json.dumps(extra))} == actual["extra"]


def test_log_with_level_error_on_invalid_code():
    """Test that log_with_level returns two logs, sanitized original and error log when an invalid
    instance of a log code is passed"""
    with patch("builtins.default_print") as default_print_mock:
        # Arrange
        level = LogLevel.INFO
        log_code = LogCode(code_message="ThisIsValidMessage", code=-1)
        logger = Log(ANY_CONTEXT)

        # Act, Assert
        logger._log_with_level("msg", level, log_code)

        assert default_print_mock.call_count == 2
        actual_log = json.loads(default_print_mock.call_args_list[0][0][0])
        actual_error_log = json.loads(default_print_mock.call_args_list[1][0][0])

        assert level == actual_log["level"]
        assert LogCodeCollection.generic.code == actual_log["code"]
        assert LogCodeCollection.generic.code_message == actual_log["codeMessage"]

        assert LogLevel.ERROR == actual_error_log["level"]
        assert actual_error_log["message"].startswith(
            "Invalid input to logging method.\n"
        )
        assert "outside of valid range" in actual_error_log["message"]
        assert LogCodeCollection.invalid_raw_input_data.code == actual_error_log["code"]
        assert (
            LogCodeCollection.invalid_raw_input_data.code_message
            == actual_error_log["codeMessage"]
        )
        assert log_code.code == actual_error_log["original"]["code"]
        assert "InvalidLogInput" == actual_error_log["exception"]["type"]
        assert actual_error_log["exception"]["stack"].startswith(
            "Traceback (most recent call last):\n"
        )


@pytest.mark.parametrize(
    "invalid_code_message,partial_error_msg",
    [
        ("Non-alphanumeric message", "alphanumeric"),
        ("notPascalCaseMessage", "PascalCase"),
    ],
)
def test_log_with_level_error_on_invalid_code_message(
    invalid_code_message, partial_error_msg
):
    """Test that log_with_level returns two logs, sanitized original and error log when a log code
    with invalid code_message is passed"""
    with patch("builtins.default_print") as default_print_mock:
        # Arrange
        level = LogLevel.INFO
        log_code = LogCode(
            code_message=invalid_code_message, code=LogCodeCollection.generic.code
        )
        logger = Log(ANY_CONTEXT)

        # Act, Assert
        logger._log_with_level("msg", level, log_code)

        assert default_print_mock.call_count == 2
        actual_log = json.loads(default_print_mock.call_args_list[0][0][0])
        actual_error_log = json.loads(default_print_mock.call_args_list[1][0][0])

        assert level == actual_log["level"]
        assert LogCodeCollection.generic.code == actual_log["code"]
        assert LogCodeCollection.generic.code_message == actual_log["codeMessage"]

        assert LogLevel.ERROR == actual_error_log["level"]
        assert actual_error_log["message"].startswith(
            "Invalid input to logging method.\n"
        )
        assert partial_error_msg in actual_error_log["message"]
        assert LogCodeCollection.invalid_raw_input_data.code == actual_error_log["code"]
        assert (
            LogCodeCollection.invalid_raw_input_data.code_message
            == actual_error_log["codeMessage"]
        )
        assert log_code.code == actual_error_log["original"]["code"]
        assert "InvalidLogInput" == actual_error_log["exception"]["type"]
        assert actual_error_log["exception"]["stack"].startswith(
            "Traceback (most recent call last):\n"
        )


@pytest.mark.parametrize("level", [LogLevel.WARNING, LogLevel.ERROR])
@pytest.mark.parametrize("not_a_log_code_instance", [1, "CodeMessage"])
def test_log_with_level_error_when_log_code_bad_type(level, not_a_log_code_instance):
    """Test that log_with_level returns two logs, sanitized original and error log when an invalid
    instance of a log code is passed

    Code is only required for WARNING and ERROR log levels, so we are only concerned about the
    validity of Log Codes in those instances"""
    with patch("builtins.default_print") as default_print_mock:
        # Arrange
        msg = "This message should pass through (log code is the problem)"
        logger = Log(ANY_CONTEXT)

        # Act, Assert
        logger._log_with_level(msg, level, not_a_log_code_instance)

        assert default_print_mock.call_count == 2
        actual_log = json.loads(default_print_mock.call_args_list[0][0][0])
        actual_error_log = json.loads(default_print_mock.call_args_list[1][0][0])

        assert level == actual_log["level"]
        assert LogCodeCollection.generic.code == actual_log["code"]
        assert LogCodeCollection.generic.code_message == actual_log["codeMessage"]
        assert msg == actual_log["message"]

        assert LogLevel.ERROR == actual_error_log["level"]
        assert (
            f"Invalid input to logging method.\nExpected {type(LogCode)}, got "
            f"{type(not_a_log_code_instance)} instead" == actual_error_log["message"]
        )
        assert LogCodeCollection.invalid_raw_input_data.code == actual_error_log["code"]
        assert (
            LogCodeCollection.invalid_raw_input_data.code_message
            == actual_error_log["codeMessage"]
        )
        assert "InvalidLogInput" == actual_error_log["exception"]["type"]
        assert actual_error_log["exception"]["stack"].startswith(
            "Traceback (most recent call last):\n"
        )


@pytest.mark.parametrize(
    "msg", [["not", "a", "string"], {"key1": "error1", "key2": "a", "key3": 4.0}]
)
def test_log_with_level_error_when_message_bad_type(msg):
    """Test that log_with_level returns two logs, sanitized original and error log when a
    non-string message is passed"""
    with patch("builtins.default_print") as default_print_mock:
        # Arrange
        level = LogLevel.WARNING
        log_code = LogCodeCollection.generic
        logger = Log(ANY_CONTEXT)

        # Act, Assert
        logger._log_with_level(msg, level, log_code)

        assert default_print_mock.call_count == 2
        actual_log = json.loads(default_print_mock.call_args_list[0][0][0])
        actual_error_log = json.loads(default_print_mock.call_args_list[1][0][0])

        assert level == actual_log["level"]
        assert str(msg) == actual_log["message"]
        assert log_code.code == actual_log["code"]

        assert LogLevel.ERROR == actual_error_log["level"]
        assert LogCodeCollection.invalid_raw_input_data.code == actual_error_log["code"]
        assert (
            LogCodeCollection.invalid_raw_input_data.code_message
            == actual_error_log["codeMessage"]
        )
        assert (
            f"Invalid input to logging method.\nExpected message to be 'str', received {type(msg)}"
            " instead" == actual_error_log["message"]
        )
        assert "InvalidLogInput" == actual_error_log["exception"]["type"]
        assert actual_error_log["exception"]["stack"].startswith(
            "Traceback (most recent call last):\n"
        )


@pytest.mark.parametrize("level", [LogLevel.WARNING, LogLevel.ERROR])
def test_log_with_level_error_when_error_or_warn_missing_code(level):
    """Test that log_with_level logs an error when error or warning logs are called without a
    Log Code"""
    with patch("builtins.default_print") as default_print_mock:
        # Arrange
        msg = "This is warn or error message missing a LogCode"
        logger = Log(ANY_CONTEXT)

        # Act, Assert
        logger._log_with_level(msg, level)

        assert default_print_mock.call_count == 2
        actual_log = json.loads(default_print_mock.call_args_list[0][0][0])
        actual_error_log = json.loads(default_print_mock.call_args_list[1][0][0])

        assert level == actual_log["level"]
        assert msg == actual_log["message"]

        assert LogLevel.ERROR == actual_error_log["level"]
        assert LogCodeCollection.invalid_raw_input_data.code == actual_error_log["code"]
        assert (
            LogCodeCollection.invalid_raw_input_data.code_message
            == actual_error_log["codeMessage"]
        )
        assert (
            "Invalid input to logging method.\nMissing LogCode"
            == actual_error_log["message"]
        )
        assert "InvalidLogInput" == actual_error_log["exception"]["type"]
        assert actual_error_log["exception"]["stack"].startswith(
            "Traceback (most recent call last):\n"
        )

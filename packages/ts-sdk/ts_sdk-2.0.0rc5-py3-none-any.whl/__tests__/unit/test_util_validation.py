from typing import Any

import pytest

from ts_sdk.task.__util_validation import (
    validate_file_labels,
    validate_file_meta,
    validate_file_tags,
)
from ts_sdk.task.data_model import Label


def test_validate_file_meta():
    assert validate_file_meta(None)
    assert validate_file_meta(
        {
            "some": "stuff,-_ hello",
            "bool": True,
            "int": 123,
            "ok-key": "val with spaces",
        }
    )

    bad_inputs = [
        {"bad-key@": "stuff"},
        {"ok-key-bad-val": "stuff@"},
        {" leading-space-in key": "a_value"},
        {"trailing space in key ": "a_value"},
        {"a-key": " leading space in value"},
        {"a-key": "trailing space in value "},
    ]
    for bad_input in bad_inputs:
        with pytest.raises(ValueError):
            validate_file_meta(bad_input)


@pytest.mark.parametrize(
    "invalid_file_tag",
    [
        "🧑‍🔬 💡 ➡️ 💊 ",
        "invalid*tag",
        "more-than-128-chars " * 20,
        "invalid&+-tag",
        "@notherInvaidTag",
        "some@",
        "stuff$",
    ],
)
def test_invalid_file_tags(invalid_file_tag: str):
    with pytest.raises(ValueError):
        validate_file_tags([invalid_file_tag])


@pytest.mark.parametrize(
    "invalid_file_tag",
    [123, True, {}, []],
)
def test_invalid_tag_type(invalid_file_tag: Any):
    with pytest.raises(TypeError):
        validate_file_tags([invalid_file_tag])


@pytest.mark.parametrize(
    "valid_file_tag",
    [
        "+-_./",
        "Valid tag with spaces",
        "Valid_tag_with_digits_1233",
        "valid_mix/tag-1.2",
    ],
)
def test_valid_file_tags(valid_file_tag: str):
    assert validate_file_tags([valid_file_tag])


@pytest.mark.parametrize(
    "invalid_name",
    [
        1,
        10.99,
        True,
        False,
        None,
        ["a", "list"],
        {"a": "dict"},
        "Wröng ch@racter$",
        "",
        "\tnon-space-whitespace",
        "🧑‍🔬 💡 ➡️ 💊 ",
    ],
)
def test_invalid_label_name(invalid_name: Any) -> None:
    """Test that invalid names are caught"""
    # Arrange
    labels = [{"name": invalid_name, "value": "_"}]

    # Act and Assert
    with pytest.raises(ValueError):
        validate_file_labels(labels)


@pytest.mark.parametrize(
    "invalid_value",
    [
        1,
        10.99,
        True,
        False,
        None,
        ["a", "list"],
        {"a": "dict"},
        "Wröng ch@racter$",
        "",
        "\tnon-space-whitespace",
        "🧑‍🔬 💡 ➡️ 💊 ",
    ],
)
def test_invalid_label_value(invalid_value: Any) -> None:
    """Test that invalid values are caught"""
    # Arrange
    labels = [{"name": "_", "value": invalid_value}]

    # Act and Assert
    with pytest.raises(ValueError):
        validate_file_labels(labels)


@pytest.mark.parametrize(
    "valid_name",
    [
        "   leading_spaces",
        "trailing_spaces   ",
        "Some internal spaces - 3",
        "mix of outer + inner  spaces ",
    ],
)
def test_valid_label_name(valid_name: str) -> None:
    """Test that valid label do not trigger errors"""
    # Arrange
    labels = [{"name": valid_name, "value": "_"}]

    # Act
    is_valid = validate_file_labels(labels)

    # Assert
    assert is_valid is True


@pytest.mark.parametrize(
    "invalid_label_input",
    [
        "name:value",
        ["name", "value"],
        [("name", "value"), ("name2", "value2")],
        [{"key": "value"}, {"key2": "value2"}],
        range(10),
        [{"foo": "bar", "baz": "qux"}],
        [{"name": "_", "value": "_", "extra": "bad"}],
        [{"name": "_"}],
    ],
    ids=[
        "just a string",
        "strings in a list",
        "tuples in a list",
        "wrong key-value format",
        "weird iterable",
        "wrong keys",
        "too many keys",
        "not enough keys",
    ],
)
def test_invalid_label_inputs(invalid_label_input: Any) -> None:
    """Test that invalid inputs trigger errors"""
    # Arrange, Act and Assert
    with pytest.raises(ValueError):
        validate_file_labels(invalid_label_input)


@pytest.mark.parametrize(
    "valid_label_input",
    [
        [
            {"name": "boring", "value": "boring"},
        ],
        [
            {"name": "boring", "value": "boring"},
            {"name": "boring2", "value": "boring2"},
        ],
        [{"name": str(x), "value": str(x)} for x in range(25)],
        [
            {"name": "same_name", "value": "a_value"},
            {"name": "same_name", "value": "different_value"},
        ],
        ({"name": "same_name", "value": "a_value"},),
        (
            {"name": "same_name", "value": "a_value"},
            {"name": "same_name", "value": "different_value"},
        ),
    ],
    ids=[
        "single item",
        "two items",
        "many items",
        "two items with the same name",
        "single item tuple",
        "multiple items in tuple",
    ],
)
def test_valid_label_inputs(valid_label_input: Any) -> None:
    """Test that invalid inputs trigger errors"""
    # Arrange and Act
    assert validate_file_labels(valid_label_input)


@pytest.mark.parametrize(
    "empty_label_input",
    [
        None,
        [],
        (),
    ],
    ids=["none", "empty list", "empty tuple"],
)
def test_empty_list_label_input(empty_label_input: Any) -> None:
    """Test that validation functions differ in behaviour on the empty list"""
    assert validate_file_labels(empty_label_input) == False


NAME_MAX_LENGTH = 128
VALUE_MAX_LENGTH = 256
DELTA = 10


@pytest.mark.parametrize(
    "num_characters",
    range(NAME_MAX_LENGTH - DELTA, NAME_MAX_LENGTH + 1),
    ids=lambda num: f"name can have {num} characters",
)
def test_name_length(num_characters) -> None:
    """Test that key length is limited correctly"""
    # Arrange
    long_string = "x" * num_characters
    labels = [{"name": long_string, "value": "_"}]

    # Act
    assert validate_file_labels(labels)


@pytest.mark.parametrize(
    "num_characters",
    range(NAME_MAX_LENGTH + 1, NAME_MAX_LENGTH + DELTA + 2),
    ids=lambda num: f"name cannot have {num} characters",
)
def test_name_length_too_long(num_characters) -> None:
    """Test that key length is limited correctly"""
    # Arrange
    long_string = "x" * num_characters
    labels = [{"name": long_string, "value": "_"}]

    # Act and Assert
    with pytest.raises(ValueError):
        validate_file_labels(labels)


@pytest.mark.parametrize(
    "num_characters",
    range(VALUE_MAX_LENGTH - DELTA, VALUE_MAX_LENGTH + 1),
    ids=lambda num: f"value can have {num} characters",
)
def test_value_length(num_characters) -> None:
    """Test that key length is limited correctly"""
    # Arrange
    long_string = "x" * num_characters
    labels = [{"name": "_", "value": long_string}]

    # Act
    assert validate_file_labels(labels)


@pytest.mark.parametrize(
    "num_characters",
    range(VALUE_MAX_LENGTH + 1, VALUE_MAX_LENGTH + DELTA + 2),
    ids=lambda num: f"value cannot have {num} characters",
)
def test_value_length_too_long(num_characters) -> None:
    """Test that key length is limited correctly"""
    # Arrange
    long_string = "x" * num_characters
    labels = [{"name": "_", "value": long_string}]

    # Act and Assert
    with pytest.raises(ValueError):
        validate_file_labels(labels)


def test_validation_with_dataclass_labels():
    """Test that we can use the label dataclass in our validation functions"""
    # Arrange
    labels = [Label("name", "value"), Label(value="value2", name="name2")]

    # Act
    assert validate_file_labels(labels)

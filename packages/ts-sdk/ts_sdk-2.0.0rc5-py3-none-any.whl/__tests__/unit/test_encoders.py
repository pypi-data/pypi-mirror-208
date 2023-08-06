from dataclasses import dataclass
from typing import Dict, List

import pytest
import simplejson as json

from ts_sdk.task.encoders import DataclassEncoder
from ts_sdk.task.data_model import Label


def test_encode_label_dataclass_to_string():
    """Test Label Encoding"""
    # Arrange
    label = Label(name="a-name", value="a-value")

    # Act
    actual = json.dumps(label, cls=DataclassEncoder)

    # Assert
    assert actual == '{"name": "a-name", "value": "a-value"}'


def test_encode_new_dataclass_to_string():
    """Test that any dataclass will correctly encode as JSON"""

    # Arrange
    @dataclass
    class SomeDataclass:
        an_int: int
        a_float: float
        a_dict: Dict[str, str]
        a_list: List[str]
        a_bool: bool
        a_null: None

    test_instance = SomeDataclass(
        an_int=1337,
        a_float=3.1415,
        a_dict={"zip": "zop"},
        a_list=["foo", "bar"],
        a_bool=True,
        a_null=None,
    )

    # Act
    actual = json.dumps(test_instance, cls=DataclassEncoder)

    # Assert
    assert actual == (
        '{"an_int": 1337, "a_float": 3.1415, "a_dict": {"zip": "zop"},'
        ' "a_list": ["foo", "bar"], "a_bool": true, "a_null": null}'
    )


@pytest.mark.parametrize(
    "test_value", [1337, 3.1415, {"zip": "zop"}, ["foo", "bar"], True, False, None]
)
def test_encode_basic_conversions(test_value):
    """Test that basic datatypes are still correctly encoded with the new encoder"""

    # Act
    actual = json.dumps(test_value, cls=DataclassEncoder)
    expected = json.dumps(test_value)

    # Assert
    assert actual == expected

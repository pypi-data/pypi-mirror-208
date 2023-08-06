import pytest

from ts_sdk.task.__util_adapters import curry_for_each_method


def test_curry_for_each_method():
    format_implementation = {
        "not_a_method": "hello world",
        "identity": lambda x: x,
        "add": lambda x, y: x + y,
        "add_three": lambda x, y, z: x + y + z,
        "kwargs": lambda x=1, y=2: x + y,
    }
    curried_format = curry_for_each_method(format_implementation, 42)
    assert curried_format["identity"]() == 42
    assert curried_format["add"](10) == 52
    assert curried_format["add_three"](10, 2) == 54
    assert curried_format["not_a_method"] == "hello world"

    doubly_curried_format = curry_for_each_method(curried_format, 10)
    with pytest.raises(TypeError):
        doubly_curried_format["identity"]()
    assert doubly_curried_format["add"]() == 52
    assert doubly_curried_format["add_three"](2) == 54
    assert doubly_curried_format["not_a_method"] == "hello world"

    curry_multiple_args = curry_for_each_method(curried_format, 10, 2)
    with pytest.raises(TypeError):
        curry_multiple_args["identity"]()
    with pytest.raises(TypeError):
        curry_multiple_args["add"]()
    assert curry_multiple_args["add_three"]() == 54

    kwargs_curried = curry_for_each_method(format_implementation, x=10)
    assert kwargs_curried["kwargs"](y=42) == 52

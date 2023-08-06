import pytest

from ts_sdk.task.__util_decorators import cached, predicated_on


def test_cached():
    call_count = 0

    @cached
    def foo():
        nonlocal call_count
        call_count = call_count + 1
        return {}

    assert call_count == 0

    first_result = foo()
    assert call_count == 1
    assert first_result == {}

    second_result = foo()
    assert call_count == 1
    assert second_result == {}
    assert first_result is second_result

    third_result = foo(force=True)
    assert call_count == 2
    assert third_result == {}
    assert third_result is not second_result


def test_predicated_on():
    @predicated_on(lambda: False, "Error Message")
    def raises():
        return "foo"

    @predicated_on(lambda: True, "Error Message")
    def returns():
        return "foo"

    @predicated_on(lambda x, y: x or y, "Error Message")
    def maybe(x, y):
        return x or y

    assert returns() == "foo"

    with pytest.raises(ValueError, match="Error Message"):
        raises()
    assert maybe("foo", False) == "foo"
    with pytest.raises(ValueError, match="Error Message"):
        maybe(False, False)

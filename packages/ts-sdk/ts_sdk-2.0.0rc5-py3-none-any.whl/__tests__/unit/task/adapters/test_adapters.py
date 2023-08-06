import os

import pytest

from ts_sdk.task.__util_adapters import (
    CommunicationFormat,
    __make_implementation_from_formats,
    make_adapter,
)
from ts_sdk.task.__util_adapters.communication_format import (
    COMMUNICATION_FORMAT_ENV_KEY,
)
from ts_sdk.task.__util_adapters.make_adapter import select_versioned_value


def test_create_simple_adapter_implementation():
    history = {
        CommunicationFormat.V0: {"a": "a from v0", "b": "b from v0"},
    }
    formats = [CommunicationFormat.V0]

    implementation = __make_implementation_from_formats(history, formats)

    assert implementation == {"a": "a from v0", "b": "b from v0"}


def test_overwriting_in_later_format():
    history = {
        CommunicationFormat.V0: {"a": "a from v0", "b": "b from v0"},
        CommunicationFormat.V1: {"a": "a from v1"},
    }
    formats = [CommunicationFormat.V0, CommunicationFormat.V1]

    implementation = __make_implementation_from_formats(history, formats)

    assert implementation == {"a": "a from v1", "b": "b from v0"}


def test_merging_all_formats():
    history = {
        CommunicationFormat.V0: {"a": "a from v0", "b": "b from v0"},
        CommunicationFormat.V1: {"a": "a from v1"},
        CommunicationFormat.VZ: {"b": "b from vz"},
    }
    formats = [CommunicationFormat.V0, CommunicationFormat.V1, CommunicationFormat.VZ]

    implementation = __make_implementation_from_formats(history, formats)

    assert implementation == {"a": "a from v1", "b": "b from vz"}


def test_omitting_formats_not_listed():
    """
    Tests when there is a format in the format history, that is not actually needed right now
    """
    history = {
        CommunicationFormat.V0: {"a": "a from v0", "b": "b from v0"},
        CommunicationFormat.V1: {"a": "a from v1"},
        CommunicationFormat.VZ: {"b": "b from vz"},
    }
    formats = [CommunicationFormat.V0, CommunicationFormat.V1]

    implementation = __make_implementation_from_formats(history, formats)

    assert implementation == {"a": "a from v1", "b": "b from v0"}


def test_accepting_formats_not_in_history():
    """
    Tests when there is a format that is applicable, but not actually in the format history
    """
    history = {
        CommunicationFormat.V0: {"a": "a from v0", "b": "b from v0"},
        CommunicationFormat.VZ: {"b": "b from vz"},
    }
    formats = [CommunicationFormat.V0, CommunicationFormat.V1, CommunicationFormat.VZ]

    implementation = __make_implementation_from_formats(history, formats)

    assert implementation == {"a": "a from v0", "b": "b from vz"}


def test_inferring_applicable_formats():
    os.environ.update({COMMUNICATION_FORMAT_ENV_KEY: CommunicationFormat.V1.value})
    history = {
        CommunicationFormat.V0: {"a": "a from v0", "b": "b from v0"},
        CommunicationFormat.V1: {"a": "a from v1"},
        CommunicationFormat.VZ: {"b": "b from vz"},
    }

    adapter = make_adapter(history)

    assert adapter.a == "a from v1"
    assert adapter.b == "b from v0"


def test_creating_object_with_methods():
    os.environ.update({COMMUNICATION_FORMAT_ENV_KEY: CommunicationFormat.V0.value})

    def identity(x):
        return x

    def add(a, b):
        return a + b

    history = {CommunicationFormat.V0: {"add": add, "identity": identity}}

    adapter = make_adapter(history)

    assert adapter.identity("foobar") == "foobar"
    assert adapter.identity(history) is history
    assert adapter.add(4, 2) == 6


def test_default_format_missing():
    history = {}
    with pytest.raises(ValueError):
        make_adapter(history)


def test_unknown_implementation():
    os.environ.update({COMMUNICATION_FORMAT_ENV_KEY: "unknown"})

    def identity(x):
        return x

    history = {CommunicationFormat.V0: {"identity": identity}}

    adapter = make_adapter(history)

    with pytest.raises(NotImplementedError):
        adapter.identity("foo")


def test_shadowing_unknown_implementation():
    os.environ.update({COMMUNICATION_FORMAT_ENV_KEY: "unknown"})

    def identity(x):
        return x

    def add(a, b):
        return a + b

    history = {
        CommunicationFormat.V0: {"add": add, "identity": identity},
        CommunicationFormat.VZ: {"add": add},
    }

    adapter = make_adapter(history)

    assert adapter.add(4, 2) == 6

    with pytest.raises(NotImplementedError):
        adapter.identity("foo")


def test_selecting_one_value():
    def get_value():
        return select_versioned_value(
            {
                CommunicationFormat.V0: "Version Zero",
                CommunicationFormat.V1: "Version One",
            }
        )

    os.environ.update({COMMUNICATION_FORMAT_ENV_KEY: CommunicationFormat.V0.value})
    assert get_value() == "Version Zero"

    os.environ.update({COMMUNICATION_FORMAT_ENV_KEY: CommunicationFormat.V1.value})
    assert get_value() == "Version One"

    os.environ.update({COMMUNICATION_FORMAT_ENV_KEY: "unknown"})
    assert get_value() == "Version One"

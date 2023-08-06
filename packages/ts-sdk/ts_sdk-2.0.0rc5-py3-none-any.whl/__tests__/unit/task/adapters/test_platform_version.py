import os

from ts_sdk.task.__util_adapters.communication_format import (
    get_all_platform_formats,
    DEFAULT_COMMUNICATION_FORMAT,
    UNKNOWN_COMMUNICATION_FORMAT,
    CommunicationFormat,
    to_communication_format,
    COMMUNICATION_FORMAT_ENV_KEY,
    get_communication_format,
    get_formats_up_to,
)


def test_get_all_communication_formats():
    formats = get_all_platform_formats()

    # should return a list!
    assert isinstance(formats, list)

    # Default and unknown communication format should always be in the list
    assert len(formats) >= 2
    assert DEFAULT_COMMUNICATION_FORMAT in formats
    assert UNKNOWN_COMMUNICATION_FORMAT in formats

    # Every element in the list must be a CommunicationFormat
    assert all(
        [
            isinstance(communication_format, CommunicationFormat)
            for communication_format in formats
        ]
    )

    # Default communication format should always be at the beginning of the list
    assert formats.index(DEFAULT_COMMUNICATION_FORMAT) == 0
    # Unknown communication format should always be at the end of the list
    assert formats.index(UNKNOWN_COMMUNICATION_FORMAT) == len(formats) - 1


def test_to_communication_format():
    # If given nothing, defaults to default communication format
    assert to_communication_format(None) == DEFAULT_COMMUNICATION_FORMAT
    # If given something unrecognizable, returns unknown communication format
    assert to_communication_format("foobar") == UNKNOWN_COMMUNICATION_FORMAT
    # Should be able to parse a communication format
    assert to_communication_format("V0") == CommunicationFormat.V0
    assert to_communication_format("v0") == CommunicationFormat.V0
    assert to_communication_format("  v0 ") == CommunicationFormat.V0
    assert to_communication_format("v1") == CommunicationFormat.V1
    assert to_communication_format("V1") == CommunicationFormat.V1
    assert to_communication_format(" V1  ") == CommunicationFormat.V1


def test_get_communication_format():
    os.environ.update({COMMUNICATION_FORMAT_ENV_KEY: "V1"})
    communication_format = get_communication_format()
    assert communication_format == CommunicationFormat.V1


def test_get_formats_up_to():
    formats_up_to_zero = get_formats_up_to(CommunicationFormat.V0)
    formats_up_to_one = get_formats_up_to(CommunicationFormat.V1)
    formats_up_to_unknown = get_formats_up_to(CommunicationFormat.VZ)
    assert formats_up_to_zero == [CommunicationFormat.V0]
    assert formats_up_to_one == [CommunicationFormat.V0, CommunicationFormat.V1]
    assert formats_up_to_unknown[-1] == CommunicationFormat.VZ

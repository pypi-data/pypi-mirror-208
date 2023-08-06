from functools import reduce
from typing import List

from .communication_format import (
    get_formats_up_to,
    get_communication_format,
    DEFAULT_COMMUNICATION_FORMAT,
    UNKNOWN_COMMUNICATION_FORMAT,
)


def __make_implementation_from_formats(history: dict, formats):
    return reduce(
        lambda implementation, communication_format: {
            **implementation,
            **history.get(communication_format, {}),
        },
        formats,
        {},
    )


def __make_unsupported_method(method_name: str):
    def method(*args, **kwargs):
        raise NotImplementedError(f"{method_name} is not implemented")

    return method


def __create_unsupported_format(method_names: List[str]):
    return {
        method_name: __make_unsupported_method(method_name)
        for method_name in method_names
    }


def __validate_history(history: dict):
    if DEFAULT_COMMUNICATION_FORMAT not in history:
        raise ValueError(
            f"{DEFAULT_COMMUNICATION_FORMAT} implementation is required in format history"
        )


def __collect_methods_names(implementation: dict):
    return [k for k, v in implementation.items() if callable(v)]


def __decorate_history(history: dict) -> dict:
    method_names = __collect_methods_names(history[DEFAULT_COMMUNICATION_FORMAT])
    default_unsupported_format = __create_unsupported_format(method_names)
    unsupported_format = {
        **default_unsupported_format,
        **(
            history[UNKNOWN_COMMUNICATION_FORMAT]
            if UNKNOWN_COMMUNICATION_FORMAT in history
            else {}
        ),
    }
    return {**history, UNKNOWN_COMMUNICATION_FORMAT: unsupported_format}


def make_adapter(history: dict):
    """
    Allows you to declare an adapter through its format history, and a correct implementation
        will automatically be created at runtime
    :param history: A collection of partial implementations indexed by CommunicationFormat.
                    CommunicationFormat.V0 _must_ be supplied with a complete implementation
    :return: A merged implementation using methods up until the currently running CommunicationFormat
    """
    __validate_history(history)
    history = __decorate_history(history)
    current_format = get_communication_format()
    applicable_formats = get_formats_up_to(current_format)
    return Adapter(__make_implementation_from_formats(history, applicable_formats))


def select_versioned_value(history):
    """
    A bit of sugar for `make_adapter`
    Allows you to just supply values instead for format objects for each CommunicationFormat
    :param history:
    :return:
    """
    return make_adapter(
        {format: {"value": value} for format, value in history.items()}
    ).value


class Adapter(object):
    def __init__(self, implementation: dict):
        for k, v in implementation.items():
            setattr(self, k, v)

import os
from urllib.parse import urljoin

from ts_sdk.task.__util_adapters import make_adapter, CommunicationFormat


def get_endpoint_adapter():
    return make_adapter(
        {
            CommunicationFormat.V0: {
                "get_private_endpoint": os.environ.get,
                "get_public_endpoint": os.environ.get,
            },
            CommunicationFormat.V1: {
                "get_public_endpoint": lambda environment_key: urljoin(
                    os.environ.get(environment_key), "api"
                )
            },
        }
    )


def get_public_endpoint(environment_key):
    """
    This submodule is used for accessing endpoints bound in the process's environment
    These endpoints should not be accessed directly, as they may be decorated by this submodule
    """
    return get_endpoint_adapter().get_public_endpoint(environment_key)


def get_private_endpoint(environment_key):
    """
    This submodule is used for accessing endpoints bound in the process's environment
    These endpoints should not be accessed directly, as they may be decorated by this submodule
    """
    return get_endpoint_adapter().get_private_endpoint(environment_key)

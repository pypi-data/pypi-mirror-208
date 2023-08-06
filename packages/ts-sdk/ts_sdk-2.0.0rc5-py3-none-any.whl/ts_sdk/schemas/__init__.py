import json
import typing as t
from importlib.resources import read_text


def load(name: str) -> t.Any:
    return json.loads(read_text(__package__, name))


config = load("config.schema.json")

protocol = load("protocol.schema.json")

__all__ = ["config", "pipeline"]

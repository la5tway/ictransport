from os import environ
from typing import Any, TypeVar

from dataclass_factory import Factory

T = TypeVar("T")


def load_config(
    config_type: type[T],
    scope: str | None = None,
    delimeter: str = "__",
) -> T:
    data: dict[str, Any] = {}
    if scope:
        for k, v in environ.items():
            if k.startswith(scope):
                k = k.split(delimeter)[-1]
                data[k] = v
                data[k.lower()] = v
                data[k.upper()] = v
    else:
        for k, v in environ.items():
            scope, _, k = k.partition(delimeter)
            if not scope:
                continue
            scopes = (scope, scope.lower(), scope.upper())
            if scope not in data:
                for s in scopes:
                    data[s] = {}
            for s in scopes:
                data[s][k] = v
                data[s][k.lower()] = v
                data[s][k.upper()] = v
    dcf = Factory()
    return dcf.load(data, config_type)

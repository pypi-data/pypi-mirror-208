from typing import Any, MutableMapping

import toml

_pyproject_singleton = None


def get_pyproject() -> MutableMapping[str, Any]:
    global _pyproject_singleton

    if _pyproject_singleton is None:
        _pyproject_singleton = toml.load("pyproject.toml")

    return _pyproject_singleton

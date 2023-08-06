import hashlib
from pathlib import Path
from typing import Any, Union

from blake3 import blake3
from typing import Protocol


class Hasher(Protocol):
    def hexdigest(self) -> str:
        ...

    def update(self, __data: Any) -> None:
        ...


def hasher(family: str = "sha256", **kwargs) -> Hasher:
    """

    :param family: str:  (Default value = "sha256")
    :param **kwargs:

    """
    if family in hashlib.algorithms_available:
        return hashlib.new(family)

    family = family.lower()
    if family == "blake3":
        return blake3(**kwargs)
    else:
        raise NotImplementedError()


_hasher_fn = hasher


def hexadecimal(
    family: str = None, hasher: Hasher = None, value: Union[str, bytes, Path] = None
) -> str:
    """

    :param family: A digest algorithm supported by python standard lib (eg: sha256) or one of the custom ones: blake3.
    :param hasher: A hasher created with `hasher(...)`
    :param value: A value to digest
    :param family: str:  (Default value = None)
    :param hasher: Hasher:  (Default value = None)
    :param value: Union[str:
    :param bytes]:  (Default value = None)
    :returns: s Message digest

    """
    if family is not None and isinstance(family, str):
        hasher = _hasher_fn(family=family)
    elif hasher is not None:
        pass
    else:
        raise ValueError("Missing family or hasher")

    if isinstance(value, str):
        value = value.encode("utf-8")
        hasher.update(value)
    elif isinstance(value, bytes):
        hasher.update(value)
    elif isinstance(value, Path):
        # Support: py38 and better
        with open(value, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
    else:
        raise NotImplementedError()

    return hasher.hexdigest()

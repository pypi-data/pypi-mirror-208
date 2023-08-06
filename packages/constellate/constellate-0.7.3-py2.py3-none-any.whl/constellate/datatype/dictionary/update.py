from enum import IntEnum, auto
from typing import Dict, Any


class DictCondition(IntEnum):
    MISSING = auto()
    PRESENT = auto()
    ALWAYS = auto()


def dict_update(
    map: Dict = None,
    when: DictCondition = DictCondition.MISSING,
    key: Any = None,
    value: Any = None,
) -> None:
    if when == DictCondition.MISSING:
        if key not in map:
            map.update({key: value})
    elif when == DictCondition.PRESENT:
        if key in map:
            map.update({key: value})
    elif when == DictCondition.ALWAYS:
        map.update({key: value})
    else:
        # No condition, no action, programming error
        raise ValueError()

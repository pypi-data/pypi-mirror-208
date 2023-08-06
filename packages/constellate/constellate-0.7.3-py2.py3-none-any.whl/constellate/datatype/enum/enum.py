from enum import Flag


def has_flag(flags: Flag, checked_flag: Flag) -> bool:
    if not (
        isinstance(flags, Flag)
        and isinstance(checked_flag, Flag)
        and isinstance(flags, type(checked_flag))
    ):
        raise ValueError("value or accepted is not a class/subclass of Flag")
    return flags & checked_flag == checked_flag

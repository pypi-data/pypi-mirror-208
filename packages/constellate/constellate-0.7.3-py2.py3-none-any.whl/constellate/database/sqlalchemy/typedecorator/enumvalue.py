from typing import Callable, Any

import sqlalchemy
from sqlalchemy import TypeDecorator


def _default_property_selector(value: Any = None, noneable: bool = None):
    if value is None:
        if noneable:
            return value
        raise ValueError("value is None while None is not allowed as enum value")

    return value.value


class EnumValue(TypeDecorator):
    """Column type for storing Python Enum's value in a database TEXT column (by default).

    User must almost always subclass (eg: `EnumInteger`)

    This will behave erratically if a database value does not correspond to map to a known enum value.


    """

    # underlying database type
    impl = sqlalchemy.types.String
    cache_ok = False

    def __init__(
        self,
        enum_type: Any = None,
        enum_property_selector: Callable[[Any, bool], Any] = _default_property_selector,
        noneable: bool = False,
    ):
        super().__init__()
        self.enum_type = enum_type
        self._noneable = noneable
        self._enum_property_selector = enum_property_selector

    def process_bind_param(self, value, dialect):
        # App Enum value to DB's datatype
        try:
            if isinstance(value, self.enum_type) or (
                self._noneable and isinstance(value, type(None))
            ):
                return self._enum_property_selector(value=value, noneable=self._noneable)
            raise ValueError("Bad type")
        except ValueError as e:
            raise ValueError(
                f"expected %s value {'or None' if self._noneable else ''}, got %s"
                % (self.enum_type.__name__, value.__class__.__name__)
            ) from e

    def process_result_value(self, value, dialect):
        # DB integer value to App Enum value
        if value is None and self._noneable:
            return None
        return self.enum_type(value)

    def copy(self, **kwargs):
        return self.__class__(
            enum_type=self.enum_type,
            enum_property_selector=self._enum_property_selector,
            noneable=self._noneable,
        )

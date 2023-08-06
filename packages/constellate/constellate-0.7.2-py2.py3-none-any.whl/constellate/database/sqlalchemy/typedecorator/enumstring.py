from typing import Callable, Union

import sqlalchemy
from typing_extensions import TypeAlias

from constellate.database.sqlalchemy.typedecorator.enumvalue import (
    EnumValue,
    _default_property_selector,
)

_EnumType: TypeAlias = Union[str]


class EnumString(EnumValue):
    """Column type for storing Python enums in a database TEXT column."""

    impl = sqlalchemy.types.String
    cache_ok = False

    def __init__(
        self,
        enum_type: _EnumType = None,
        enum_property_selector: Callable[[_EnumType, bool], _EnumType] = _default_property_selector,
        noneable: bool = False,
    ):
        super().__init__(
            enum_type=enum_type, enum_property_selector=enum_property_selector, noneable=noneable
        )

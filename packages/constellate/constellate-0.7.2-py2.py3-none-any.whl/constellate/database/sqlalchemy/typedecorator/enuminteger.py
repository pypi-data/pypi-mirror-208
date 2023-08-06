from typing import Callable, Union

import sqlalchemy
from typing_extensions import TypeAlias

from constellate.database.sqlalchemy.typedecorator.enumvalue import (
    EnumValue,
    _default_property_selector,
)

EnumType: TypeAlias = Union[int]


class EnumInteger(EnumValue):
    """Column type for storing Python enums in a database INTEGER column."""

    impl = sqlalchemy.types.Integer
    cache_ok = False

    def __init__(
        self,
        enum_type: EnumType = None,
        enum_property_selector: Callable[[EnumType, bool], EnumType] = _default_property_selector,
        noneable: bool = False,
    ):
        super().__init__(
            enum_type=enum_type, enum_property_selector=enum_property_selector, noneable=noneable
        )

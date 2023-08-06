from enum import Enum


class RelationshipType(Enum):
    NONE = "none"
    ONE_TO_ONE = "1-to-1"
    ONE_TO_MANY = "1-to-n"
    MANY_TO_ONE = "n-to-1"
    MANY_TO_MANY = "n-to-n"

from sqlalchemy import DateTime
from sqlalchemy_utils import EnrichedDateTimeType
from sqlalchemy_utils.types.enriched_datetime import PendulumDateTime


class _TIMESTAMPZ(DateTime):
    # Class created to force asyncpg to use TIMESTAMP with TIMEZONE
    __visit_name__ = "TIMESTAMP"

    def __init__(self, timezone=True):
        super().__init__(timezone=timezone)


class TimestampTZ(EnrichedDateTimeType):
    cache_ok = False
    impl = _TIMESTAMPZ

    def __init__(self, *args, **kwargs):
        super().__init__(*args, datetime_processor=PendulumDateTime, **kwargs)

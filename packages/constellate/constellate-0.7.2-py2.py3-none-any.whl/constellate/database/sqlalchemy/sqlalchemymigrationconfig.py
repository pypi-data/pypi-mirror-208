import attr as attr


@attr.s(kw_only=True, auto_attribs=True)
class _MigrationConfig:
    # Migration can run concurrently with other migration on other (database,schema) configuration
    concurrent: bool = False

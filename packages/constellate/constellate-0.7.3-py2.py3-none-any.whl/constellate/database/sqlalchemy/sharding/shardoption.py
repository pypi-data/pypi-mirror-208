from sqlalchemy.orm import UserDefinedOption


class SetShardSchemaOption(UserDefinedOption):
    # FIXME: (high) Maybe this class won't be needed when this is implemented https://github.com/sqlalchemy/sqlalchemy/issues/7226#issuecomment-950440743
    propagate_to_loaders = True

    def _gen_cache_key(self, anon_map, bindparams):
        return (self.payload,)


class SetShardEngineOption(UserDefinedOption):
    propagate_to_loaders = True

    def _gen_cache_key(self, anon_map, bindparams):
        return (self.payload,)

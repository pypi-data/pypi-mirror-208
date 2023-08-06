from enum import auto, Flag


class LogMode(Flag):
    # Environment
    ENV_PRODUCTION = auto()
    ENV_STAGING = auto()
    ENV_LOCAL = auto()
    # Interactive
    INTERACTIVE_YES = auto()
    INTERACTIVE_NO = auto()
    # Level of details
    DETAIL_NORMAL = auto()
    DETAIL_TRACE = auto()
    # Server+Client or Standalone Logger
    OPERATE_STANDALONE = auto()
    OPERATE_SERVER = auto()
    OPERATE_CLIENT = auto()
    OPERATE_SERVER_OPTION_NATIVE = auto()  # deprecated
    OPERATE_SERVER_OPTION_ZEROMQ = auto()
    OPERATE_SERVER_OPTION_DEFAULT = auto()
    # Log Message Dispatchness
    DISPATCH_SYNC = auto()
    DISPATCH_ASYNC = auto()

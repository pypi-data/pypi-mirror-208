import logging
import os
import sys
import threading
import uuid
from logging.config import dictConfig
from pathlib import PurePath
from typing import Dict, Union, Tuple, List

import pendulum
from narration._handler.common.handler.base_handler import NarrationHandler
from narration._misc.constants import DispatchMode
from narration.constants import Backend
from narration.narration import setup_server_handlers, setup_client_handlers

from constellate.datatype.enum.enum import has_flag
from constellate.logger.handler.stringhandler import StringHandler
from constellate.logger.loggers import Loggers
from constellate.logger.logmode import LogMode


class _LogDefault:
    LOGS_DIRECTORY = os.getcwd()
    ROOT_LOGGER_NAME = "default"
    MODE = LogMode = (
        LogMode.ENV_PRODUCTION
        | LogMode.INTERACTIVE_NO
        | LogMode.DETAIL_NORMAL
        | LogMode.OPERATE_STANDALONE
        | LogMode.DISPATCH_SYNC
    )
    TEMPLATE_CONFIG = {
        "root": {
            "logger": "default",  # Field mandatory
            "app": {
                "logger": "default",  # Field mandatory
            },
            "network": {
                "logger": "default",
            },
            "database": {
                "logger": "default",
            },
            "media": {
                "logger": "default",
            },
        }
    }


class Log:
    _LOGGER_NAMES_RETRIEVED = {}
    # Logger instance are held by python sdk private dictionary. Only loggers settings are tracked
    _FQDN_LOGGER_SETTINGS_EXTERNAL = {}
    # Logger instance are held by python sdk private dictionary. Only loggers names are tracked
    _FQDN_LOGGER_NAMES_EXTERNAL = set()

    _JOB_LOGGER_NAMES_LOCK = threading.Lock()
    _LOGS_DIRECTORY = _LogDefault.LOGS_DIRECTORY
    _ROOT_LOGGER_NAME = _LogDefault.ROOT_LOGGER_NAME

    def default_config_dict(
        root_name=None,
        mode: LogMode = _LogDefault.MODE,
        template: Dict[str, object] = _LogDefault.TEMPLATE_CONFIG,
    ):
        COLOR_MARKER = "%(log_color)s"

        def console_formatter(name=None, mode=None, normal_fmt=None, trace_fmt=None):
            remove_color = not has_flag(mode, LogMode.INTERACTIVE_YES)
            fmt = trace_fmt if has_flag(mode, LogMode.DETAIL_TRACE) else normal_fmt
            fmt = fmt.replace(COLOR_MARKER, "") if remove_color else fmt
            colored = "colored" if not remove_color else "monocolor"
            key = f"console_{colored}_{name}"
            return (
                key,
                {
                    key: {
                        "class": "logging.Formatter"
                        if remove_color
                        else "colorlog.ColoredFormatter",
                        "format": fmt,
                        "date_fmt": "%Y-%m-%d %H:%M:%S",
                    }
                },
            )

        def file_formatter(name=None, mode=None, normal_fmt=None, trace_fmt=None):
            key = f"fmt_{name}"
            fmt = trace_fmt if has_flag(mode, LogMode.DETAIL_TRACE) else normal_fmt
            return (key, {key: {"class": "logging.Formatter", "format": fmt}})

        def rotating_file_handler(name=None, fmt_id=None, filename=None) -> Tuple[str, Dict]:
            key = f"rfhd_{name}"
            return (
                key,
                {
                    key: {
                        "class": "logging.handlers.TimedRotatingFileHandler",
                        "filename": filename,
                        "when": "W0",
                        "backupCount": 4,
                        "encoding": "utf-8",
                        "delay": False,
                        "utc": True,
                        "atTime": pendulum.time(23, 59, 0, 0),
                        "formatter": fmt_id,
                    }
                },
            )

        def console_handler(name=None, formatter=None) -> Tuple[str, Dict]:
            key = f"console_{name}"
            return (
                key,
                {
                    key: {
                        "class": "logging.StreamHandler",
                        "formatter": formatter,
                        "stream": sys.stdout,
                    }
                },
            )

        def logger(
            name=None,
            handlers=[],
            levelIFProd="INFO",
            mode=None,
            levelIfNotProd="DEBUG",
            propagate=False,
        ):
            return {
                f"{name}": {
                    "handlers": handlers,
                    "level": levelIFProd
                    if has_flag(mode, LogMode.ENV_PRODUCTION)
                    else levelIfNotProd,
                    "propagate": propagate,
                }
            }

        console_fmt_id, console_fmt = console_formatter(
            name="console",
            mode=mode,
            normal_fmt=f"%(asctime)s: P%(process)d: %(processName)s: T%(thread)d: %(threadName)s: {COLOR_MARKER}%(levelname)s: %(message)s",
            trace_fmt=f"%(asctime)s: P%(process)d: %(processName)s: T%(thread)d: %(threadName)s: %(name)s: {COLOR_MARKER}%(levelname)s: %(message)s",
        )
        file_fmt_id, file_fmt = file_formatter(
            name="detailed",
            mode=mode,
            normal_fmt="%(asctime)s: P%(process)d: %(processName)s: T%(thread)d: %(threadName)s: %(levelname)s: %(message)s",
            trace_fmt="%(asctime)s: P%(process)d: %(processName)s: T%(thread)d: %(threadName)s: %(levelname)s: %(message)s",
        )
        root_file_fmt_id, root_file_fmt = file_formatter(
            name="root_detailed",
            mode=mode,
            normal_fmt="%(asctime)s: P%(process)d: %(processName)s: T%(thread)d: %(threadName)s: %(levelname)s: %(message)s",
            trace_fmt="%(asctime)s: P%(process)d: %(processName)s: T%(thread)d: %(threadName)s: %(name)s: %(levelname)s: %(message)s",
        )

        console_hd_id, console_hd = console_handler(name=f"{root_name}", formatter=console_fmt_id)

        config = {
            "disable_existing_loggers": False,
            "version": 1,
            "formatters": {
                **console_fmt,
                **file_fmt,
                **root_file_fmt,
            },
            "handlers": {
                **console_hd,
                # More will be added lower in this function
            },
            "loggers": {
                # More will be added lower in this function
            },
        }

        # Generate additional handlers/loggers
        def update_config(config, previous_logger_parts, logger_part, template_logger_obj):
            is_root = len(previous_logger_parts) == 0
            is_logger = "logger" in template_logger_obj

            if is_logger:
                parts = list(previous_logger_parts)
                parts.append(logger_part)
                underscored_name = "_".join(parts)
                dot_name = ".".join(parts)

                # Generate handler
                custom_fhd_id, custom_fhd = rotating_file_handler(
                    name=f"{underscored_name}",
                    fmt_id=file_fmt_id,
                    filename=f"{Log._LOGS_DIRECTORY}/{dot_name}.log",
                )

                # Associate handler to config
                config["handlers"].update(custom_fhd)

                # Generate logger
                custom_logger = logger(
                    name=f"{dot_name}",
                    handlers=[console_hd_id, custom_fhd_id] if is_root else [custom_fhd_id],
                    levelIfNotProd="DEBUG",
                    mode=mode,
                    levelIFProd="INFO",
                    propagate=not is_root,
                )

                # Associate logger to config
                config["loggers"].update(custom_logger)

        def update_config_tree(config, template, previous_logger_parts):
            for logger_part, logger_obj in template.items():
                _previous_logger_parts = list(previous_logger_parts)
                logger_part = root_name if logger_part == "root" else logger_part
                update_config(config, _previous_logger_parts, logger_part, logger_obj)

                if isinstance(logger_obj, Dict):
                    _previous_logger_parts.append(logger_part)
                    update_config_tree(config, logger_obj, _previous_logger_parts)

        update_config_tree(config, template, [])

        return config

    @staticmethod
    def setup(
        root_logger_name: str = _LogDefault.ROOT_LOGGER_NAME,
        log_dir_path: str = _LogDefault.LOGS_DIRECTORY,
        mode: LogMode = _LogDefault.MODE,
        config_dict: Dict = None,
        template_config_dict: Dict = _LogDefault.TEMPLATE_CONFIG,
    ):
        Log._LOGS_DIRECTORY = log_dir_path
        Log._ROOT_LOGGER_NAME = root_logger_name

        # Load default logger config dict
        if config_dict is None:
            config_dict = Log.default_config_dict(
                root_name=Log._ROOT_LOGGER_NAME, mode=mode, template=template_config_dict
            )

        # Load declarative config
        try:
            dictConfig(config_dict)
        except BaseException as e:
            print(f"ERROR: Cannot configure loggers: {e}")
            raise

        # Keep track of loggers being setup
        logger_names = sorted(list(config_dict.get("loggers", {}).keys()))
        for name in logger_names:
            Log._FQDN_LOGGER_NAMES_EXTERNAL.add(name)

    @staticmethod
    def get_file_path(fileName=None):
        return (
            PurePath(Log._LOGS_DIRECTORY, fileName)
            if Log._LOGS_DIRECTORY is not None
            else PurePath(fileName)
        )

    @staticmethod
    def teardown_loggers(loggers: List[logging.Logger] = []):
        names = [logger.name for logger in loggers]
        for name in names:
            if name in Log._FQDN_LOGGER_NAMES_EXTERNAL:
                Log._FQDN_LOGGER_NAMES_EXTERNAL.remove(name)
            Log._LOGGER_NAMES_RETRIEVED.pop(name, None)

    @staticmethod
    def get_native_logger(name=None) -> Tuple[bool, logging.Logger]:
        """

        :param name:  (Default value = None)
        :returns: A logger instance and whether it existed before

        """
        exist = Log._LOGGER_NAMES_RETRIEVED.get(name, False)
        if not exist:
            Log._LOGGER_NAMES_RETRIEVED[name] = True
        return exist, logging.getLogger(name)

    @staticmethod
    def get_hierarchical_logger(
        name: str = None,
        mode: LogMode = LogMode.OPERATE_SERVER,
        mode_settings: Dict = {},
    ):
        """name_parts: List of a logger's split into parts. Eg: foo.bar.zoo => ['foo','bar','zoo']

        :param name: str:  (Default value = None)
        :param mode: LogMode:  (Default value = LogMode.OPERATE_SERVER)
        :param mode_settings: Dict:  (Default value = {})
        :returns: A logger instance

        """
        # Construct Fully Qualified Logger Name
        existed, logger = Log.get_native_logger(name=name)
        if not existed:
            # Client mode logger should not have any handlers set by default, as it will create as many handlers as
            # the original "server" logger had
            if has_flag(mode, LogMode.OPERATE_CLIENT):
                for handler in list(logger.handlers):
                    logger.removeHandler(handler)

        has_narration_handlers = next(
            filter(
                lambda v: v == True,
                [isinstance(handler, NarrationHandler) for handler in list(logger.handlers)],
            ),
            False,
        )
        if has_narration_handlers:
            # Loggers already setup with narration handlers must not be setup again
            return logger, Log._FQDN_LOGGER_SETTINGS_EXTERNAL.get(name, {})

        # Decide whether to propagate to upper logger
        if has_flag(mode, LogMode.OPERATE_SERVER):
            # Propagate log to ancestor loggers.
            logger.propagate = True
        elif has_flag(mode, LogMode.OPERATE_CLIENT):
            # Client logger's handlers must not propagate. The server's logger
            # handlers will do so if configured
            logger.propagate = False
        elif has_flag(mode, LogMode.OPERATE_STANDALONE):
            # Let initial loggers configuration decide
            pass

        # Gather log records into main process's logging thread for that logger
        # Other (forked) processed will simply send log records to the main process
        if has_flag(mode, LogMode.OPERATE_SERVER):
            ctx = mode_settings["ctx"]
            ctx_manager = mode_settings["ctx_manager"]
            backend = Backend.DEFAULT
            if has_flag(mode, LogMode.OPERATE_SERVER_OPTION_ZEROMQ):
                backend = Backend.ZMQ
            elif has_flag(mode, LogMode.OPERATE_SERVER_OPTION_NATIVE):
                backend = Backend.NATIVE
            elif has_flag(mode, LogMode.OPERATE_SERVER_OPTION_DEFAULT):
                backend = Backend.DEFAULT

            # Decide how to log message senders sync with the receiver
            dispatch_mode = (
                DispatchMode.ASYNC if has_flag(mode, LogMode.DISPATCH_ASYNC) else DispatchMode.SYNC
            )

            client_handler_settings = setup_server_handlers(
                logger=logger,
                ctx=ctx,
                ctx_manager=ctx_manager,
                backend=backend,
                message_dispatch_mode=dispatch_mode,
            )

            Log._FQDN_LOGGER_SETTINGS_EXTERNAL.update({name: client_handler_settings})
            return logger, client_handler_settings
        elif has_flag(mode, LogMode.OPERATE_CLIENT):
            setup_client_handlers(
                logger=logger, handler_name_to_client_handler_settings=mode_settings
            )
            return logger, {}
        elif has_flag(mode, LogMode.OPERATE_STANDALONE):
            return logger, {}

    @staticmethod
    def create_job_handler(capacity=sys.maxsize):
        """

        :param capacity:  (Default value = sys.maxsize)
        :returns: In-Memory Handler instance

        """
        handler = StringHandler(capacity=capacity)
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)
        return handler

    @staticmethod
    def get_available_job_logger(level=logging.DEBUG, capacity=sys.maxsize, console=False):
        """

        :param level:  (Default value = logging.DEBUG)
        :param capacity:  (Default value = sys.maxsize)
        :param console:  (Default value = False)
        :returns: Create or get a free Job logger instance

        """
        with Log._JOB_LOGGER_NAMES_LOCK:
            defaultHandlers = [Log._CONSOLE_HANDLER] if console else []

            handler = Log.create_job_handler(capacity=capacity)
            logger = logging.getLogger(name=str(uuid.uuid4()))
            logger.setLevel(level)

            for defaultHandler in [handler] + defaultHandlers:
                logger.addHandler(defaultHandler)
            return logger

    @staticmethod
    def free_job_logger(logger=None):
        """

        :param logger:  (Default value = None)
        :returns: Create or get a free Job logger instance

        """
        with Log._JOB_LOGGER_NAMES_LOCK:
            if logger is not None:
                # Note: This is a private controller, at least available on Python 3.7
                name = logger.name
                loggers = logging.Logger.manager.loggerDict
                if name in loggers:
                    del loggers[logger.name]
                if name in Log._LOGGER_NAMES_RETRIEVED:
                    del Log._LOGGER_NAMES_RETRIEVED[name]

    @staticmethod
    def loggers(
        mode: LogMode = LogMode.OPERATE_SERVER,
        mode_settings: Union[Dict, Loggers] = None,
        logger_names: List[str] = None,
    ) -> Loggers:
        """mode_settings: Settings vary per LoggerMode.

        LoggerMode.SERVER's settings are:
        {
            ctx: mp.get_context(...),
            ctx_manager: ctx.Manager()
        }

        LoggerMode.CLIENT's settings be: Loggers.setting()

        :param mode: LogMode:  (Default value = LogMode.OPERATE_SERVER)
        :param mode_settings: Union[Dict:
        :param Loggers]:  (Default value = None)
        :param logger_names: List[str]:  (Default value = None)

        """

        def get_logger_name(parts: List[str]):
            return ".".join(parts)

        def get_settings(parts: List[str], mode_settings: Union[Loggers, Dict]):
            if isinstance(mode_settings, Loggers):
                return mode_settings._get_settings(parts)
            return mode_settings

        def associate_logger(
            _loggers: Union[Loggers, logging.Logger],
            fqln_parts: List[str],
            part_index_start: int,
            part_index_end: int,
            mode_settings: Dict[str, str],
        ):
            fqln_current_parts = fqln_parts[0:part_index_end]

            if len(fqln_current_parts) <= 1:
                return

            fqln_current_name = get_logger_name(fqln_current_parts)
            current_parts = fqln_current_parts[1:part_index_end]

            mode_settings = get_settings(current_parts, mode_settings)
            logger, client_logger_settings = Log.get_hierarchical_logger(
                name=fqln_current_name, mode=mode, mode_settings=mode_settings
            )
            _loggers.setup_logger(
                parts=fqln_current_parts, logger=logger, settings=client_logger_settings
            )

        loggers = Loggers()

        # Logger instance already exists (due to setup). Retrieve them only,
        # albeit with modification
        logger_names = logger_names if logger_names is not None else Log._FQDN_LOGGER_NAMES_EXTERNAL
        for logger_name in sorted(
            logger_names
        ):  # Shorter logger name's first and then long ones (to initialize the parent loggers first)
            _loggers = loggers

            fqln_parts = logger_name.split(".")
            fqln_parts_count = len(fqln_parts)

            if fqln_parts_count <= 0:
                # No loggers to setup
                break

            # Eg: Uzzaz.test.innertest
            # Loggers to be setup will be: test and test.innertest
            for part_index_end in range(0, fqln_parts_count + 1):
                part_index_start = 0
                associate_logger(
                    _loggers, fqln_parts, part_index_start, part_index_end, mode_settings
                )

        return loggers

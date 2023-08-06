from typing import Dict

from constellate.virtualization.common.common import is_containerized
from constellate.debugger.debugger import debugger_setup as _debugger_setup


def debugger_setup(enabled: bool = False, kwargs_debugger_setup: Dict = None) -> None:
    if kwargs_debugger_setup is None:
        kwargs_debugger_setup = {"skip_on_missing_debug_server": True}

    if is_containerized():
        # Local machine: client app runs in Docker
        _debugger_setup(
            enabled=enabled, host="host.docker.internal", port=4444, **kwargs_debugger_setup
        )
    else:
        # Local machine: client app runs without docker
        _debugger_setup(enabled=enabled, host="localhost", port=4444, **kwargs_debugger_setup)

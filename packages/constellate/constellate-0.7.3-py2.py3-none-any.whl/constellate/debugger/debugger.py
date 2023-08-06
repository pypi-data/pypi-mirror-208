import sys
from typing import List


def debugger_setup(
    enabled: bool = False,
    host: str = "host.docker.internal",
    port: int = 4444,
    skip_on_missing_debug_server: bool = False,
):
    if enabled is True:
        try:
            sys.path.append("pydevd-pycharm.egg")
            import pydevd_pycharm
        except BaseException:
            print(
                "ERROR: PyCharm's remote debugging library not installed: "
                " - pydevd-pycharm~=XXX.XXXX.XX; sys.platform=='linux'"
            )
            raise

        try:
            pydevd_pycharm.settrace(
                host, port=port, stdoutToServer=True, stderrToServer=True, suspend=False
            )
        except BaseException as e:
            if not skip_on_missing_debug_server:
                raise e


def debugger_setup_stage(
    stage: str = None, enabled_stages: List[str] = [], skip_on_missing_debug_server: bool = False
):
    """Enable remote debugger if the current stage is one of the enabled stages

    :param stage: str:  (Default value = None)
    :param enabled_stages: List[str]:  (Default value = [])
    :param skip_on_missing_debug_server: bool:  (Default value = False)

    """
    enabled_stages = enabled_stages or []
    debugger_setup(
        enabled=stage in enabled_stages, skip_on_missing_debug_server=skip_on_missing_debug_server
    )

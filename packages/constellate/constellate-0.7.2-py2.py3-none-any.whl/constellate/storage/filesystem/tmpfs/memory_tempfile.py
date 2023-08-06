# Release:
# v0: https://github.com/mbello/memory-tempfile
# v1: Code cleanup + partial macos support

import os
import sys
import tempfile
import platform
from collections import OrderedDict
from typing import List, Union

_LINUX_MEM_BASED_FS = ["tmpfs", "ramfs"]
_LINUX_SUITABLE_PATHS = ["/tmp", "/run/user/{uid}", "/run/shm", "/dev/shm"]


class MemoryTempFS:
    def __init__(
        self,
        preferred_paths: List[str] = None,
        remove_paths: Union[bool, List[str]] = None,
        additional_paths: List[str] = None,
        filesystem_types: List = None,
        fallback: Union[bool, str] = True,
    ):
        system_type = platform.system()

        os_tempdir = tempfile.gettempdir()

        suitable_paths = []
        if system_type == "Linux":
            suitable_paths = [os_tempdir] + _LINUX_SUITABLE_PATHS
        elif system_type == "Darwin":
            # No support yet for ram backed directory. Assume os independent path is usable
            suitable_paths = [os_tempdir]
        else:
            # No support yet for ram backed directory. Assume os independent path is usable
            suitable_paths = [os_tempdir]

        preferred_paths = [] if preferred_paths is None else preferred_paths

        # Fallback path
        self.fallback = os_tempdir if isinstance(fallback, bool) else fallback

        # Prune suitable paths with removed paths
        if isinstance(remove_paths, bool) and remove_paths:
            suitable_paths = []
        elif isinstance(remove_paths, list) and len(remove_paths) > 0:
            suitable_paths = [i for i in suitable_paths if i not in remove_paths]

        # Expand suitable paths
        additional_paths = [] if additional_paths is None else additional_paths
        self.suitable_paths = preferred_paths + suitable_paths + additional_paths

        self.usable_paths = OrderedDict()

        if system_type == "Linux":
            self.filesystem_types = (
                list(filesystem_types) if filesystem_types is not None else _LINUX_MEM_BASED_FS
            )

            uid = os.geteuid()

            # mountinfo format: https://github.com/torvalds/linux/blob/master/Documentation/filesystems/proc.rst
            with open("/proc/self/mountinfo") as file:
                mount_info = {i[2]: i for i in [line.split() for line in file]}

            # Find path amongst suitable paths with a suitable filesystem type
            for path in self.suitable_paths:
                path = path.replace("{uid}", str(uid))

                # We may have repeated
                if self.usable_paths.get(path) is not None:
                    continue
                self.usable_paths[path] = False
                try:
                    dev = os.stat(path).st_dev
                    major, minor = os.major(dev), os.minor(dev)
                    mount_point = mount_info.get(f"{major}:{minor}")

                    if mount_point:
                        separator_index = mount_point.index("-")
                        if mount_point[separator_index + 1] in self.filesystem_types:
                            self.usable_paths[path] = mount_point
                except FileNotFoundError:
                    pass
        elif system_type == "Darwin":
            # No support yet for ram backed directory. Assume all paths are usable
            for p in self.suitable_paths:
                self.usable_paths[p] = [True]
        else:
            # No support yet for ram backed directory. Assume all paths are usable
            for p in self.suitable_paths:
                self.usable_paths[p] = [True]

        for key in [k for k, v in self.usable_paths.items() if not v]:
            del self.usable_paths[key]

        if len(self.usable_paths) > 0:
            self.tempdir = next(iter(self.usable_paths.keys()))
        else:
            if not fallback:
                raise RuntimeError("No memory temporary dir found and fallback is disabled.")
            self.tempdir = self.fallback

    def found_mem_tempdir(self):
        return len(self.usable_paths) > 0

    def using_mem_tempdir(self):
        return self.tempdir in self.usable_paths

    def get_usable_mem_tempdir_paths(self):
        return list(self.usable_paths.keys())

    def gettempdir(self):
        return self.tempdir

    def gettempdirb(self):
        return self.tempdir.encode(sys.getfilesystemencoding(), "surrogateescape")

    def mkdtemp(self, suffix=None, prefix=None, dir=None):
        return tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=self.tempdir if not dir else dir)

    def mkstemp(self, suffix=None, prefix=None, dir=None, text=False):
        return tempfile.mkstemp(
            suffix=suffix, prefix=prefix, dir=self.tempdir if not dir else dir, text=text
        )

    def TemporaryDirectory(self, suffix=None, prefix=None, dir=None):
        return tempfile.TemporaryDirectory(
            suffix=suffix, prefix=prefix, dir=self.tempdir if not dir else dir
        )

    def SpooledTemporaryFile(
        self,
        max_size=0,
        mode="w+b",
        buffering=-1,
        encoding=None,
        newline=None,
        suffix=None,
        prefix=None,
        dir=None,
    ):
        return tempfile.SpooledTemporaryFile(
            max_size=max_size,
            mode=mode,
            buffering=buffering,
            encoding=encoding,
            newline=newline,
            suffix=suffix,
            prefix=prefix,
            dir=self.tempdir if not dir else dir,
        )

    def NamedTemporaryFile(
        self,
        mode="w+b",
        buffering=-1,
        encoding=None,
        newline=None,
        suffix=None,
        prefix=None,
        dir=None,
        delete=True,
    ):
        return tempfile.NamedTemporaryFile(
            mode=mode,
            buffering=buffering,
            encoding=encoding,
            newline=newline,
            suffix=suffix,
            prefix=prefix,
            dir=self.tempdir if not dir else dir,
            delete=delete,
        )

    def TemporaryFile(
        self,
        mode="w+b",
        buffering=-1,
        encoding=None,
        newline=None,
        suffix=None,
        prefix=None,
        dir=None,
    ):
        return tempfile.TemporaryFile(
            mode=mode,
            buffering=buffering,
            encoding=encoding,
            newline=newline,
            suffix=suffix,
            prefix=prefix,
            dir=self.tempdir if not dir else dir,
        )

    def gettempprefix(self):
        return tempfile.gettempdir()

    def gettempprefixb(self):
        return tempfile.gettempprefixb()

import os
import tempfile
from contextlib import contextmanager
from pathlib import Path

from typing import Optional, List

from constellate.storage.filesystem.tmpfs.memory_tempfile import MemoryTempFS


def mkd_tmpfs(
    prefix: Optional[str] = None,
    suffix: Optional[str] = None,
    dir: str = None,
    env_tmpfs_dir: str = "TMPFS_DIR",
    env_tmpfs_dir_fs_types: Optional[List[str]] = ["ext4", "overlay", "tmpfs"],
) -> tempfile.TemporaryDirectory:
    """Create a temporary directory, preferably RAM backed, for speed

    (dir) and (env_tmpfs_dir + env_tmpfs_dir_fs_types) are MUTUALLY EXCLUSIVE

    :param prefix: Prefix
    :param suffix: Suffix
    :param dir: Directory must exist
    :param env_tmpfs_dir: TMPFS_DIR: Env var name indicating the absolute path to a memory backed tmpfs dir. Directory must exist
    :param env_tmpfs_dir_fs_types:  Filesystem type associated to env_tmpfs_dir.
                                    Note: "overlay" mainly used by k8s container with EmptyDir backed by Memory
    :returns: tempfile.TemporaryDirectory

    """
    tmpfs = None
    tmpfs_dir = None
    fs_types = None

    if env_tmpfs_dir in os.environ:
        tmpfs_dir = os.environ[env_tmpfs_dir]
        fs_types = env_tmpfs_dir_fs_types

        preferred_paths = [tmpfs_dir] if tmpfs_dir is not None else []
        try:
            tmpfs = MemoryTempFS(
                preferred_paths=preferred_paths, filesystem_types=fs_types, fallback=False
            )
        except RuntimeError:
            # Ignore "No memory temporary dir found and fallback disabled case
            pass

    if tmpfs is None or not tmpfs.using_mem_tempdir():
        tmpfs = MemoryTempFS(fallback=True)

    return tmpfs.TemporaryDirectory(prefix=prefix, suffix=suffix, dir=dir)


def mkd_tmp(
    prefix: Optional[str] = None, suffix: Optional[str] = None, dir: Optional[str] = None
) -> tempfile.TemporaryDirectory:
    return tempfile.TemporaryDirectory(prefix=prefix, suffix=suffix, dir=dir)


@contextmanager
def mkf_tmpfs(
    prefix: Optional[str] = None, suffix: Optional[str] = None, dir: Optional[str] = None
) -> Path:
    """Create a temporary file, preferably RAM backed, for speed

    :param prefix: Optional[str]:  (Default value = None)
    :param suffix: Optional[str]:  (Default value = None)
    :param dir: Optional[str]:  (Default value = None)

    """
    with mkd_tmpfs(dir=dir) as tmp_dir:
        file_name = None
        with tempfile.NamedTemporaryFile(
            prefix=prefix, suffix=suffix, dir=tmp_dir, delete=False
        ) as f:
            file_name = f.name
        yield Path(file_name)

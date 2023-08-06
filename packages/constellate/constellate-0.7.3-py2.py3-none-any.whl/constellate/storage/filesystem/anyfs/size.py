from pathlib import Path

from constellate.storage.filesystem.anyfs.path import get_purepath


def file_size(path):
    """Get file size in bytes

    :param path:

    """
    file = get_purepath(path)
    return -1 if file is None else Path(file).stat().st_size

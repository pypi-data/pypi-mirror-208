from contextlib import contextmanager
from io import BytesIO
from pathlib import Path
from typing import List, Tuple
from zipfile import ZipFile, ZipInfo, ZIP_STORED

import attr


@attr.s(kw_only=True, auto_attribs=True)
class RAMZipConfig:
    # In memory ZIP file
    buffer: BytesIO = None
    # Zip file creation params
    mode: str = None
    compression: int = None
    allowZip64: bool = True


@contextmanager
def _zip_file_from_ram_zip_config(config: RAMZipConfig = None) -> ZipFile:
    yield ZipFile(config.buffer, config.mode, config.compression, config.allowZip64)


def create_ram_zip(compression: int = ZIP_STORED, allowZip64: bool = True) -> RAMZipConfig:
    buffer = BytesIO()
    mode = "a"

    config = RAMZipConfig(buffer=buffer, mode=mode, compression=compression, allowZip64=allowZip64)

    with _zip_file_from_ram_zip_config(config=config) as zip_file:
        #  file is created with mode 'w', 'x' or 'a' and then closed without adding any files to the archive,
        #  the appropriate ZIP structures for an empty archive will be written to the file.
        # src: https://docs.python.org/3/library/zipfile.html#zipfile.ZipFile
        return config


@attr.s(kw_only=True, auto_attribs=True)
class ZipFileInfo:
    root: Path = None
    arc_name: Path = None
    # Mode 1: Load data from zipinfo
    data_zip_info: ZipInfo = None
    # Mode 2: Load data from
    data_binary: BytesIO = None


def append_ram_zip(config: RAMZipConfig = None, files: List[ZipFileInfo] = None) -> RAMZipConfig:
    with _zip_file_from_ram_zip_config(config=config) as zip_file:
        for file_info in files or []:
            if isinstance(file_info.data_zip_info, ZipInfo):
                root_file_path = file_info.root.resolve() if file_info.root else None
                src_file_path = Path(f"/{file_info.data_zip_info.filename}").resolve()
                archive_file_name = (
                    src_file_path.relative_to(root_file_path)
                    if None not in [root_file_path, src_file_path]
                    else src_file_path
                )
                zip_file.write(src_file_path, archive_file_name)
            elif isinstance(file_info.data_binary, Tuple):
                zip_file.writestr(file_info.arc_name, file_info.data_binary.getvalue())
            else:
                raise NotImplementedError()
        assert zip_file.testzip() is None

    return config


def save_ram_zip(file_path: Path = None, config: RAMZipConfig = None):
    with open(file_path, "wb") as f:
        f.write(config.buffer.getvalue())

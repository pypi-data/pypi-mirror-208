from pathlib import PurePath, Path
from typing import Union


def _get_path(file_path: Union[str, Path]) -> Path:
    return Path(file_path) if isinstance(file_path, str) else file_path


def get_immediate_parent_folder_if_file(file_path: Union[str, Path]) -> Path:
    file_path2 = _get_path(file_path)
    return file_path2 if file_path2.is_dir() else file_path2.parent


def get_basename_without_extension(file_path: Union[str, Path]) -> str:
    file_path2 = _get_path(file_path)
    extension = file_path2.suffix
    extension_lenght = +len(file_path2.name) if len(extension) == 0 else -len(extension)
    base_name = file_path2.name[:extension_lenght]
    return base_name


def get_path_without_extension(file_path: Union[str, Path]) -> str:
    """Get path without the extension

    :param file_path: File Path
    :returns: File path without the new extension
            Eg: /path/to/file.txt -> /path/to/file

    """
    file_path2 = _get_path(file_path)
    parent = file_path2.parent
    base_name = get_basename_without_extension(file_path)
    return str(Path(parent, base_name))


def get_path_with_extension(file_path: Union[str, Path], new_extension: str) -> Path:
    """Get path with the new extension instead

    :param file_path: File Path
    :param new_extension: Extension to use in the file path
    :returns: File path with the new extension

    """
    file_path2 = _get_path(file_path)
    path = get_path_without_extension(file_path2)
    return Path(f"{path}.{new_extension}")


def get_path_with_parent_and_extension(file_path, new_parent, new_extension) -> Path:
    """Get path with the new extension instead

    :param file_path: File Path
    :param new_parent: Parent path to use in the file path
    :param new_extension: Extension to use in the file path
    :returns: File path with the new parent/extension

    """
    basename = get_basename_without_extension(file_path)
    return Path(new_parent, f"{basename}.{new_extension}")


def get_purepath(file_path) -> PurePath:
    return PurePath(file_path)


def get_file_extension(file_path: Union[str, Path]) -> str:
    """Get file extension, **dotless**"""
    file_path2 = _get_path(file_path)
    return file_path2.suffix[1:].casefold().lower()


def is_hidden_file(file_path: Union[str, Path]) -> str:
    basename = get_basename_without_extension(file_path)
    return basename.startswith(".")


def escape_occurences(source, escape_string) -> str:
    """Escape all characters with the escape string.

    :param source: String to escape
    :param escape_string: String to escape the first string with
    :returns: Escaped string

    """
    assert isinstance(source, str), "source must be a str"

    escaped_string = list()
    for c in source:
        escaped_string.append(escape_string)
        escaped_string.append(c)

    return "".join(escaped_string)


def escape_path(file_path) -> str:
    """Escape all characters with the escape string.

    :param file_path: String to escape
    :returns: Escaped string

    """
    return escape_occurences(file_path, "\\")


def same_path(
    file_path1: Union[str, Path],
    file_path2: Union[str, Path],
    file_path1_strict: bool = False,
    file_path2_strict: bool = False,
    case_insensitive: bool = False,
) -> bool:
    """Case sensitive path check
    Assume linux fs path (ie case sensitive paths)

    :param path1:
    :param path2:

    """
    path1 = _get_path(file_path1).resolve(strict=file_path1_strict)
    path2 = _get_path(file_path2).resolve(strict=file_path2_strict)

    path1_str = None
    path2_str = None

    if case_insensitive:
        path1_str = str(path1).lower()
        path2_str = str(path2).lower()
    else:
        path1_str = str(path1)
        path2_str = str(path2)

    return path1_str == path2_str

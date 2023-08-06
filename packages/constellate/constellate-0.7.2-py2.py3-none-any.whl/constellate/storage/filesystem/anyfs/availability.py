from pathlib import Path


def is_file_available(path) -> bool:
    return Path(path).is_file() if path is not None else False

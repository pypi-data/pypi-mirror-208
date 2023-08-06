from contextlib import contextmanager
from pathlib import Path


@contextmanager
def readiness(file_path: str = "/tmp/app.ready"):
    yield from _file_probe(file_path=file_path)


@contextmanager
def liveness(file_path="/tmp/app.live"):
    yield from _file_probe(file_path=file_path)


def _file_probe(file_path="/tmp/foobar"):
    p = Path(file_path)
    try:
        p.touch()
        yield None
    finally:
        p.unlink(missing_ok=True)

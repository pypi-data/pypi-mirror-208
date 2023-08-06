import pkgutil


def package_available(name: str = None) -> bool:
    try:
        return pkgutil.find_loader(name) is not None
    except ImportError:
        return False

def version_int(version: str = "0.0.0") -> int:
    # Integer version
    parts = [int(x, 10) for x in version.split(".")]
    parts.reverse()
    return sum(x * (1000**i) for i, x in enumerate(parts))

from typing import Optional


def with_prefix(prefix: Optional[str], value: str) -> str:
    """Add prefix to string.

    If prefix is not empty, this function will add a
    prefix to a string, delimited by a white space.
    """
    prefix = prefix.strip() if prefix else ""
    if prefix:
        return f"{prefix} {value}"
    else:
        return value

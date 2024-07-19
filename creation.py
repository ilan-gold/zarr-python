import warnings

from zarrs_python.api.synchronous import (
    array,
    create,
    empty,
    empty_like,
    full,
    full_like,
    ones,
    ones_like,
    open_array,
    open_like,
    zeros,
    zeros_like,
)

warnings.warn(
    "zarrs_python.creation is deprecated, use zarrs_python.api.synchronous",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "create",
    "empty",
    "zeros",
    "ones",
    "full",
    "array",
    "open_array",
    "empty_like",
    "zeros_like",
    "ones_like",
    "full_like",
    "open_like",
]

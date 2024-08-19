import warnings

from zarrs_python.api.synchronous import (
    consolidate_metadata,
    copy,
    copy_all,
    copy_store,
    load,
    open,
    open_consolidated,
    save,
    save_array,
    save_group,
    tree,
)

__all__ = [
    "open",
    "save",
    "load",
    "save_array",
    "save_group",
    "copy",
    "copy_all",
    "copy_store",
    "tree",
    "consolidate_metadata",
    "open_consolidated",
]

warnings.warn(
    "zarrs_python.convenience is deprecated, use zarrs_python.api.synchronous",
    DeprecationWarning,
    stacklevel=2,
)

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

warnings.warn(
    "zarrs_python.convenience is deprecated, use zarrs_python.api.synchronous",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "open",
    "save_array",
    "save_group",
    "save",
    "load",
    "tree",
    "copy_store",
    "copy",
    "copy_all",
    "consolidate_metadata",
    "open_consolidated",
]

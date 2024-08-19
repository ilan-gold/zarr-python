from collections.abc import Iterator

import numpy as np
import pytest

from zarrs_python import Array
from zarrs_python.abc.store import Store
from zarrs_python.store import MemoryStore, StorePath


@pytest.fixture
async def store() -> Iterator[Store]:
    yield StorePath(await MemoryStore.open(mode="w"))


def test_simple(store: Store):
    data = np.arange(0, 256, dtype="uint16").reshape((16, 16))

    a = Array.create(
        store / "simple_v2",
        zarr_format=2,
        shape=data.shape,
        chunks=(16, 16),
        dtype=data.dtype,
        fill_value=0,
    )

    a[:, :] = data
    assert np.array_equal(data, a[:, :])

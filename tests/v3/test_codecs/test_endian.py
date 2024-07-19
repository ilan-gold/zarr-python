from typing import Literal

import numpy as np
import pytest

import zarrs_python.v2
from zarrs_python.abc.store import Store
from zarrs_python.array import AsyncArray
from zarrs_python.buffer import default_buffer_prototype
from zarrs_python.codecs import BytesCodec
from zarrs_python.store.core import StorePath
from zarrs_python.testing.utils import assert_bytes_equal

from .test_codecs import _AsyncArrayProxy


@pytest.mark.parametrize("store", ("local", "memory"), indirect=["store"])
@pytest.mark.parametrize("endian", ["big", "little"])
async def test_endian(store: Store, endian: Literal["big", "little"]) -> None:
    data = np.arange(0, 256, dtype="uint16").reshape((16, 16))
    path = "endian"
    spath = StorePath(store, path)
    a = await AsyncArray.create(
        spath,
        shape=data.shape,
        chunk_shape=(16, 16),
        dtype=data.dtype,
        fill_value=0,
        chunk_key_encoding=("v2", "."),
        codecs=[BytesCodec(endian=endian)],
    )

    await _AsyncArrayProxy(a)[:, :].set(data)
    readback_data = await _AsyncArrayProxy(a)[:, :].get()
    assert np.array_equal(data, readback_data)

    # Compare with v2
    z = zarrs_python.v2.create(
        shape=data.shape,
        chunks=(16, 16),
        dtype=">u2" if endian == "big" else "<u2",
        compressor=None,
        fill_value=1,
    )
    z[:, :] = data
    assert_bytes_equal(
        await store.get(f"{path}/0.0", prototype=default_buffer_prototype), z._store["0.0"]
    )


@pytest.mark.parametrize("store", ("local", "memory"), indirect=["store"])
@pytest.mark.parametrize("dtype_input_endian", [">u2", "<u2"])
@pytest.mark.parametrize("dtype_store_endian", ["big", "little"])
async def test_endian_write(
    store: Store,
    dtype_input_endian: Literal[">u2", "<u2"],
    dtype_store_endian: Literal["big", "little"],
) -> None:
    data = np.arange(0, 256, dtype=dtype_input_endian).reshape((16, 16))
    path = "endian"
    spath = StorePath(store, path)
    a = await AsyncArray.create(
        spath,
        shape=data.shape,
        chunk_shape=(16, 16),
        dtype="uint16",
        fill_value=0,
        chunk_key_encoding=("v2", "."),
        codecs=[BytesCodec(endian=dtype_store_endian)],
    )

    await _AsyncArrayProxy(a)[:, :].set(data)
    readback_data = await _AsyncArrayProxy(a)[:, :].get()
    assert np.array_equal(data, readback_data)

    # Compare with zarr-python
    z = zarrs_python.v2.create(
        shape=data.shape,
        chunks=(16, 16),
        dtype=">u2" if dtype_store_endian == "big" else "<u2",
        compressor=None,
        fill_value=1,
    )
    z[:, :] = data
    assert_bytes_equal(
        await store.get(f"{path}/0.0", prototype=default_buffer_prototype), z._store["0.0"]
    )

import numpy as np
import pytest

from zarrs_python.abc.store import Store
from zarrs_python.array import Array
from zarrs_python.codecs import BytesCodec, GzipCodec
from zarrs_python.store.core import StorePath


@pytest.mark.parametrize("store", ("local", "memory"), indirect=["store"])
def test_gzip(store: Store) -> None:
    data = np.arange(0, 256, dtype="uint16").reshape((16, 16))

    a = Array.create(
        StorePath(store),
        shape=data.shape,
        chunk_shape=(16, 16),
        dtype=data.dtype,
        fill_value=0,
        codecs=[BytesCodec(), GzipCodec()],
    )

    a[:, :] = data
    assert np.array_equal(data, a[:, :])

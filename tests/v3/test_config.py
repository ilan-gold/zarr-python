import os
from collections.abc import Iterable
from typing import Any
from unittest import mock
from unittest.mock import Mock

import numpy as np
import pytest

import zarrs_python
from zarrs_python import Array, zeros
from zarrs_python.abc.codec import CodecInput, CodecOutput, CodecPipeline
from zarrs_python.abc.store import ByteSetter
from zarrs_python.codecs import BatchedCodecPipeline, BloscCodec, BytesCodec, Crc32cCodec, ShardingCodec
from zarrs_python.core.array_spec import ArraySpec
from zarrs_python.core.buffer import NDBuffer
from zarrs_python.core.config import BadConfigError, config
from zarrs_python.core.indexing import SelectorTuple
from zarrs_python.registry import (
    fully_qualified_name,
    get_buffer_class,
    get_codec_class,
    get_ndbuffer_class,
    get_pipeline_class,
    register_buffer,
    register_codec,
    register_ndbuffer,
    register_pipeline,
)
from zarrs_python.testing.buffer import (
    NDBufferUsingTestNDArrayLike,
    StoreExpectingTestBuffer,
    TestBuffer,
    TestNDArrayLike,
)


def test_config_defaults_set() -> None:
    # regression test for available defaults
    assert config.defaults == [
        {
            "array": {"order": "C"},
            "async": {"concurrency": None, "timeout": None},
            "json_indent": 2,
            "codec_pipeline": {
                "path": "zarrs_python.codecs.pipeline.BatchedCodecPipeline",
                "batch_size": 1,
            },
            "buffer": "zarrs_python.core.buffer.Buffer",
            "ndbuffer": "zarrs_python.core.buffer.NDBuffer",
            "codecs": {
                "blosc": "zarrs_python.codecs.blosc.BloscCodec",
                "gzip": "zarrs_python.codecs.gzip.GzipCodec",
                "zstd": "zarrs_python.codecs.zstd.ZstdCodec",
                "bytes": "zarrs_python.codecs.bytes.BytesCodec",
                "endian": "zarrs_python.codecs.bytes.BytesCodec",
                "crc32c": "zarrs_python.codecs.crc32c_.Crc32cCodec",
                "sharding_indexed": "zarrs_python.codecs.sharding.ShardingCodec",
                "transpose": "zarrs_python.codecs.transpose.TransposeCodec",
            },
        }
    ]
    assert config.get("array.order") == "C"
    assert config.get("async.concurrency") is None
    assert config.get("async.timeout") is None
    assert config.get("codec_pipeline.batch_size") == 1
    assert config.get("json_indent") == 2


@pytest.mark.parametrize(
    "key, old_val, new_val",
    [("array.order", "C", "F"), ("async.concurrency", None, 10), ("json_indent", 2, 0)],
)
def test_config_defaults_can_be_overridden(key: str, old_val: Any, new_val: Any) -> None:
    assert config.get(key) == old_val
    with config.set({key: new_val}):
        assert config.get(key) == new_val


def test_fully_qualified_name():
    class MockClass:
        pass

    assert "v3.test_config.test_fully_qualified_name.<locals>.MockClass" == fully_qualified_name(
        MockClass
    )


@pytest.mark.parametrize("store", ("local", "memory"), indirect=["store"])
def test_config_codec_pipeline_class(store):
    # has default value
    assert get_pipeline_class().__name__ != ""

    config.set({"codec_pipeline.name": "zarrs_python.codecs.pipeline.BatchedCodecPipeline"})
    assert get_pipeline_class() == zarrs_python.codecs.pipeline.BatchedCodecPipeline

    _mock = Mock()

    class MockCodecPipeline(BatchedCodecPipeline):
        async def write(
            self,
            batch_info: Iterable[tuple[ByteSetter, ArraySpec, SelectorTuple, SelectorTuple]],
            value: NDBuffer,
            drop_axes: tuple[int, ...] = (),
        ) -> None:
            _mock.call()

    register_pipeline(MockCodecPipeline)
    config.set({"codec_pipeline.path": fully_qualified_name(MockCodecPipeline)})

    assert get_pipeline_class() == MockCodecPipeline

    # test if codec is used
    arr = Array.create(
        store=store,
        shape=(100,),
        chunks=(10,),
        zarr_format=3,
        dtype="i4",
    )
    arr[:] = range(100)

    _mock.call.assert_called()

    with pytest.raises(BadConfigError):
        config.set({"codec_pipeline.path": "wrong_name"})
        get_pipeline_class()

    class MockEnvCodecPipeline(CodecPipeline):
        pass

    register_pipeline(MockEnvCodecPipeline)

    with mock.patch.dict(
        os.environ, {"ZARR_CODEC_PIPELINE__PATH": fully_qualified_name(MockEnvCodecPipeline)}
    ):
        assert get_pipeline_class(reload_config=True) == MockEnvCodecPipeline


@pytest.mark.parametrize("store", ("local", "memory"), indirect=["store"])
def test_config_codec_implementation(store):
    # has default value
    assert fully_qualified_name(get_codec_class("blosc")) == config.defaults[0]["codecs"]["blosc"]

    _mock = Mock()

    class MockBloscCodec(BloscCodec):
        async def _encode_single(
            self, chunk_data: CodecInput, chunk_spec: ArraySpec
        ) -> CodecOutput | None:
            _mock.call()

    config.set({"codecs.blosc": fully_qualified_name(MockBloscCodec)})
    register_codec("blosc", MockBloscCodec)
    assert get_codec_class("blosc") == MockBloscCodec

    # test if codec is used
    arr = Array.create(
        store=store,
        shape=(100,),
        chunks=(10,),
        zarr_format=3,
        dtype="i4",
        codecs=[BytesCodec(), {"name": "blosc", "configuration": {}}],
    )
    arr[:] = range(100)
    _mock.call.assert_called()

    with mock.patch.dict(os.environ, {"ZARR_CODECS__BLOSC": fully_qualified_name(BloscCodec)}):
        assert get_codec_class("blosc", reload_config=True) == BloscCodec


@pytest.mark.parametrize("store", (pytest.param("local", marks=pytest.mark.skip(reason="No nd buffer usage yet for rust array")), "memory"), indirect=["store"])
def test_config_ndbuffer_implementation(store):
    # has default value
    assert fully_qualified_name(get_ndbuffer_class()) == config.defaults[0]["ndbuffer"]

    # set custom ndbuffer with TestNDArrayLike implementation
    register_ndbuffer(NDBufferUsingTestNDArrayLike)
    config.set({"ndbuffer": fully_qualified_name(NDBufferUsingTestNDArrayLike)})
    assert get_ndbuffer_class() == NDBufferUsingTestNDArrayLike
    arr = Array.create(
        store=store,
        shape=(100,),
        chunks=(10,),
        zarr_format=3,
        dtype="i4",
    )
    got = arr[:]
    print(type(got))
    assert isinstance(got, TestNDArrayLike)


def test_config_buffer_implementation():
    # has default value
    assert fully_qualified_name(get_buffer_class()) == config.defaults[0]["buffer"]

    arr = zeros(shape=(100), store=StoreExpectingTestBuffer(mode="w"))

    # AssertionError of StoreExpectingTestBuffer when not using my buffer
    with pytest.raises(AssertionError):
        arr[:] = np.arange(100)

    register_buffer(TestBuffer)
    config.set({"buffer": fully_qualified_name(TestBuffer)})
    assert get_buffer_class() == TestBuffer

    # no error using TestBuffer
    data = np.arange(100)
    arr[:] = np.arange(100)
    assert np.array_equal(arr[:], data)

    data2d = np.arange(1000).reshape(100, 10)
    arr_sharding = zeros(
        shape=(100, 10),
        store=StoreExpectingTestBuffer(mode="w"),
        codecs=[ShardingCodec(chunk_shape=(10, 10))],
    )
    arr_sharding[:] = data2d
    assert np.array_equal(arr_sharding[:], data2d)

    arr_Crc32c = zeros(
        shape=(100, 10),
        store=StoreExpectingTestBuffer(mode="w"),
        codecs=[BytesCodec(), Crc32cCodec()],
    )
    arr_Crc32c[:] = data2d
    assert np.array_equal(arr_Crc32c[:], data2d)

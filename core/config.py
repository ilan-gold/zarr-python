from __future__ import annotations

from typing import Any, Literal, cast

from donfig import Config as DConfig


class BadConfigError(ValueError):
    _msg = "bad Config: %r"


class Config(DConfig):  # type: ignore[misc]
    """Will collect configuration from config files and environment variables

    Example environment variables:
    Grabs environment variables of the form "ZARR_FOO__BAR_BAZ=123" and
    turns these into config variables of the form ``{"foo": {"bar-baz": 123}}``
    It transforms the key and value in the following way:

    -  Lower-cases the key text
    -  Treats ``__`` (double-underscore) as nested access
    -  Calls ``ast.literal_eval`` on the value

    """

    def reset(self) -> None:
        self.clear()
        self.refresh()


"""
The config module is responsible for managing the configuration of zarr and  is based on the Donfig python library.
For selecting custom implementations of codecs, pipelines, buffers and ndbuffers, first register the implementations 
in the registry and then select them in the config.
e.g. an implementation of the bytes codec in a class "NewBytesCodec", requires the value of codecs.bytes.name to be 
"NewBytesCodec".
Donfig can be configured programmatically, by environment variables, or from YAML files in standard locations
e.g. export ZARR_CODECS__BYTES__NAME="NewBytesCodec"
(for more information see github.com/pytroll/donfig)
Default values below point to the standard implementations of zarr-python
"""
config = Config(
    "zarr",
    defaults=[
        {
            "array": {"order": "C"},
            "async": {"concurrency": None, "timeout": None},
            "json_indent": 2,
            "codec_pipeline": {
                "path": "zarrs_python.codecs.pipeline.BatchedCodecPipeline",
                "batch_size": 1,
            },
            "codecs": {
                "blosc": "zarrs_python.codecs.blosc.BloscCodec",
                "gzip": "zarrs_python.codecs.gzip.GzipCodec",
                "zstd": "zarrs_python.codecs.zstd.ZstdCodec",
                "bytes": "zarrs_python.codecs.bytes.BytesCodec",
                "endian": "zarrs_python.codecs.bytes.BytesCodec",  # compatibility with earlier versions of ZEP1
                "crc32c": "zarrs_python.codecs.crc32c_.Crc32cCodec",
                "sharding_indexed": "zarrs_python.codecs.sharding.ShardingCodec",
                "transpose": "zarrs_python.codecs.transpose.TransposeCodec",
            },
            "buffer": "zarrs_python.core.buffer.Buffer",
            "ndbuffer": "zarrs_python.core.buffer.NDBuffer",
        }
    ],
)


def parse_indexing_order(data: Any) -> Literal["C", "F"]:
    if data in ("C", "F"):
        return cast(Literal["C", "F"], data)
    msg = f"Expected one of ('C', 'F'), got {data} instead."
    raise ValueError(msg)
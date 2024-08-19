from collections.abc import Iterable

from numpy import ndarray

from zarrs_python.abc.codec import ArrayBytesCodec, CodecInput, CodecPipeline
from zarrs_python.codecs import BytesCodec
from zarrs_python.core.array_spec import ArraySpec
from zarrs_python.core.buffer import Buffer, NDBuffer
from zarrs_python.core.common import BytesLike


class TestEntrypointCodec(ArrayBytesCodec):
    is_fixed_size = True

    async def encode(
        self,
        chunks_and_specs: Iterable[tuple[CodecInput | None, ArraySpec]],
    ) -> BytesLike | None:
        pass

    async def decode(
        self,
        chunks_and_specs: Iterable[tuple[CodecInput | None, ArraySpec]],
    ) -> ndarray:
        pass

    def compute_encoded_size(self, input_byte_length: int, chunk_spec: ArraySpec) -> int:
        return input_byte_length


class TestEntrypointCodecPipeline(CodecPipeline):
    def __init__(self, batch_size: int = 1):
        pass

    async def encode(
        self, chunks_and_specs: Iterable[tuple[CodecInput | None, ArraySpec]]
    ) -> BytesLike:
        pass

    async def decode(
        self, chunks_and_specs: Iterable[tuple[CodecInput | None, ArraySpec]]
    ) -> ndarray:
        pass


class TestEntrypointBuffer(Buffer):
    pass


class TestEntrypointNDBuffer(NDBuffer):
    pass


class TestEntrypointGroup:
    class Codec(BytesCodec):
        pass

    class Buffer(Buffer):
        pass

    class NDBuffer(NDBuffer):
        pass

    class Pipeline(CodecPipeline):
        pass

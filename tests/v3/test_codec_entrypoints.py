import os.path
import sys

import pytest

import zarrs_python.codecs.registry

here = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture()
def set_path():
    sys.path.append(here)
    zarrs_python.codecs.registry._collect_entrypoints()
    yield
    sys.path.remove(here)
    entry_points = zarrs_python.codecs.registry._collect_entrypoints()
    entry_points.pop("test")


@pytest.mark.usefixtures("set_path")
def test_entrypoint_codec():
    cls = zarrs_python.codecs.registry.get_codec_class("test")
    assert cls.__name__ == "TestCodec"

import gzip
import os
import os.path

import pytest
from Bio.bgzf import BgzfWriter
from constants import CANONICAL_TRANSCRIPT, CONTIG_ALIAS

from pyvariant.constants import CACHE_DIR_ENV, CACHE_DIR_NAME
from pyvariant.files import bgzip, get_cache_dir, is_bgzipped, tsv_to_dict, txt_to_list


@pytest.fixture
def bgzip_file(tmpdir) -> str:
    path = tmpdir / "test.txt.gz"
    with BgzfWriter(path.strpath, compresslevel=9) as fh:
        fh.write(b"test")

    return path.strpath


@pytest.fixture
def cache_env_var():
    old_end_var = os.environ.get(CACHE_DIR_ENV, "")
    os.environ[CACHE_DIR_ENV] = "TEST"
    yield
    if old_end_var:
        os.environ[CACHE_DIR_ENV] = old_end_var
    else:
        del os.environ[CACHE_DIR_ENV]


@pytest.fixture
def gzip_file(tmpdir) -> str:
    path = tmpdir / "test.txt.gz"
    with gzip.open(path.strpath, "wb") as fh:
        fh.write(b"test")

    return path.strpath


@pytest.fixture
def uncompressed_file(tmpdir) -> str:
    path = tmpdir / "test.txt"
    with open(path.strpath, "w") as fh:
        fh.write("test")

    return path.strpath


def test_bgzip_gzip(gzip_file):
    bgzip(gzip_file)
    assert os.path.exists(gzip_file)


def test_bgzip_uncompressed(uncompressed_file):
    compressed_file = uncompressed_file + ".gz"
    bgzip(uncompressed_file)
    assert os.path.exists(compressed_file)


def test_is_bgzipped_false(gzip_file):
    assert is_bgzipped(gzip_file) is False


def test_is_bgzipped_true(bgzip_file):
    assert is_bgzipped(bgzip_file) is True


def test_get_cache_dir():
    assert get_cache_dir().rstrip("/").endswith(CACHE_DIR_NAME)


def test_get_cache_dir_env_var(cache_env_var):
    assert get_cache_dir() == "TEST"


def test_tsv_to_dict():
    result = tsv_to_dict(CONTIG_ALIAS)
    assert result == {"chr4": ["4"]}


def test_txt_to_list():
    result = txt_to_list(CANONICAL_TRANSCRIPT)
    assert result == ["ENST00000000233"]

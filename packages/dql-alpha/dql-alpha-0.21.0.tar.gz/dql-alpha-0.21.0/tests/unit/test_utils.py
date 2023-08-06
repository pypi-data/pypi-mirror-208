import io

import pytest

from dql.utils import (
    FileSlice,
    dql_paths_join,
    sizeof_fmt,
    sql_escape_like,
    suffix_to_number,
)

DQL_TEST_PATHS = ["/file1", "file2", "/dir/file3", "dir/file4"]
DQL_EX_ROOT = ["/file1", "/file2", "/dir/file3", "/dir/file4"]
DQL_EX_SUBDIR = [
    "subdir/file1",
    "subdir/file2",
    "subdir/dir/file3",
    "subdir/dir/file4",
]
DQL_EX_DOUBLE_SUBDIR = [
    "subdir/double/file1",
    "subdir/double/file2",
    "subdir/double/dir/file3",
    "subdir/double/dir/file4",
]


@pytest.mark.parametrize(
    "src,paths,expected",
    (
        ("", DQL_TEST_PATHS, DQL_EX_ROOT),
        ("/", DQL_TEST_PATHS, DQL_EX_ROOT),
        ("/*", DQL_TEST_PATHS, DQL_EX_ROOT),
        ("/file*", DQL_TEST_PATHS, DQL_EX_ROOT),
        ("subdir", DQL_TEST_PATHS, DQL_EX_SUBDIR),
        ("subdir/", DQL_TEST_PATHS, DQL_EX_SUBDIR),
        ("subdir/*", DQL_TEST_PATHS, DQL_EX_SUBDIR),
        ("subdir/file*", DQL_TEST_PATHS, DQL_EX_SUBDIR),
        ("subdir/double", DQL_TEST_PATHS, DQL_EX_DOUBLE_SUBDIR),
        ("subdir/double/", DQL_TEST_PATHS, DQL_EX_DOUBLE_SUBDIR),
        ("subdir/double/*", DQL_TEST_PATHS, DQL_EX_DOUBLE_SUBDIR),
        ("subdir/double/file*", DQL_TEST_PATHS, DQL_EX_DOUBLE_SUBDIR),
    ),
)
def test_dql_paths_join(src, paths, expected):
    assert list(dql_paths_join(src, paths)) == expected


@pytest.mark.parametrize(
    "num,suffix,si,expected",
    (
        (1, "", False, "   1"),
        (536, "", False, " 536"),
        (1000, "", False, "1000"),
        (1000, "", True, "1.0K"),
        (1000, " tests", False, "1000 tests"),
        (1000, " tests", True, "1.0K tests"),
        (100000, "", False, "97.7K"),
        (100000, "", True, "100.0K"),
        (1000000, "", True, "1.0M"),
        (1000000000, "", True, "1.0G"),
        (1000000000000, "", True, "1.0T"),
        (1000000000000000, "", True, "1.0P"),
        (1000000000000000000, "", True, "1.0E"),
        (1000000000000000000000, "", True, "1.0Z"),
        (1000000000000000000000000, "", True, "1.0Y"),
        (1000000000000000000000000000, "", True, "1.0R"),
        (1000000000000000000000000000000, "", True, "1.0Q"),
    ),
)
def test_sizeof_fmt(num, suffix, si, expected):
    assert sizeof_fmt(num, suffix, si) == expected


@pytest.mark.parametrize(
    "text,expected",
    (
        ("1", 1),
        ("50", 50),
        ("1K", 1024),
        ("1k", 1024),
        ("2M", 1024 * 1024 * 2),
    ),
)
def test_suffix_to_number(text, expected):
    assert suffix_to_number(text) == expected


@pytest.mark.parametrize(
    "text",
    (
        "",
        "Bogus",
        "50H",
    ),
)
def test_suffix_to_number_invalid(text):
    with pytest.raises(ValueError):
        suffix_to_number(text)


@pytest.mark.parametrize(
    "text,expected",
    (
        ("test like", "test like"),
        ("Can%t \\escape_this", "Can\\%t \\\\escape\\_this"),
    ),
)
def test_sql_escape_like(text, expected):
    assert sql_escape_like(text) == expected


def test_FileSlice():
    data = b"0123456789abcdef"
    base = io.BytesIO(data)
    f = FileSlice(base, 5, 5, "foo")
    assert base.tell() == 0
    assert f.readable()
    assert not f.writable()
    assert f.seekable()
    assert f.name == "foo"

    # f.seek() doesn't move the underlying stream
    f.seek(0)
    assert f.tell() == 0
    assert base.tell() == 0

    assert f.read(3) == data[5:8]
    assert f.tell() == 3
    assert base.tell() == 8

    assert f.read(4) == data[8:10]
    assert f.tell() == 5
    assert base.tell() == 10

    b = bytearray(5)
    f.seek(0)
    f.readinto(b)
    assert b == data[5:10]


def test_bad_FileSlice():
    data = b"0123456789abcdef"
    base = io.BytesIO(data)
    f = FileSlice(base, 10, 10, "foo")
    assert f.read(4) == data[10:14]
    with pytest.raises(RuntimeError):
        f.read()

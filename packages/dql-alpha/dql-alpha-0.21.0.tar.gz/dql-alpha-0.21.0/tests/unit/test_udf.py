from sqlalchemy import Integer

from dql.dataset import DatasetRow
from dql.query import C, generator, udf


def test_udf():
    @udf(Integer, C.id, C.size)
    def t(a, b):
        return a * b

    row = DatasetRow(
        id=6,
        dir_type=1,
        name="obj",
        checksum="",
        parent_id=None,
        last_modified=None,
        anno={},
        etag="",
        version="",
        is_latest=True,
        size=7,
        owner_name="",
        owner_id="",
        path_str="path",
        source="",
        random=1234,
    )
    result = t(None, row)  # pylint: disable=no-value-for-parameter
    assert result == 42


def test_generator():
    @generator(C.name)
    def gen(parent, name):
        yield parent, name

    row = DatasetRow(
        id=6,
        dir_type=1,
        name="obj",
        checksum="",
        parent_id=None,
        last_modified=None,
        anno={},
        etag="",
        version="",
        is_latest=True,
        size=7,
        owner_name="",
        owner_id="",
        path_str="path",
        source="",
        random=1234,
    )

    assert list(gen(None, row)) == [(row, "obj")]

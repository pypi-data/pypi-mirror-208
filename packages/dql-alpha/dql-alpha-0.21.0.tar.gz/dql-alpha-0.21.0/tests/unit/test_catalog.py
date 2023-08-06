from textwrap import dedent

import pytest


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("file", False)],
    indirect=True,
)
def test_compile_query_script(cloud_test_catalog):
    script = dedent(
        """
        from dql.query import C, DatasetQuery, asUDF
        DatasetQuery("s3://bkt/dir1")
        """
    ).strip()
    result = cloud_test_catalog.catalog.compile_query_script(script)
    expected = dedent(
        """
        from dql.query import C, DatasetQuery, asUDF
        import dql.query.dataset
        dql.query.dataset.return_ds(
        DatasetQuery('s3://bkt/dir1'))
        """
    ).strip()
    assert result == expected

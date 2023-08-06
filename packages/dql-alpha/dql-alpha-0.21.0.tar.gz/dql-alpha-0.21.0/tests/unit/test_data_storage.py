from sqlalchemy import select
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import true

from ..data import ENTRIES, INVALID_ENTRIES
from ..utils import insert_entries


def test_validate_paths(data_storage):
    src = "s3://bucket1"
    data_storage = data_storage.clone(uri=src)
    data_storage.init_db(src, True)
    insert_entries(data_storage, ENTRIES + INVALID_ENTRIES)

    def count_valid_nodes():
        n = data_storage.nodes
        query = select(func.count(n.c.valid)).where(  # pylint: disable=not-callable
            n.c.valid == true()
        )
        return data_storage.execute(query).fetchone()[0]

    before_count = count_valid_nodes()
    data_storage.validate_paths()
    after_count = count_valid_nodes()

    assert before_count == 14
    assert after_count == 11

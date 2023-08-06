from datetime import datetime, timedelta, timezone

import pytest

from dql import utils
from dql.error import StorageNotFoundError
from dql.storage import STALE_HOURS_LIMIT, Status, Storage

TS = datetime(2022, 8, 1)
EXPIRES = datetime(2022, 8, 2)


def test_human_time():
    assert utils.human_time_to_int("1236") == 1236
    assert utils.human_time_to_int("3h") == 3 * 60 * 60
    assert utils.human_time_to_int("2w") == 2 * 7 * 24 * 60 * 60
    assert utils.human_time_to_int("4M") == 4 * 31 * 24 * 60 * 60

    assert utils.human_time_to_int("bla") is None


def test_storage():
    s = Storage("s3://foo", TS, EXPIRES)

    d = s.to_dict()
    assert d.get("uri") == s.uri


def test_expiration_time():
    assert Storage.get_expiration_time(TS, 12344) == TS + timedelta(seconds=12344)


def test_adding_storage(data_storage):
    # These tests re-use the same database for better performance
    data_storage.db.execute("DELETE FROM buckets")
    data_storage.db.commit()
    uri = "s3://whatever"
    with pytest.raises(StorageNotFoundError):
        data_storage.get_storage(uri)

    storage, _, _, _ = data_storage.register_storage_for_indexing(uri)
    cnt = data_storage.db.execute("SELECT COUNT() FROM buckets").fetchall()
    assert cnt[0][0] == 1

    query = "SELECT * FROM buckets WHERE uri = ?"
    bkt = data_storage.db.execute(query, [uri]).fetchall()
    assert len(bkt) == 1

    s = Storage(*bkt[0])
    assert s == storage


def test_storage_status(data_storage):
    uri = "s3://somebucket"

    data_storage.create_storage_if_not_registered(uri)
    storage = data_storage.get_storage(uri)
    assert storage.uri == uri
    assert storage.status == Status.CREATED

    (
        storage,
        need_index,
        in_progress,
        is_new,
    ) = data_storage.register_storage_for_indexing(uri)
    assert storage.status == Status.PENDING
    assert storage.uri == uri
    assert storage == data_storage.get_storage(uri)
    assert need_index is True
    assert in_progress is False
    assert is_new is True

    s2, need_index, in_progress, is_new = data_storage.register_storage_for_indexing(
        uri
    )
    assert s2.status == Status.PENDING
    assert storage == s2 == data_storage.get_storage(uri)
    assert need_index is False
    assert in_progress is True
    assert is_new is False

    end_time = datetime.now(timezone.utc)
    data_storage.mark_storage_indexed(uri, Status.COMPLETE, 1000, end_time)
    storage = data_storage.get_storage(uri)
    assert storage.status == Status.COMPLETE


@pytest.mark.parametrize(
    "ttl",
    (-1, 999999999999, 99999999999999, 9999999999999999),
)
def test_max_ttl(ttl):
    uri = "s3://whatever"
    expires = Storage.get_expiration_time(TS, ttl)
    storage = Storage(1, uri, TS, expires)
    assert storage.timestamp == TS
    assert storage.expires == datetime.max
    assert storage.timestamp_str  # no error
    assert storage.timestamp_to_local  # no error
    assert storage.expires_to_local  # no error


def test_storage_without_dates():
    uri = "s3://whatever"
    storage = Storage(1, uri, None, None)
    assert storage.timestamp is None
    assert storage.expires is None
    assert storage.timestamp_str is None  # no error
    assert storage.timestamp_to_local is None  # no error
    assert storage.expires_to_local is None  # no error
    assert storage.to_dict() == {
        "uri": uri,
        "timestamp": None,
        "expires": None,
    }


async def test_storage_update_last_inserted_at(data_storage):
    uri = "s3://bucket_last_inserted"
    data_storage.create_storage_if_not_registered(uri)
    await data_storage.update_last_inserted_at(uri)
    storage = data_storage.get_storage(uri)
    assert storage.last_inserted_at


def test_stale_storage(data_storage):
    uri_stale = "s3://bucket_stale"
    uri_not_stale = "s3://bucket_not_stale"

    data_storage.create_storage_if_not_registered(uri_stale)
    data_storage.create_storage_if_not_registered(uri_not_stale)

    data_storage.mark_storage_pending(data_storage.get_storage(uri_stale))
    data_storage.mark_storage_pending(data_storage.get_storage(uri_not_stale))

    # make storage looks stale
    updates = {
        "last_inserted_at": datetime.now(timezone.utc)
        - timedelta(hours=STALE_HOURS_LIMIT + 1)
    }
    s = data_storage.storages
    data_storage.execute(s.update().where(s.c.uri == uri_stale).values(**updates))

    data_storage.find_stale_storages()

    stale_storage = data_storage.get_storage(uri_stale)
    assert stale_storage.status == Status.STALE

    not_stale_storage = data_storage.get_storage(uri_not_stale)
    assert not_stale_storage.status == Status.PENDING

import posixpath
from datetime import datetime

import pytest

from dql.catalog import Catalog
from dql.catalog.catalog import DataSource
from dql.data_storage import SQLiteDataStorage
from dql.listing import Listing
from dql.node import DirType

# pylint: disable=redefined-outer-name

TS = datetime(2022, 8, 1)
DB_FILE = ".test.db"

TREE = {
    "dir1": {
        "d2": {None: ["file1.csv", "file2.csv"]},
        None: ["dataset.csv"],
    },
    "dir2": {None: ["diagram.png"]},
    None: ["users.csv"],
}


async def _tree_to_db(lst: Listing, tree: dict, dir_id: int = 1, path=""):
    for k, v in tree.items():
        if k:
            dir_path = posixpath.join(path, k)
            new_dir_id = await lst.insert_dir(dir_id, k, TS, posixpath.join(path, k), 0)
            await _tree_to_db(lst, v, new_dir_id, dir_path)
        else:
            for fname in v:
                await lst.insert_file(dir_id, fname, TS, posixpath.join(path, fname), 0)


@pytest.fixture
def data_storage():
    _data_storage = SQLiteDataStorage(db_file=":memory:")
    yield _data_storage
    _data_storage.db.execute("DROP TABLE IF EXISTS buckets")


@pytest.fixture
async def listing(data_storage):
    bkt = "s3://whatever"
    lst, _ = Catalog(data_storage).enlist_source(bkt, 1234, skip_indexing=True)
    lst.data_storage.init_db()
    await _tree_to_db(lst, TREE, await lst.insert_root())
    return lst


async def test_resolve_path_in_root(listing):
    node = listing.resolve_path("dir1")
    assert node.dir_type == DirType.DIR
    assert node.is_dir
    assert node.name == "dir1"


async def test_path_resolving_nested(listing):
    node = listing.resolve_path("dir1/d2/file2.csv")
    assert node.dir_type == DirType.FILE
    assert node.name == "file2.csv"
    assert not node.is_dir

    node = listing.resolve_path("dir1/d2")
    assert node.dir_type == DirType.DIR
    assert node.is_dir
    assert node.name == "d2"


async def test_resolve_not_existing_path(listing):
    with pytest.raises(FileNotFoundError):
        listing.resolve_path("dir1/fake-file-name")


async def test_resolve_root(listing):
    node = listing.resolve_path("")
    assert node.dir_type == DirType.ROOT
    assert node.is_dir
    assert node.name == ""


async def test_path_starts_with_slash(listing):
    node = listing.resolve_path("/dir1")
    assert node.dir_type == DirType.DIR
    assert node.is_dir
    assert node.name == "dir1"


async def test_dir_ends_with_slash(listing):
    node = listing.resolve_path("dir1/")
    assert node.dir_type == DirType.DIR
    assert node.is_dir
    assert node.name == "dir1"


async def test_file_ends_with_slash(listing):
    with pytest.raises(FileNotFoundError):
        listing.resolve_path("dir1/dataset.csv/")


def _match_filenames(nodes, expected_names):
    assert len(nodes) == len(expected_names)
    names = (node.name for node in nodes)
    assert set(names).intersection(set(expected_names))


async def test_basic_expansion(listing):
    nodes = listing.expand_path("*")
    _match_filenames(nodes, ["dir1", "dir2", "users.csv"])


async def test_subname_expansion(listing):
    nodes = listing.expand_path("di*/")
    _match_filenames(nodes, ["dir1", "dir2"])


async def test_multilevel_expansion(listing):
    nodes = listing.expand_path("dir[1,2]/d*")
    _match_filenames(nodes, ["dataset.csv", "diagram.png", "d2"])


async def test_expand_root(listing):
    nodes = listing.expand_path("")
    assert len(nodes) == 1
    assert nodes[0].dir_type == DirType.ROOT
    assert nodes[0].is_dir


async def test_list_dir(listing):
    dir1 = listing.resolve_path("dir1/")
    names = listing.ls_path(dir1, ["name"])
    assert {n[0] for n in names} == {"d2", "dataset.csv"}


async def test_list_file(listing):
    file = listing.resolve_path("dir1/dataset.csv")
    src = DataSource(listing, file)
    results = list(src.ls(["id", "name", "dir_type"]))
    assert {r[1] for r in results} == {"dataset.csv"}
    assert results[0][0] == file.id
    assert results[0][1] == file.name
    assert results[0][2] == DirType.FILE


async def test_subtree(listing):
    dir1 = listing.resolve_path("dir1/")
    nodes = listing.data_storage.walk_subtree(dir1)
    subtree_files = ["dir2", "dataset.csv", "file1.csv", "file2.csv"]
    _match_filenames(list(nodes), subtree_files)

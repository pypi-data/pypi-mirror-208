import pytest

from dql.node import DirType, Node
from dql.nodes_thread_pool import NodeChunk

# pylint: disable=redefined-outer-name


@pytest.fixture
def nodes():
    return iter(
        [
            make_size_node(11, DirType.DIR, 1, "f1", 100),
            make_size_node(12, DirType.FILE, 2, "f2", 100),
            make_size_node(13, DirType.FILE, 3, "f3", 100),
            make_size_node(14, DirType.FILE, 4, "", 100),
            make_size_node(15, DirType.FILE, 5, "f5", 100),
            make_size_node(16, DirType.DIR, 6, "f6", 100),
            make_size_node(17, DirType.FILE, 7, "f7", 100),
        ]
    )


def make_size_node(node_id, dir_type, parent_id, name, size):
    return Node._make(
        (
            node_id,
            dir_type,
            parent_id,
            name,
            "",
            "",
            "",
            True,
            None,
            size,
            "",
            "",
            name,
            None,
            True,
            1234,
            None,
            0,
        )
    )


def test_node_bucket_the_only_item():
    bkt = NodeChunk(iter([make_size_node(20, DirType.FILE, 2, "file.csv", 100)]), 201)

    result = next(bkt)
    assert len(result) == 1
    assert next(bkt, None) is None


def test_node_bucket_the_only_item_over_limit():
    bkt = NodeChunk(iter([make_size_node(20, DirType.FILE, 2, "file.csv", 100)]), 1)

    result = next(bkt)
    assert len(result) == 1
    assert next(bkt, None) is None


def test_node_bucket_the_last_one():
    bkt = NodeChunk(iter([make_size_node(20, DirType.FILE, 2, "file.csv", 100)]), 1)

    next(bkt)
    with pytest.raises(StopIteration):
        next(bkt)


def test_node_bucket_basic(nodes):
    bkt = list(NodeChunk(nodes, 201))

    assert len(bkt) == 2
    assert len(bkt[0]) == 3
    assert len(bkt[1]) == 1


def test_node_bucket_full_split(nodes):
    bkt = list(NodeChunk(nodes, 0))

    assert len(bkt) == 4
    assert len(bkt[0]) == 1
    assert len(bkt[1]) == 1
    assert len(bkt[2]) == 1
    assert len(bkt[3]) == 1

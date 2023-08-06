import io
import json
import os.path
import tarfile
from random import getrandbits

import pytest
from sqlalchemy import Integer, String

from dql.data_storage.abstract import RANDOM_BITS
from dql.dataset import Status as DatasetStatus
from dql.loader import DataView
from dql.node import DirType
from dql.query import C, DatasetQuery, Object, generator, udf
from dql.query.builtins import checksum, index_tar

from ..utils import DEFAULT_TREE, instantiate_tree


@pytest.mark.parametrize("from_path", [True, False])
@pytest.mark.parametrize("save", [True, False])
@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_filter(cloud_test_catalog, save, from_path):
    catalog = cloud_test_catalog.catalog
    conf = cloud_test_catalog.client_config
    # ensure we can select a subset of a bucket properly
    path = f"{cloud_test_catalog.src_uri}/cats"
    if from_path:
        ds = DatasetQuery(path=path, catalog=catalog, client_config=conf)
    else:
        sources = [path]
        globs = [s.rstrip("/") + "/*" for s in sources]
        catalog.index(sources, client_config=conf)
        catalog.create_shadow_dataset(
            "animals", globs, client_config=conf, recursive=True
        )
        ds = DatasetQuery(name="animals", catalog=catalog)
    q = ds.filter(C.size < 13).filter(C.path_str.glob("cats/*") | (C.size < 4))
    if save:
        ds_name = "animals_cats"
        q.save(ds_name)
        new_query = DatasetQuery(name=ds_name, catalog=catalog)
        result = new_query.results()
        dataset_record = catalog.get_dataset(ds_name)
        assert dataset_record.status == DatasetStatus.COMPLETE
    else:
        result = q.results()
    assert len(result) == 2


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_udf(cloud_test_catalog):
    catalog = cloud_test_catalog.catalog
    conf = cloud_test_catalog.client_config
    sources = [cloud_test_catalog.src_uri]
    globs = [s.rstrip("/") + "/*" for s in sources]
    catalog.index(sources, client_config=conf)
    catalog.create_shadow_dataset("animals", globs, client_config=conf, recursive=True)

    @udf(Integer, C.name)
    def name_len(name):
        # A very simple udf.
        return len(name)

    q = (
        DatasetQuery(name="animals", catalog=catalog)
        .filter(C.size < 13)
        .filter(C.path_str.glob("cats/*") | (C.size < 4))
        .add_signal(name_len, "name_len")
    )
    result = q.results()

    assert len(result) == 3


def to_str(buf) -> str:
    return io.TextIOWrapper(buf, encoding="utf8").read()


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_udf_object_param(cloud_test_catalog, dogs_shadow_dataset):
    # Setup catalog.
    catalog = cloud_test_catalog.catalog
    catalog.client_config = cloud_test_catalog.client_config

    @udf(String, C.name, Object(to_str))
    def signal(name, obj):
        # A very simple udf.
        return name + " -> " + obj

    q = DatasetQuery(name=dogs_shadow_dataset.name, catalog=catalog).add_signal(
        signal, "signal"
    )
    result = q.results()

    assert len(result) == 4
    signals = [r[-1] for r in result]
    assert signals == ["dog1 -> woof", "dog2 -> arf", "dog3 -> bark", "dog4 -> ruff"]


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_union(cloud_test_catalog):
    catalog = cloud_test_catalog.catalog
    conf = cloud_test_catalog.client_config
    sources = [str(cloud_test_catalog.src_uri)]
    catalog.index(sources, client_config=conf)

    src = cloud_test_catalog.src_uri
    catalog.create_shadow_dataset(
        "dogs", [f"{src}/dogs/*"], client_config=conf, recursive=True
    )
    catalog.create_shadow_dataset(
        "cats", [f"{src}/cats/*"], client_config=conf, recursive=True
    )

    dogs = DatasetQuery(name="dogs", catalog=catalog)
    cats = DatasetQuery(name="cats", catalog=catalog)

    (dogs | cats).save("dogs_cats")

    result = DatasetQuery(name="dogs_cats", catalog=catalog).results()
    assert len(result) == 6


def test_loader_from_query(cloud_test_catalog):
    catalog = cloud_test_catalog.catalog
    conf = cloud_test_catalog.client_config
    src_uri = cloud_test_catalog.src_uri
    catalog.index([src_uri], client_config=conf)
    catalog.create_shadow_dataset(
        "animals", [f"{src_uri}/*"], client_config=conf, recursive=True
    )
    q = DatasetQuery(name="animals", catalog=catalog).filter(C.path_str.glob("cats/*"))

    def transform(row, sample):
        return sample, row.name[-1]

    ds = DataView.from_query(
        q, reader=to_str, transform=transform, catalog=catalog, client_config=conf
    )
    assert set(ds) == {("meow", "1"), ("mrow", "2")}


def create_subobject(row, path_str: str, size: int):
    """Create a subobject with this row as its parent."""
    return {
        # Values that depend on the parent object.
        "dir_type": 0,
        "parent_id": row.id,
        # Inherited values.
        "owner_name": row.owner_name,
        "owner_id": row.owner_id,
        "is_latest": row.is_latest,
        "source": row.source,
        # User-provided values.
        "name": os.path.normpath(os.path.basename(path_str)),
        "path_str": _sub_path(row, path_str),
        "size": size,
        # Unspecified.
        "version": None,
        "etag": None,
        # Generated.
        "random": getrandbits(RANDOM_BITS),
    }


def _sub_path(row, child_path: str) -> str:
    """Define the path of the subobject in relation to the parent."""
    # The parent/child annotation logic will need to be updated.
    return f"{row.path_str}:{child_path}"


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_row_generator(cloud_test_catalog, dogs_shadow_dataset):
    # Setup catalog.
    catalog = cloud_test_catalog.catalog
    catalog.client_config = cloud_test_catalog.client_config

    @generator(C.name, C.path_str)
    def gen(parent, _, __):
        # A very simple generator.
        yield create_subobject(parent, "subobject", 50)

    q = DatasetQuery(name=dogs_shadow_dataset.name, catalog=catalog).generate(gen)
    result = q.results()

    assert len(result) == 8

    signals = {r[12]: r[3] for r in result}  # path_str: name
    assert signals == {
        "dogs/dog1": "dog1",
        "dogs/dog1:subobject": "subobject",
        "dogs/dog2": "dog2",
        "dogs/dog2:subobject": "subobject",
        "dogs/dog3": "dog3",
        "dogs/dog3:subobject": "subobject",
        "dogs/others/dog4": "dog4",
        "dogs/others/dog4:subobject": "subobject",
    }


@pytest.mark.parametrize("tree", [{}], indirect=True)
def test_index_tar(cloud_test_catalog):
    ctc = cloud_test_catalog
    (ctc.working_dir / "data").mkdir()
    instantiate_tree(ctc.working_dir / "data", DEFAULT_TREE)
    with (ctc.src / "animals.tar").open("wb") as f:
        with tarfile.open(fileobj=f, mode="w") as archive:
            for p in (ctc.working_dir / "data").iterdir():
                archive.add(p, p.name)

    catalog = ctc.catalog
    catalog.client_config = ctc.client_config
    catalog.index([ctc.src_uri])
    catalog.create_shadow_dataset("animals", [ctc.src_uri])

    q = DatasetQuery(name="animals", catalog=catalog).generate(index_tar)
    q.save("extracted")

    rows = list(catalog.ls_dataset_rows("extracted"))
    assert {row.name for row in rows} == {
        "animals.tar",
        "cats/cat1",
        "cats/cat2",
        "description",
        "dogs/dog1",
        "dogs/dog2",
        "dogs/dog3",
        "dogs/others/dog4",
    }

    offsets = [
        json.loads(row.sub_meta)["offset"] for row in rows if row.name != "animals.tar"
    ]
    # Check that offsets are unique integers
    assert all(isinstance(offset, int) for offset in offsets)
    assert len(set(offsets)) == len(offsets)

    assert all(
        row.dir_type == DirType.TAR_FILE for row in rows if row.name != "animals.tar"
    )


@pytest.mark.parametrize(
    "cloud_type,version_aware",
    [("s3", True)],
    indirect=True,
)
def test_checksum_udf(cloud_test_catalog, dogs_shadow_dataset):
    # Setup catalog.
    catalog = cloud_test_catalog.catalog
    catalog.client_config = cloud_test_catalog.client_config

    q = DatasetQuery(name=dogs_shadow_dataset.name, catalog=catalog).add_signal(
        checksum
    )
    result = q.results()

    assert len(result) == 4


@pytest.mark.parametrize("tree", [{}], indirect=True)
def test_tar_loader(cloud_test_catalog):
    ctc = cloud_test_catalog
    (ctc.working_dir / "data").mkdir()
    instantiate_tree(ctc.working_dir / "data", DEFAULT_TREE)
    with (ctc.src / "animals.tar").open("wb") as f:
        with tarfile.open(fileobj=f, mode="w") as archive:
            for p in (ctc.working_dir / "data").iterdir():
                archive.add(p, p.name)
    catalog = ctc.catalog
    catalog.client_config = ctc.client_config
    catalog.index([ctc.src_uri])
    catalog.create_shadow_dataset("animals", [ctc.src_uri])
    q = DatasetQuery(name="animals", catalog=catalog).generate(index_tar)
    q.save("extracted")

    q = DatasetQuery(name="extracted", catalog=catalog).filter(
        C.path_str.glob("*/cats/*")
    )
    assert len(q.results()) == 2

    def transform(row, sample):
        return sample, row.name[-1]

    ds = DataView.from_query(q, reader=to_str, transform=transform, catalog=catalog)
    assert set(ds) == {("meow", "1"), ("mrow", "2")}

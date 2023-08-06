import os
import shutil
import tarfile

import pytest
import yaml
from fsspec.implementations.local import LocalFileSystem

from dql.catalog import indexer_formats, parse_edql_file
from dql.utils import remove_readonly

from ..utils import DEFAULT_TREE, instantiate_tree, tree_from_path

# pylint: disable=redefined-outer-name,unused-argument,protected-access


def test_find(cloud_test_catalog):
    src_uri = cloud_test_catalog.src_uri
    catalog = cloud_test_catalog.catalog
    config = cloud_test_catalog.client_config

    assert set(catalog.find([src_uri], client_config=config)) == {
        f"{src_uri}/description",
        f"{src_uri}/cats/",
        f"{src_uri}/cats/cat1",
        f"{src_uri}/cats/cat2",
        f"{src_uri}/dogs/",
        f"{src_uri}/dogs/dog1",
        f"{src_uri}/dogs/dog2",
        f"{src_uri}/dogs/dog3",
        f"{src_uri}/dogs/others/",
        f"{src_uri}/dogs/others/dog4",
    }

    with pytest.raises(FileNotFoundError):
        set(
            catalog.find(
                [f"{src_uri}/does_not_exist"],
                client_config=config,
            )
        )


def test_find_names_paths_size_type(cloud_test_catalog):
    src_uri = cloud_test_catalog.src_uri
    catalog = cloud_test_catalog.catalog
    config = cloud_test_catalog.client_config

    assert set(catalog.find([src_uri], names=["*cat*"], client_config=config)) == {
        f"{src_uri}/cats/",
        f"{src_uri}/cats/cat1",
        f"{src_uri}/cats/cat2",
    }

    assert set(
        catalog.find([src_uri], names=["*cat*"], typ="dir", client_config=config)
    ) == {
        f"{src_uri}/cats/",
    }

    assert (
        len(list(catalog.find([src_uri], names=["*CAT*"], client_config=config))) == 0
    )

    assert set(catalog.find([src_uri], inames=["*CAT*"], client_config=config)) == {
        f"{src_uri}/cats/",
        f"{src_uri}/cats/cat1",
        f"{src_uri}/cats/cat2",
    }

    assert set(catalog.find([src_uri], paths=["*cats/cat*"], client_config=config)) == {
        f"{src_uri}/cats/cat1",
        f"{src_uri}/cats/cat2",
    }

    assert (
        len(list(catalog.find([src_uri], paths=["*caTS/CaT**"], client_config=config)))
        == 0
    )

    assert set(
        catalog.find([src_uri], ipaths=["*caTS/CaT*"], client_config=config)
    ) == {
        f"{src_uri}/cats/cat1",
        f"{src_uri}/cats/cat2",
    }

    assert set(catalog.find([src_uri], size="5", typ="f", client_config=config)) == {
        f"{src_uri}/description",
    }

    assert set(catalog.find([src_uri], size="-3", typ="f", client_config=config)) == {
        f"{src_uri}/dogs/dog2",
    }


def test_find_names_columns(cloud_test_catalog, cloud_type):
    src_uri = cloud_test_catalog.src_uri
    catalog = cloud_test_catalog.catalog
    config = cloud_test_catalog.client_config

    owner = "webfile" if cloud_type == "s3" else ""

    assert set(
        catalog.find(
            [src_uri],
            names=["*cat*"],
            columns=["du", "name", "owner", "path", "size", "type"],
            client_config=config,
        )
    ) == {
        "\t".join(columns)
        for columns in [
            ["8", "cats", "", f"{src_uri}/cats/", "0", "d"],
            ["4", "cat1", owner, f"{src_uri}/cats/cat1", "4", "f"],
            ["4", "cat2", owner, f"{src_uri}/cats/cat2", "4", "f"],
        ]
    }


@pytest.mark.parametrize(
    "recursive,star,dir_exists",
    (
        (True, True, False),
        (True, False, False),
        (True, False, True),
        (False, True, False),
        (False, False, False),
    ),
)
def test_cp_root(cloud_test_catalog, recursive, star, dir_exists):
    src_uri = cloud_test_catalog.src_uri
    working_dir = cloud_test_catalog.working_dir
    catalog = cloud_test_catalog.catalog

    dest = working_dir / "data"

    if star:
        src_path = f"{src_uri}/*"
    else:
        src_path = src_uri

    if star:
        with pytest.raises(FileNotFoundError):
            catalog.cp(
                [src_path],
                str(dest),
                client_config=cloud_test_catalog.client_config,
                recursive=recursive,
            )

    if dir_exists or star:
        dest.mkdir()

    catalog.cp(
        [src_path],
        str(dest),
        client_config=cloud_test_catalog.client_config,
        recursive=recursive,
    )

    if not star and not recursive:
        # The root directory is skipped, so nothing is copied
        assert tree_from_path(dest) == {}
        return

    assert (dest / "description").read_text() == "Cats and Dogs"

    # Testing DQL File Contents
    assert dest.with_suffix(".edql").is_file()
    edql_contents = yaml.safe_load(dest.with_suffix(".edql").read_text())
    assert len(edql_contents) == 1
    data = edql_contents[0]
    assert data["data-source"]["uri"] == src_path.rstrip("/")
    expected_file_count = 7 if recursive else 1
    assert len(data["files"]) == expected_file_count
    files_by_name = {f["name"]: f for f in data["files"]}

    # Directories should never be saved
    assert "cats" not in files_by_name
    assert "dogs" not in files_by_name
    assert "others" not in files_by_name
    assert "dogs/others" not in files_by_name

    # Ensure all files have checksum saved
    for f in data["files"]:
        assert len(f["checksum"]) > 1

    # Description is always copied (if anything is copied)
    prefix = "" if star or (recursive and not dir_exists) else "/"
    assert files_by_name[f"{prefix}description"]["size"] == 13

    if recursive:
        assert tree_from_path(dest) == DEFAULT_TREE
        assert files_by_name[f"{prefix}cats/cat1"]["size"] == 4
        assert files_by_name[f"{prefix}cats/cat2"]["size"] == 4
        assert files_by_name[f"{prefix}dogs/dog1"]["size"] == 4
        assert files_by_name[f"{prefix}dogs/dog2"]["size"] == 3
        assert files_by_name[f"{prefix}dogs/dog3"]["size"] == 4
        assert files_by_name[f"{prefix}dogs/others/dog4"]["size"] == 4
        return

    assert (dest / "cats").exists() is False
    assert (dest / "dogs").exists() is False
    for prefix in ["/", ""]:
        assert f"{prefix}cats/cat1" not in files_by_name
        assert f"{prefix}cats/cat2" not in files_by_name
        assert f"{prefix}dogs/dog1" not in files_by_name
        assert f"{prefix}dogs/dog2" not in files_by_name
        assert f"{prefix}dogs/dog3" not in files_by_name
        assert f"{prefix}dogs/others/dog4" not in files_by_name


@pytest.mark.parametrize(
    "recursive,star,slash,dir_exists",
    (
        (True, True, False, False),
        (True, False, False, False),
        (True, False, False, True),
        (True, False, True, False),
        (False, True, False, False),
        (False, False, False, False),
        (False, False, True, False),
    ),
)
def test_cp_subdir(cloud_test_catalog, recursive, star, slash, dir_exists):
    src_uri = f"{cloud_test_catalog.src_uri}/dogs"
    working_dir = cloud_test_catalog.working_dir
    catalog = cloud_test_catalog.catalog

    dest = working_dir / "data"

    if star:
        src_path = f"{src_uri}/*"
    elif slash:
        src_path = f"{src_uri}/"
    else:
        src_path = src_uri

    if star:
        with pytest.raises(FileNotFoundError):
            catalog.cp(
                [src_path],
                str(dest),
                client_config=cloud_test_catalog.client_config,
                recursive=recursive,
            )

    if dir_exists or star:
        dest.mkdir()

    catalog.cp(
        [src_path],
        str(dest),
        client_config=cloud_test_catalog.client_config,
        recursive=recursive,
    )

    if not star and not recursive:
        # Directories are skipped, so nothing is copied
        assert tree_from_path(dest) == {}
        return

    # Testing DQL File Contents
    assert dest.with_suffix(".edql").is_file()
    edql_contents = yaml.safe_load(dest.with_suffix(".edql").read_text())
    assert len(edql_contents) == 1
    data = edql_contents[0]
    assert data["data-source"]["uri"] == src_path.rstrip("/")
    expected_file_count = 4 if recursive else 3
    assert len(data["files"]) == expected_file_count
    files_by_name = {f["name"]: f for f in data["files"]}

    # Directories should never be saved
    assert "others" not in files_by_name
    assert "dogs/others" not in files_by_name

    # Ensure all files have checksum saved
    for f in data["files"]:
        assert len(f["checksum"]) > 1

    if not dir_exists:
        assert (dest / "dog1").read_text() == "woof"
        assert (dest / "dog2").read_text() == "arf"
        assert (dest / "dog3").read_text() == "bark"
        assert (dest / "dogs").exists() is False
        assert files_by_name["dog1"]["size"] == 4
        assert files_by_name["dog2"]["size"] == 3
        assert files_by_name["dog3"]["size"] == 4
        if recursive:
            assert (dest / "others" / "dog4").read_text() == "ruff"
            assert files_by_name["others/dog4"]["size"] == 4
        else:
            assert (dest / "others").exists() is False
            assert "others/dog4" not in files_by_name
        return

    assert tree_from_path(dest / "dogs") == DEFAULT_TREE["dogs"]
    assert (dest / "dog1").exists() is False
    assert (dest / "dog2").exists() is False
    assert (dest / "dog3").exists() is False
    assert (dest / "others").exists() is False
    assert files_by_name["dogs/dog1"]["size"] == 4
    assert files_by_name["dogs/dog2"]["size"] == 3
    assert files_by_name["dogs/dog3"]["size"] == 4
    assert files_by_name["dogs/others/dog4"]["size"] == 4


@pytest.mark.parametrize(
    "recursive,star,slash",
    (
        (True, True, False),
        (True, False, False),
        (True, False, True),
        (False, True, False),
        (False, False, False),
        (False, False, True),
    ),
)
def test_cp_multi_subdir(cloud_test_catalog, recursive, star, slash):
    sources = [
        f"{cloud_test_catalog.src_uri}/cats",
        f"{cloud_test_catalog.src_uri}/dogs",
    ]
    working_dir = cloud_test_catalog.working_dir
    catalog = cloud_test_catalog.catalog

    dest = working_dir / "data"

    if star:
        src_paths = [f"{src}/*" for src in sources]
    elif slash:
        src_paths = [f"{src}/" for src in sources]
    else:
        src_paths = sources

    with pytest.raises(FileNotFoundError):
        catalog.cp(
            src_paths,
            str(dest),
            client_config=cloud_test_catalog.client_config,
            recursive=recursive,
        )

    dest.mkdir()

    catalog.cp(
        src_paths,
        str(dest),
        client_config=cloud_test_catalog.client_config,
        recursive=recursive,
    )

    if not star and not recursive:
        # Directories are skipped, so nothing is copied
        assert tree_from_path(dest) == {}
        return

    # Testing DQL File Contents
    assert dest.with_suffix(".edql").is_file()
    edql_contents = yaml.safe_load(dest.with_suffix(".edql").read_text())
    assert len(edql_contents) == 2
    data_cats = edql_contents[0]
    data_dogs = edql_contents[1]
    assert data_cats["data-source"]["uri"] == src_paths[0].rstrip("/")
    assert data_dogs["data-source"]["uri"] == src_paths[1].rstrip("/")
    assert len(data_cats["files"]) == 2
    assert len(data_dogs["files"]) == 4 if recursive else 3
    cat_files_by_name = {f["name"]: f for f in data_cats["files"]}
    dog_files_by_name = {f["name"]: f for f in data_dogs["files"]}

    # Directories should never be saved
    assert "others" not in dog_files_by_name
    assert "dogs/others" not in dog_files_by_name

    # Ensure all files have checksum saved
    for f in data_cats["files"]:
        assert len(f["checksum"]) > 1
    for f in data_dogs["files"]:
        assert len(f["checksum"]) > 1

    if star or slash:
        assert (dest / "cat1").read_text() == "meow"
        assert (dest / "cat2").read_text() == "mrow"
        assert (dest / "dog1").read_text() == "woof"
        assert (dest / "dog2").read_text() == "arf"
        assert (dest / "dog3").read_text() == "bark"
        assert (dest / "cats").exists() is False
        assert (dest / "dogs").exists() is False
        assert cat_files_by_name["cat1"]["size"] == 4
        assert cat_files_by_name["cat2"]["size"] == 4
        assert dog_files_by_name["dog1"]["size"] == 4
        assert dog_files_by_name["dog2"]["size"] == 3
        assert dog_files_by_name["dog3"]["size"] == 4
        if recursive:
            assert (dest / "others" / "dog4").read_text() == "ruff"
            assert dog_files_by_name["others/dog4"]["size"] == 4
        else:
            assert (dest / "others").exists() is False
            assert "others/dog4" not in dog_files_by_name
        return

    assert (dest / "cats" / "cat1").read_text() == "meow"
    assert (dest / "cats" / "cat2").read_text() == "mrow"
    assert (dest / "dogs" / "dog1").read_text() == "woof"
    assert (dest / "dogs" / "dog2").read_text() == "arf"
    assert (dest / "dogs" / "dog3").read_text() == "bark"
    assert (dest / "dogs" / "others" / "dog4").read_text() == "ruff"
    assert (dest / "cat1").exists() is False
    assert (dest / "cat2").exists() is False
    assert (dest / "dog1").exists() is False
    assert (dest / "dog2").exists() is False
    assert (dest / "dog3").exists() is False
    assert (dest / "others").exists() is False
    assert cat_files_by_name["cats/cat1"]["size"] == 4
    assert cat_files_by_name["cats/cat2"]["size"] == 4
    assert dog_files_by_name["dogs/dog1"]["size"] == 4
    assert dog_files_by_name["dogs/dog2"]["size"] == 3
    assert dog_files_by_name["dogs/dog3"]["size"] == 4
    assert dog_files_by_name["dogs/others/dog4"]["size"] == 4


def test_cp_double_subdir(cloud_test_catalog):
    src_path = f"{cloud_test_catalog.src_uri}/dogs/others"
    working_dir = cloud_test_catalog.working_dir
    catalog = cloud_test_catalog.catalog

    dest = working_dir / "data"

    catalog.cp(
        [src_path],
        str(dest),
        client_config=cloud_test_catalog.client_config,
        recursive=True,
    )

    # Testing DQL File Contents
    assert dest.with_suffix(".edql").is_file()
    edql_contents = yaml.safe_load(dest.with_suffix(".edql").read_text())
    assert len(edql_contents) == 1
    data = edql_contents[0]
    assert data["data-source"]["uri"] == src_path.rstrip("/")
    assert len(data["files"]) == 1
    files_by_name = {f["name"]: f for f in data["files"]}

    # Directories should never be saved
    assert "others" not in files_by_name
    assert "dogs/others" not in files_by_name

    # Ensure all files have checksum saved
    for f in data["files"]:
        assert len(f["checksum"]) > 1

    assert (dest / "dogs").exists() is False
    assert (dest / "others").exists() is False
    assert (dest / "dog4").read_text() == "ruff"
    assert files_by_name["dog4"]["size"] == 4


@pytest.mark.parametrize("no_glob", (True, False))
def test_cp_single_file(cloud_test_catalog, no_glob):
    working_dir = cloud_test_catalog.working_dir
    catalog = cloud_test_catalog.catalog

    dest = working_dir / "data"

    src_path = f"{cloud_test_catalog.src_uri}/dogs/dog1"

    dest.mkdir()

    catalog.cp(
        [src_path],
        str(dest / "local_dog"),
        client_config=cloud_test_catalog.client_config,
        no_edql_file=True,
        no_glob=no_glob,
    )

    assert tree_from_path(dest) == {"local_dog": "woof"}


def test_cp_edql_file_options(cloud_test_catalog):
    working_dir = cloud_test_catalog.working_dir
    catalog = cloud_test_catalog.catalog

    dest = working_dir / "data"

    src_path = f"{cloud_test_catalog.src_uri}/dogs/*"

    edql_file = working_dir / "custom_name.edql"

    catalog.cp(
        [src_path],
        str(dest),
        client_config=cloud_test_catalog.client_config,
        recursive=False,
        edql_only=True,
        edql_file=str(edql_file),
    )

    assert (dest / "dog1").exists() is False
    assert (dest / "dog2").exists() is False
    assert (dest / "dog3").exists() is False
    assert (dest / "dogs").exists() is False
    assert (dest / "others").exists() is False
    assert dest.with_suffix(".edql").exists() is False

    # Testing DQL File Contents
    assert edql_file.is_file()
    edql_contents = yaml.safe_load(edql_file.read_text())
    assert len(edql_contents) == 1
    data = edql_contents[0]
    assert data["data-source"]["uri"] == src_path
    expected_file_count = 3
    assert len(data["files"]) == expected_file_count
    files_by_name = {f["name"]: f for f in data["files"]}

    assert parse_edql_file(str(edql_file)) == edql_contents

    # Directories should never be saved
    assert "others" not in files_by_name
    assert "dogs/others" not in files_by_name

    assert files_by_name["dog1"]["size"] == 4
    assert files_by_name["dog2"]["size"] == 3
    assert files_by_name["dog3"]["size"] == 4
    assert "others/dog4" not in files_by_name

    with pytest.raises(FileNotFoundError):
        # Should fail, as * will not be expanded
        catalog.cp(
            [src_path],
            str(dest),
            client_config=cloud_test_catalog.client_config,
            recursive=False,
            edql_only=True,
            edql_file=str(edql_file),
            no_glob=True,
        )

    # Should succeed, as the DQL file exists check will be skipped
    edql_only_data = catalog.cp(
        [src_path],
        str(dest),
        client_config=cloud_test_catalog.client_config,
        recursive=False,
        edql_only=True,
        edql_file=str(edql_file),
        no_edql_file=True,
    )

    # Check the returned DQL data contents
    assert len(edql_only_data) == len(edql_contents)
    edql_only_source = edql_only_data[0]
    assert edql_only_source["data-source"]["uri"] == src_path.rstrip("/")
    assert edql_only_source["files"] == data["files"]


def test_cp_edql_file_sources(cloud_test_catalog):
    sources = [
        f"{cloud_test_catalog.src_uri}/cats/",
        f"{cloud_test_catalog.src_uri}/dogs/*",
    ]
    working_dir = cloud_test_catalog.working_dir
    catalog = cloud_test_catalog.catalog

    dest = working_dir / "data"

    edql_files = [
        working_dir / "custom_cats.edql",
        working_dir / "custom_dogs.edql",
    ]

    catalog.cp(
        sources[:1],
        str(dest),
        client_config=cloud_test_catalog.client_config,
        recursive=True,
        edql_only=True,
        edql_file=str(edql_files[0]),
    )

    catalog.cp(
        sources[1:],
        str(dest),
        client_config=cloud_test_catalog.client_config,
        recursive=True,
        edql_only=True,
        edql_file=str(edql_files[1]),
    )

    # Files should not be copied yet
    assert (dest / "cat1").exists() is False
    assert (dest / "cat2").exists() is False
    assert (dest / "cats").exists() is False
    assert (dest / "dog1").exists() is False
    assert (dest / "dog2").exists() is False
    assert (dest / "dog3").exists() is False
    assert (dest / "dogs").exists() is False
    assert (dest / "others").exists() is False

    # Testing DQL File Contents
    edql_data = []
    for dqf in edql_files:
        assert dqf.is_file()
        edql_contents = yaml.safe_load(dqf.read_text())
        assert len(edql_contents) == 1
        edql_data.extend(edql_contents)

    assert len(edql_data) == 2
    data_cats1 = edql_data[0]
    data_dogs1 = edql_data[1]
    assert data_cats1["data-source"]["uri"] == sources[0].rstrip("/")
    assert data_dogs1["data-source"]["uri"] == sources[1].rstrip("/")
    assert len(data_cats1["files"]) == 2
    assert len(data_dogs1["files"]) == 4
    cat_files_by_name1 = {f["name"]: f for f in data_cats1["files"]}
    dog_files_by_name1 = {f["name"]: f for f in data_dogs1["files"]}

    # Directories should never be saved
    assert "others" not in dog_files_by_name1
    assert "dogs/others" not in dog_files_by_name1

    assert cat_files_by_name1["cat1"]["size"] == 4
    assert cat_files_by_name1["cat2"]["size"] == 4
    assert dog_files_by_name1["dog1"]["size"] == 4
    assert dog_files_by_name1["dog2"]["size"] == 3
    assert dog_files_by_name1["dog3"]["size"] == 4
    assert dog_files_by_name1["others/dog4"]["size"] == 4

    assert not dest.exists()

    with pytest.raises(FileNotFoundError):
        catalog.cp(
            [str(dqf) for dqf in edql_files],
            str(dest),
            client_config=cloud_test_catalog.client_config,
            recursive=True,
        )

    dest.mkdir()

    # Copy using these DQL files as sources
    catalog.cp(
        [str(dqf) for dqf in edql_files],
        str(dest),
        client_config=cloud_test_catalog.client_config,
        recursive=True,
    )

    # Files should now be copied
    assert (dest / "cat1").read_text() == "meow"
    assert (dest / "cat2").read_text() == "mrow"
    assert (dest / "dog1").read_text() == "woof"
    assert (dest / "dog2").read_text() == "arf"
    assert (dest / "dog3").read_text() == "bark"
    assert (dest / "others" / "dog4").read_text() == "ruff"

    # Testing DQL File Contents
    assert dest.with_suffix(".edql").is_file()
    edql_contents = yaml.safe_load(dest.with_suffix(".edql").read_text())
    assert len(edql_contents) == 2
    data_cats2 = edql_contents[0]
    data_dogs2 = edql_contents[1]
    assert data_cats2["data-source"]["uri"] == sources[0].rstrip("/")
    assert data_dogs2["data-source"]["uri"] == sources[1].rstrip("/")
    assert len(data_cats2["files"]) == 2
    assert len(data_dogs2["files"]) == 4
    cat_files_by_name2 = {f["name"]: f for f in data_cats2["files"]}
    dog_files_by_name2 = {f["name"]: f for f in data_dogs2["files"]}

    # Ensure all files have checksum saved
    for f in data_cats2["files"]:
        assert len(f["checksum"]) > 1
    for f in data_dogs2["files"]:
        assert len(f["checksum"]) > 1

    # Directories should never be saved
    assert "others" not in dog_files_by_name2
    assert "dogs/others" not in dog_files_by_name2

    assert cat_files_by_name2["cat1"]["size"] == 4
    assert cat_files_by_name2["cat2"]["size"] == 4
    assert dog_files_by_name2["dog1"]["size"] == 4
    assert dog_files_by_name2["dog2"]["size"] == 3
    assert dog_files_by_name2["dog3"]["size"] == 4
    assert dog_files_by_name2["others/dog4"]["size"] == 4


@pytest.mark.parametrize("cloud_type", ["file"], indirect=True)
def test_cp_symlinks(cloud_test_catalog):
    catalog = cloud_test_catalog.catalog
    src_uri = cloud_test_catalog.src_uri
    work_dir = cloud_test_catalog.working_dir
    dest = work_dir / "data"
    dest.mkdir()
    s = catalog.data_storage.storages
    catalog.data_storage.execute(
        s.update().where(s.c.uri == src_uri).values(symlinks=True)
    )
    catalog.cp([f"{src_uri}/dogs/"], str(dest), recursive=True)

    assert (dest / "dog1").is_symlink()
    assert os.path.realpath(dest / "dog1") == str(
        cloud_test_catalog.src / "dogs" / "dog1"
    )
    assert (dest / "dog1").read_text() == "woof"
    assert (dest / "others" / "dog4").is_symlink()
    assert os.path.realpath(dest / "others" / "dog4") == str(
        cloud_test_catalog.src / "dogs" / "others" / "dog4"
    )
    assert (dest / "others" / "dog4").read_text() == "ruff"


def test_get(cloud_test_catalog):
    src_uri = cloud_test_catalog.src_uri
    catalog = cloud_test_catalog.catalog
    config = cloud_test_catalog.client_config
    dest = cloud_test_catalog.working_dir / "data"

    catalog.get(src_uri, str(dest), client_config=config)

    assert (dest / "cats" / "cat1").read_text() == "meow"
    assert (dest / "cats" / "cat2").read_text() == "mrow"
    assert (dest / "dogs" / "dog1").read_text() == "woof"
    assert (dest / "dogs" / "dog2").read_text() == "arf"
    assert (dest / "dogs" / "dog3").read_text() == "bark"
    assert (dest / "dogs" / "others" / "dog4").read_text() == "ruff"
    assert dest.with_suffix(".edql").is_file()


def test_get_subdir(cloud_test_catalog):
    src = f"{cloud_test_catalog.src_uri}/dogs"
    working_dir = cloud_test_catalog.working_dir
    catalog = cloud_test_catalog.catalog

    dest = working_dir / "data"

    catalog.get(src, str(dest), client_config=cloud_test_catalog.client_config)

    assert tree_from_path(dest) == DEFAULT_TREE["dogs"]

    assert dest.with_suffix(".edql").is_file()
    assert parse_edql_file(str(dest.with_suffix(".edql"))) == [
        yaml.safe_load(dest.with_suffix(".edql").read_text())
    ]

    with pytest.raises(RuntimeError):
        # An error should be raised if the output directory already exists
        catalog.get(src, str(dest), client_config=cloud_test_catalog.client_config)

    shutil.rmtree(dest, onerror=remove_readonly)
    assert dest.with_suffix(".edql").is_file()

    with pytest.raises(RuntimeError):
        # An error should also be raised if the dataset file already exists
        catalog.get(src, str(dest), client_config=cloud_test_catalog.client_config)


def test_du(cloud_test_catalog):
    src_uri = cloud_test_catalog.src_uri
    catalog = cloud_test_catalog.catalog

    expected_results = [
        (f"{src_uri}/cats/", 8),
        (f"{src_uri}/dogs/others/", 4),
        (f"{src_uri}/dogs/", 15),
        (f"{src_uri}/", 36),
    ]

    results = catalog.du([src_uri], client_config=cloud_test_catalog.client_config)

    assert set(results) == set(expected_results[3:])

    results = catalog.du(
        [src_uri], client_config=cloud_test_catalog.client_config, depth=1
    )

    assert set(results) == set(expected_results[:1] + expected_results[2:])

    results = catalog.du(
        [src_uri], client_config=cloud_test_catalog.client_config, depth=5
    )

    assert set(results) == set(expected_results)


def test_ls_glob(cloud_test_catalog):
    src_uri = cloud_test_catalog.src_uri
    catalog = cloud_test_catalog.catalog

    assert sorted(
        (source.node.name, [r[0] for r in results])
        for source, results in catalog.ls(
            [f"{src_uri}/dogs/dog*"],
            fields=["name"],
            client_config=cloud_test_catalog.client_config,
        )
    ) == [("dog1", ["dog1"]), ("dog2", ["dog2"]), ("dog3", ["dog3"])]


def clear_storages(catalog):
    ds = catalog.data_storage
    ds.execute(ds.storages.delete())


@pytest.mark.parametrize("cloud_type", ["file"], indirect=True)
@pytest.mark.parametrize("use_path", [False, True])
def test_add_storage(cloud_test_catalog, use_path):
    catalog = cloud_test_catalog.catalog
    src_uri = cloud_test_catalog.src_uri
    clear_storages(catalog)
    if use_path:
        src = LocalFileSystem._strip_protocol(src_uri)
        src = os.path.relpath(src)
    else:
        src = src_uri
    with pytest.raises(RuntimeError):
        catalog.index([src_uri])
    catalog.add_storage(src)
    assert catalog.index([src_uri])


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
    catalog.index([ctc.src_uri], index_processor=indexer_formats["webdataset"])


def test_add_storage_error(cloud_test_catalog, cloud_type):
    catalog = cloud_test_catalog.catalog
    src_uri = cloud_test_catalog.src_uri
    if cloud_type == "file":
        src_uri += "/invalid"
    with pytest.raises(RuntimeError):
        catalog.add_storage(src_uri)


@pytest.mark.parametrize("tree", [{}], indirect=True)
def test_ls_subobjects(cloud_test_catalog):
    ctc = cloud_test_catalog
    (ctc.working_dir / "data").mkdir()
    instantiate_tree(ctc.working_dir / "data", DEFAULT_TREE)
    with (ctc.src / "animals.tar").open("wb") as f:
        with tarfile.open(fileobj=f, mode="w") as archive:
            for p in (ctc.working_dir / "data").iterdir():
                archive.add(p, p.name)
    catalog = ctc.catalog
    catalog.client_config = ctc.client_config
    catalog.index([ctc.src_uri], index_processor=indexer_formats["webdataset"])

    def do_ls(target):
        ((_, results),) = list(catalog.ls([target], fields=["name"]))
        results = list(results)
        result_set = {x[0] for x in results}
        assert len(result_set) == len(results)
        return result_set

    assert do_ls(ctc.src_uri) == {"animals.tar"}
    assert do_ls(f"{ctc.src_uri}/animals.tar") == {"animals.tar"}
    assert do_ls(f"{ctc.src_uri}/animals.tar/dogs") == {
        "dog1",
        "dog2",
        "dog3",
        "others",
    }
    assert do_ls(f"{ctc.src_uri}/animals.tar/") == {"description", "cats", "dogs"}

import asyncio
import json
import logging
import os
import os.path
import posixpath
import shutil
import sys
from contextlib import contextmanager
from dataclasses import dataclass
from itertools import islice
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple

import yaml
from dvc_data.hashfile.db.local import LocalHashFileDB
from dvc_objects.fs.local import LocalFileSystem as _LocalFileSystem
from fsspec.implementations.local import LocalFileSystem
from tqdm import tqdm

from dql.client import Client
from dql.data_storage import AbstractDataStorage
from dql.dataset import DatasetRecord, DatasetRow
from dql.dataset import Status as DatasetStatus
from dql.error import DatasetNotFoundError, PendingIndexingError
from dql.listing import Listing
from dql.node import DirType, Node, NodeWithPath
from dql.storage import Status, Storage
from dql.utils import DQLDir, FileSlice, dql_paths_join

from .datasource import DataSource
from .formats import IndexingFormat

if sys.version_info < (3, 9):
    from dql.vendored import ast
    from dql.vendored.ast import Attribute, Call, Expr, Import, Load, Name, alias
else:
    import ast
    from ast import Attribute, Call, Expr, Import, Load, Name, alias

logger = logging.getLogger("dql")

DEFAULT_DATASET_DIR = "dataset"
DATASET_FILE_SUFFIX = ".edql"

PROCESSING_BATCH_SIZE = 1000  # Batch size for inserting entries.

TTL_INT = 4 * 60 * 60


@dataclass
class NodeGroup:
    """Class for a group of nodes from the same source"""

    listing: Listing
    nodes: List[NodeWithPath]

    # The source path within the bucket
    # (not including the bucket name or s3:// prefix)
    source_path: str = ""
    updated_checksums: Optional[Dict[int, str]] = None


def check_output_dataset_file(
    output: str,
    force: bool = False,
    dataset_filename: Optional[str] = None,
    skip_check_output: bool = False,
    skip_check_edql: bool = False,
) -> str:
    """
    Checks the output directory and dataset filename for existence or if they
    should be force-overwritten.
    """
    if not skip_check_output:
        if os.path.exists(output):
            if force:
                shutil.rmtree(output)
            else:
                raise RuntimeError(f"Output directory already exists: {output}")

    dataset_file = (
        dataset_filename if dataset_filename else output + DATASET_FILE_SUFFIX
    )
    if not skip_check_edql:
        if os.path.exists(dataset_file):
            if force:
                os.remove(dataset_file)
            else:
                raise RuntimeError(
                    f"Output dataset file already exists: {dataset_file}"
                )
    return dataset_file


def parse_edql_file(filename: str) -> List[Dict[str, Any]]:
    with open(filename, encoding="utf-8") as f:
        contents = yaml.safe_load(f)

    if not isinstance(contents, list):
        contents = [contents]

    for entry in contents:
        if not isinstance(entry, dict):
            raise ValueError(
                "Failed parsing EDQL file, "
                "each data source entry must be a dictionary"
            )
        if "data-source" not in entry or "files" not in entry:
            raise ValueError(
                "Failed parsing EDQL file, "
                "each data source entry must contain the "
                '"data-source" and "files" keys'
            )

    return contents


def prepare_output_for_cp(
    node_groups: List[NodeGroup],
    output: str,
    force: bool = False,
    edql_only: bool = False,
    no_edql_file: bool = False,
) -> Tuple[bool, Optional[str]]:
    total_node_count = 0
    for node_group in node_groups:
        if not node_group.nodes:
            raise FileNotFoundError(
                f"No such file or directory: {node_group.source_path}"
            )
        total_node_count += len(node_group.nodes)

    always_copy_dir_contents = False
    copy_to_filename = None

    if edql_only:
        return always_copy_dir_contents, copy_to_filename

    if not os.path.isdir(output):
        if total_node_count == 1:
            first_node: NodeWithPath = node_groups[0].nodes[0]
            if first_node.is_dir:
                if os.path.exists(output):
                    if force:
                        os.remove(output)
                    else:
                        raise FileExistsError(f"Path already exists: {output}")
                always_copy_dir_contents = True
                os.mkdir(output)
            else:  # Is a File
                if os.path.exists(output):
                    if force:
                        os.remove(output)
                    else:
                        raise FileExistsError(f"Path already exists: {output}")
                copy_to_filename = output
        else:
            raise FileNotFoundError(f"Is not a directory: {output}")

    if copy_to_filename and not no_edql_file:
        raise RuntimeError("File to file cp not supported with .edql files!")

    return always_copy_dir_contents, copy_to_filename


def collect_nodes_for_cp(
    node_groups: Iterable[NodeGroup],
    recursive: bool = False,
) -> Tuple[int, int]:
    total_size: int = 0
    total_files: int = 0

    # Collect all nodes to process
    for node_group in node_groups:
        listing: Listing = node_group.listing
        valid_nodes: List[NodeWithPath] = []
        for node in node_group.nodes:
            if node.is_dir:
                if not recursive:
                    print(f"{node.full_path} is a directory (not copied).")
                    continue
                add_size, add_files = listing.du(node, count_files=True)
                total_size += add_size
                total_files += add_files
                valid_nodes.append(node)
            else:
                # This node is a file
                total_size += node.size
                total_files += 1
                valid_nodes.append(node)

        node_group.nodes = valid_nodes

    return total_size, total_files


def download_node_groups(
    node_groups: Iterable[NodeGroup],
    cache: LocalHashFileDB,
    bar_format: str,
    total_size: int,
    recursive: bool = False,
):
    download_progress_bar = tqdm(
        desc="Downloading files: ",
        unit="B",
        bar_format=bar_format,
        unit_scale=True,
        unit_divisor=1000,
        total=total_size,
    )

    # Download these nodes
    for node_group in node_groups:
        if not node_group.nodes:
            continue
        listing: Listing = node_group.listing

        updated_nodes: List[NodeWithPath]
        updated_nodes, updated_checksums = listing.download_nodes(
            node_group.nodes,
            cache,
            total_size,
            recursive=recursive,
            shared_progress_bar=download_progress_bar,
        )

        # This assert is hopefully not necessary, but is here mostly to
        # ensure this functionality stays consistent (and catch any bugs)
        assert len(node_group.nodes) == len(updated_nodes)

        node_group.nodes = updated_nodes
        node_group.updated_checksums = updated_checksums

    download_progress_bar.close()


def instantiate_node_groups(
    node_groups: Iterable[NodeGroup],
    cache: LocalHashFileDB,
    output: str,
    bar_format: str,
    total_files: int,
    force: bool = False,
    recursive: bool = False,
    virtual_only: bool = False,
    always_copy_dir_contents: bool = False,
    copy_to_filename: Optional[str] = None,
) -> List[Dict[str, Any]]:
    instantiate_progress_bar = (
        None
        if virtual_only
        else tqdm(
            desc=f"Instantiating {output}: ",
            unit=" f",
            bar_format=bar_format,
            unit_scale=True,
            unit_divisor=1000,
            total=total_files,
        )
    )

    metafile_data = []

    # Instantiate these nodes
    for node_group in node_groups:
        if not node_group.nodes:
            continue
        listing: Listing = node_group.listing
        source_path: str = node_group.source_path
        metafile_group = {
            "data-source": listing.storage.to_dict(source_path),
            "files": [],
        }
        output_dir = output
        if copy_to_filename:
            output_dir = os.path.dirname(output)
            if not output_dir:
                output_dir = "."
            node_group.nodes = [
                node._replace(path=[], name=os.path.basename(output))  # type: ignore [call-arg] # noqa: E501
                for node in node_group.nodes
            ]
        copy_dir_contents = always_copy_dir_contents or source_path.endswith("/")
        instantiated_nodes = listing.collect_nodes_to_instantiate(
            node_group.nodes,
            recursive,
            copy_dir_contents,
            source_path,
        )
        if node_group.updated_checksums:
            instantiated_nodes = [
                n._replace(checksum=node_group.updated_checksums.get(n.id, n.checksum))
                for n in instantiated_nodes
            ]
        if not virtual_only:
            listing.instantiate_nodes(
                instantiated_nodes,
                output_dir,
                cache,
                total_files,
                force=force,
                shared_progress_bar=instantiate_progress_bar,
            )

        for node in instantiated_nodes:
            if not node.is_dir:
                metafile_group["files"].append(node.get_metafile_data())
        if metafile_group["files"]:
            metafile_data.append(metafile_group)

    if instantiate_progress_bar:
        instantiate_progress_bar.close()

    return metafile_data


def trim_node_path(node: NodeWithPath) -> NodeWithPath:
    return node._replace(path=node.path[:-1])  # type: ignore[call-arg,attr-defined]


def find_column_to_str(
    row: Tuple[Any, ...], field_lookup: Dict[str, int], src: DataSource, column: str
) -> str:
    if column == "du":
        return str(
            src.listing.du(
                {f: row[field_lookup[f]] for f in ["dir_type", "size", "path_str"]}
            )[0]
        )
    if column == "name":
        return row[field_lookup["name"]] or ""
    if column == "owner":
        return row[field_lookup["owner_name"]] or ""
    if column == "path":
        is_dir = row[field_lookup["dir_type"]] in (DirType.DIR, DirType.ROOT)
        path_str = row[field_lookup["path_str"]]
        if is_dir and path_str:
            full_path = path_str + "/"
        else:
            full_path = path_str
        return src.get_node_full_path_from_path(full_path)
    if column == "size":
        return str(row[field_lookup["size"]])
    if column == "type":
        dt = row[field_lookup["dir_type"]]
        if dt in (DirType.DIR, DirType.ROOT):
            return "d"
        elif dt == DirType.FILE:
            return "f"
        elif dt == DirType.TAR_FILE:
            return "t"
        # Unknown - this only happens if a type was added elsewhere but not here
        return "u"
    return ""


class Catalog:
    def __init__(
        self,
        data_storage: AbstractDataStorage,
        cache_dir=None,
        tmp_dir=None,
        client_config=None,
    ):
        dql_dir = DQLDir(cache=cache_dir, tmp=tmp_dir)
        self.data_storage = data_storage
        self.cache = LocalHashFileDB(
            _LocalFileSystem(),
            dql_dir.cache,
            tmp_dir=dql_dir.tmp,
        )
        self.client_config = client_config

    def compile_query_script(self, script: str) -> str:
        code_ast = ast.parse(script)
        if code_ast.body:
            last_expr = code_ast.body[-1]
            if isinstance(last_expr, Expr):
                new_expressions = [
                    Import(names=[alias(name="dql.query.dataset", asname=None)]),
                    Expr(
                        value=Call(
                            func=Attribute(
                                value=Attribute(
                                    value=Attribute(
                                        value=Name(id="dql", ctx=Load()),
                                        attr="query",
                                        ctx=Load(),
                                    ),
                                    attr="dataset",
                                    ctx=Load(),
                                ),
                                attr="return_ds",
                                ctx=Load(),
                            ),
                            args=[last_expr],
                            keywords=[],
                        )
                    ),
                ]
                code_ast.body[-1:] = new_expressions

        return ast.unparse(code_ast)

    def add_storage(self, source: str, symlinks: bool = False) -> None:
        # pylint:disable-next=protected-access
        path = LocalFileSystem._strip_protocol(source)
        if not os.path.isdir(path):
            raise RuntimeError(f"{path} is not a directory")
        uri = Path(path).resolve().as_uri()
        print(f"Registering storage {uri}")
        self.data_storage.create_storage_if_not_registered(uri, symlinks)

    def parse_url(self, uri: str, **config: Any) -> Tuple[Client, str]:
        config = config or self.client_config or {}
        return Client.parse_url(uri, self.data_storage, **config)

    def enlist_source(
        self,
        source: str,
        ttl: int,
        force_update=False,
        skip_indexing=False,
        client_config=None,
        index_processor: Optional[IndexingFormat] = None,
    ) -> Tuple[Listing, str]:
        if force_update and skip_indexing:
            raise ValueError(
                "Both force_update and skip_indexing flags"
                " cannot be True at the same time"
            )

        client_config = client_config or self.client_config or {}
        client, path = self.parse_url(source, **client_config)
        prefix = posixpath.dirname(path)
        source_data_storage = self.data_storage.clone(uri=client.uri)

        if skip_indexing:
            source_data_storage.create_storage_if_not_registered(client.uri)
            storage = source_data_storage.get_storage(client.uri)
            return (
                Listing(storage, source_data_storage, client),
                path,
            )

        (
            storage,
            need_index,
            in_progress,
            is_new,
        ) = source_data_storage.register_storage_for_indexing(
            client.uri, force_update, prefix
        )
        if in_progress:
            raise PendingIndexingError(f"Pending indexing operation: uri={storage.uri}")

        lst = Listing(storage, source_data_storage, client)

        if not need_index:
            logger.debug(  # type: ignore[unreachable]
                f"Using cached listing {storage.uri}."
                + f" Valid till: {storage.expires_to_local}"
            )
            # Listing has to have correct version of data storage
            # initialized with correct Storage
            return lst, path

        try:
            source_data_storage.init_db(prefix, is_new)
            partial_id = source_data_storage.get_next_partial_id(prefix)
            lst.fetch(prefix, partial_id)

            # We need to validate paths to eliminate duplicate entries
            # both right after indexing regular storage files and also
            # after applying index_processor, which may create
            # subobjects, so we're always working with valid entries
            source_data_storage.validate_paths()

            # Apply index processing before marking storage as indexed.
            if index_processor:
                asyncio.run(self._apply_processor(lst, path, index_processor))

            source_data_storage.validate_paths()

            source_data_storage.mark_storage_indexed(
                storage.uri,
                Status.PARTIAL if prefix else Status.COMPLETE,
                ttl,
                prefix=prefix,
                partial_id=partial_id,
            )
        except:  # noqa: E722,B001
            source_data_storage.mark_storage_indexed(
                storage.uri, Status.FAILED, ttl, prefix=prefix
            )
            raise
        lst.storage = storage

        return lst, path

    def enlist_sources(
        self,
        sources: List[str],
        ttl: int,
        update: bool,
        skip_indexing=False,
        client_config=None,
        index_processor: Optional[IndexingFormat] = None,
    ) -> List["DataSource"]:
        enlisted_sources = []
        for src in sources:  # Opt: parallel
            listing, file_path = self.enlist_source(
                src,
                ttl,
                update,
                skip_indexing=skip_indexing,
                client_config=client_config or self.client_config,
                index_processor=index_processor,
            )
            enlisted_sources.append((listing, file_path))

        dsrc_all = []
        for listing, file_path in enlisted_sources:
            nodes = listing.expand_path(file_path)
            dir_only = file_path.endswith("/")
            for node in nodes:
                dsrc_all.append(DataSource(listing, node, dir_only))

        return dsrc_all

    @staticmethod
    def _with_path(node: Node) -> NodeWithPath:
        path_list = node.path_str.split("/") if node.path_str else []
        if not node.is_dir:
            del path_list[-1]
        return NodeWithPath(*node, path_list)  # type: ignore [call-arg]

    def enlist_sources_grouped(
        self,
        sources: List[str],
        ttl: int,
        update: bool,
        no_glob: bool = False,
        client_config=None,
    ) -> List[NodeGroup]:
        enlisted_sources: List[Tuple[bool, Any]] = []
        client_config = client_config or self.client_config or {}
        for src in sources:  # Opt: parallel
            if src.endswith(DATASET_FILE_SUFFIX) and os.path.isfile(src):
                # TODO: Also allow using EDQL files from cloud locations?
                edql_data = parse_edql_file(src)
                indexed_sources = []
                for ds in edql_data:
                    listing, source_path = self.enlist_source(
                        ds["data-source"]["uri"],
                        ttl,
                        update,
                        client_config=client_config,
                    )
                    paths = dql_paths_join(
                        source_path, (f["name"] for f in ds["files"])
                    )
                    indexed_sources.append((listing, source_path, paths))
                enlisted_sources.append((True, indexed_sources))
            else:
                listing, source_path = self.enlist_source(
                    src, ttl, update, client_config=client_config
                )
                enlisted_sources.append((False, (listing, source_path)))

        node_groups = []
        nodes: List[NodeWithPath] = []
        for is_dql, payload in enlisted_sources:  # Opt: parallel
            if is_dql:
                for listing, source_path, paths in payload:
                    nodes = [trim_node_path(listing.resolve_path(p)) for p in paths]
                    node_groups.append(NodeGroup(listing, nodes, source_path))
            else:
                listing, source_path = payload
                if no_glob:
                    nodes = [trim_node_path(listing.resolve_path(source_path))]
                else:
                    nodes = [
                        self._with_path(node)
                        for node in listing.expand_path(source_path)
                    ]
                node_groups.append(NodeGroup(listing, nodes, source_path))

        return node_groups

    def create_shadow_dataset(
        self,
        name: str,
        sources: List[str],
        client_config=None,
        recursive=False,
        populate=True,
    ) -> DatasetRecord:
        """
        Creates shadow dataset in DB if it doesn't exist and updates it with
        entries from sources.
        Example of sources:
            s3://bucket_name/dir1/dir2/*
            s3://bucket_name/*
            s3://bucket_name/image_*
        """
        client_config = client_config or self.client_config or {}
        dataset = self.data_storage.create_shadow_dataset(name, create_rows=populate)
        assert dataset
        if not populate:
            # returning empty dataset without dataset rows table and data inside
            return dataset

        final_status = DatasetStatus.FAILED
        try:
            for source in sources:
                client, path = self.parse_url(source, **client_config)
                self.data_storage.insert_into_shadow_dataset(
                    name, client.uri, path, recursive=recursive
                )
            final_status = DatasetStatus.COMPLETE
        finally:
            self.data_storage.update_dataset_status(dataset, final_status)

        return dataset

    def register_shadow_dataset(
        self,
        shadow_name: str,
        registered_name: Optional[str] = None,
        version: Optional[int] = None,
        description: Optional[str] = None,
        labels: Optional[List[str]] = None,
    ):
        """
        Method for registering shadow dataset as a new dataset with version 1, or
        as a new version of existing registered dataset
        """
        version = version or 1

        # getting shadow dataset
        shadow_dataset = self.data_storage.get_dataset(shadow_name)

        if not shadow_dataset.shadow:
            raise ValueError(f"Dataset {shadow_name} must be shadow")

        try:
            registered_dataset = (
                self.data_storage.get_dataset(registered_name)
                if registered_name
                else None
            )
        except DatasetNotFoundError:
            registered_dataset = None

        if registered_dataset:
            # if registered dataset already exists, we are creating new version
            # of it out of shadow dataset
            version = version or registered_dataset.next_version
            if not registered_dataset.is_valid_next_version(version):
                raise ValueError(
                    f"Version {version} must be higher than the current latest one"
                )

            self.data_storage.create_dataset_version(
                registered_dataset.name, version, create_rows_table=False
            )
            # to avoid re-creating rows table, we are just taking shadow one and
            # renaming it for a new version of registered one
            self.data_storage.rename_dataset_table(
                shadow_dataset.name,
                registered_dataset.name,
                old_version=None,
                new_version=version,
            )
            # finally, we are removing shadow dataset from datasets table
            self.data_storage.remove_shadow_dataset(shadow_dataset, drop_rows=False)
            return

        # if registered dataset doesn't exist we are modifying shadow dataset
        # to become registered one
        update_data = {
            "shadow": False,
            "description": description,
            "labels": labels,
        }

        if registered_name:
            update_data["name"] = registered_name

        self.data_storage.update_dataset(shadow_name, **update_data)
        self.data_storage.create_dataset_version(
            registered_name or shadow_name,
            version,
            create_rows_table=False,
        )
        self.data_storage.rename_dataset_table(
            registered_name or shadow_name,
            registered_name or shadow_name,
            old_version=None,
            new_version=version,
        )

    def get_dataset(self, name: str) -> DatasetRecord:
        return self.data_storage.get_dataset(name)

    def ls_datasets(self, shadow_only=None) -> Iterator[DatasetRecord]:
        yield from self.data_storage.list_datasets(shadow_only=shadow_only)

    def ls_dataset_rows(
        self, name: str, limit=None, version=None
    ) -> Iterator[DatasetRow]:
        dataset = self.data_storage.get_dataset(name)
        if not dataset.shadow and not version:
            raise ValueError(
                f"Missing dataset version from input for registered dataset {name}"
            )

        yield from self.data_storage.get_dataset_rows(
            name, limit=limit, version=version
        )

    def dataset_row_url(self, row: DatasetRow, client_config=None) -> str:
        client_config = client_config or {}
        client, _ = self.parse_url(row.source, **client_config)
        return client.url(row.path_str)

    def dataset_row(
        self,
        name: str,
        row_id: int,
        dataset_version: Optional[int] = None,
    ) -> Optional[DatasetRow]:
        return self.data_storage.get_dataset_row(
            name, row_id, dataset_version=dataset_version
        )

    def remove_dataset(
        self,
        name: str,
        version: Optional[int] = None,
        force: Optional[bool] = False,
    ):
        dataset = self.data_storage.get_dataset(name)
        if dataset.registered and not version and not force:
            raise ValueError(
                f"Missing dataset version from input for registered dataset {name}"
            )
        if version and not dataset.has_version(version):
            raise RuntimeError(f"Dataset {name} doesn't have version {version}")

        if dataset.registered and version:
            # removing one version of registered dataset
            self.data_storage.remove_dataset_version(dataset, version)

        elif dataset.registered and force:
            for version in dataset.versions.copy():  # type: ignore [assignment, union-attr] # noqa: E501
                self.data_storage.remove_dataset_version(
                    dataset, version.version  # type: ignore [union-attr]
                )
        else:
            self.data_storage.remove_shadow_dataset(dataset)

    def edit_dataset(
        self,
        name: str,
        new_name: Optional[str] = None,
        description: Optional[str] = None,
        labels: Optional[List[str]] = None,
    ):
        update_data = {}
        if new_name:
            update_data["name"] = new_name
        if description is not None:
            update_data["description"] = description
        if labels is not None:
            update_data["labels"] = labels  # type: ignore[assignment]

        self.data_storage.update_dataset(name, **update_data)

    def merge_datasets(
        self,
        src_name: str,
        dst_name: str,
        src_version: Optional[int] = None,
        dst_version: Optional[int] = None,
    ) -> DatasetRecord:
        """
        Merges records from source to destination dataset.
        If destination dataset is shadow, it will copy all the records from source
        dataset to shadow one
        If destination dataset is registered, it will create a new version
        of dataset with records merged from old version and the source
        """

        src = self.data_storage.get_dataset(src_name)
        dst = self.data_storage.get_dataset(dst_name)

        # validation
        if src.shadow and src_version:
            raise ValueError(
                f"Source dataset {src_name} is shadow, cannot use it with versions"
            )
        if not src.shadow and not src_version:
            raise ValueError(f"Source dataset {src_name} is registered, need a version")
        if dst.shadow and dst_version:
            raise ValueError(
                f"Dataset {dst_name} is shadow, cannot use it with versions"
            )

        if dst_version and not dst.is_valid_next_version(dst_version):
            raise ValueError(
                f"Version {dst_version} must be higher than the current latest one"
            )

        if dst.shadow:
            self.data_storage.merge_dataset_rows(
                src,
                dst,
                src_version,
                dst_version=None,
            )
        else:
            dst_version = dst_version or dst.next_version
            dst = self.data_storage.create_dataset_version(dst_name, dst_version)
            self.data_storage.merge_dataset_rows(
                src,
                dst,
                src_version,
                dst_version,
            )

        return dst

    @contextmanager
    def open_object(self, row: DatasetRow, **config: Any):
        config = config or self.client_config or {}
        client, _ = self.parse_url(row.source, **config)
        if row.dir_type == DirType.TAR_FILE:
            assert row.path_str.endswith(row.name)
            tar_path = row.path_str[: -len(row.name) - 1]
            assert row.sub_meta is not None
            offset = json.loads(row.sub_meta)["offset"]
            with client.open(tar_path) as f:
                yield FileSlice(f, offset, row.size, row.name)
        else:
            with client.open(row.path_str) as f:
                yield f

    def ls(
        self,
        sources: List[str],
        fields: Iterable[str],
        ttl=TTL_INT,
        update=False,
        skip_indexing=False,
        *,
        client_config=None,
    ) -> Iterator[Tuple[DataSource, Iterable[tuple]]]:
        data_sources = self.enlist_sources(
            sources,
            ttl,
            update,
            skip_indexing=skip_indexing,
            client_config=client_config or self.client_config,
        )

        for source in data_sources:
            yield source, source.ls(fields)

    def ls_storage_uris(self) -> Iterator[str]:
        yield from self.data_storage.get_all_storage_uris()

    def get_storage(self, uri: str) -> Storage:
        return self.data_storage.get_storage(uri)

    def ls_storages(self) -> List[Storage]:
        return self.data_storage.list_storages()

    def get(
        self,
        source,
        output,
        force=False,
        update=False,
        ttl=TTL_INT,
        *,
        client_config=None,
    ) -> None:
        listing, file_path = self.enlist_source(
            source, ttl, update, client_config=client_config or self.client_config
        )

        if not output:
            if file_path:
                output = os.path.basename(file_path.rstrip("/"))
            else:
                output = listing.storage.name

        dataset_file = check_output_dataset_file(output, force)

        node = listing.resolve_path(file_path)
        total_size, total_files = listing.du(node, count_files=True)
        listing.download_subtree(node, self.cache, total_size)
        listing.instantiate_subtree(node, output, self.cache, total_files)
        listing.metafile_for_subtree(file_path, node, dataset_file)

    def clone(
        self,
        sources: List[str],
        output: str,
        force: bool = False,
        update: bool = False,
        recursive: bool = False,
        no_glob: bool = False,
        no_cp: bool = False,
        edql: bool = False,
        edql_file: Optional[str] = None,
        ttl: int = TTL_INT,
        *,
        client_config=None,
    ) -> None:
        """
        This command takes cloud path(s) and duplicates files and folders in
        them into the dataset folder.
        It also adds those files to a shadow dataset in database, which is
        created if doesn't exist yet
        Optionally, it creates a .edql file
        """
        if not no_cp or edql:
            self.cp(
                sources,
                output,
                force=force,
                update=update,
                recursive=recursive,
                no_glob=no_glob,
                edql_only=no_cp,
                no_edql_file=not edql,
                edql_file=edql_file,
                ttl=ttl,
                client_config=client_config,
            )
        else:
            # since we don't call cp command, which does listing implicitly,
            # it needs to be done here
            self.enlist_sources(
                sources,
                ttl,
                update,
                client_config=client_config or self.client_config,
            )

        self.create_shadow_dataset(output, sources, client_config, recursive=recursive)

    def cp(
        self,
        sources: List[str],
        output: str,
        force: bool = False,
        update: bool = False,
        recursive: bool = False,
        edql_file: Optional[str] = None,
        edql_only: bool = False,
        no_edql_file: bool = False,
        no_glob: bool = False,
        ttl: int = TTL_INT,
        *,
        client_config=None,
    ) -> List[Dict[str, Any]]:
        """
        This function copies files from cloud sources to local destination directory
        If cloud source is not indexed, or has expired index, it runs indexing
        It also creates .edql file by default, if not specified differently
        """
        client_config = client_config or self.client_config or {}
        node_groups = self.enlist_sources_grouped(
            sources,
            ttl,
            update,
            no_glob,
            client_config=client_config,
        )

        always_copy_dir_contents, copy_to_filename = prepare_output_for_cp(
            node_groups, output, force, edql_only, no_edql_file
        )

        dataset_file = check_output_dataset_file(
            output, force, edql_file, True, no_edql_file
        )

        total_size, total_files = collect_nodes_for_cp(node_groups, recursive)

        if total_files == 0:
            # Nothing selected to cp
            return []

        desc_max_len = max(len(output) + 16, 19)
        bar_format = (
            "{desc:<"
            f"{desc_max_len}"
            "}{percentage:3.0f}%|{bar}| {n_fmt:>5}/{total_fmt:<5} "
            "[{elapsed}<{remaining}, {rate_fmt:>8}]"
        )

        if not edql_only:
            download_node_groups(
                node_groups, self.cache, bar_format, total_size, recursive
            )

        metafile_data = instantiate_node_groups(
            node_groups,
            self.cache,
            output,
            bar_format,
            total_files,
            force,
            recursive,
            edql_only,
            always_copy_dir_contents,
            copy_to_filename,
        )

        if not metafile_data or no_edql_file:
            # Don't write the metafile if nothing was copied (or skipped)
            return metafile_data

        print(f"Creating '{dataset_file}'")
        with open(dataset_file, "w", encoding="utf-8") as fd:
            yaml.dump(metafile_data, fd, sort_keys=False)

        return metafile_data

    def du(
        self,
        sources,
        depth=0,
        ttl=TTL_INT,
        update=False,
        *,
        client_config=None,
    ) -> Iterable[Tuple[str, float]]:
        sources = self.enlist_sources(
            sources,
            ttl,
            update,
            client_config=client_config or self.client_config,
        )

        def du_dirs(src, node, subdepth):
            if subdepth > 0:
                subdirs = src.listing.data_storage.get_nodes_by_parent_id(
                    node.id, type="dir"
                )
                for sd in subdirs:
                    yield from du_dirs(src, sd, subdepth - 1)
            path_str = node.path_str
            if node.is_dir:
                path_str = posixpath.join(path_str, "")
            yield (
                src.get_node_full_path_from_path(path_str),
                src.listing.du(node)[0],
            )

        for src in sources:
            yield from du_dirs(src, src.node, depth)

    def find(
        self,
        sources,
        ttl=TTL_INT,
        update=False,
        names=None,
        inames=None,
        paths=None,
        ipaths=None,
        size=None,
        typ=None,
        jmespath=None,
        columns=None,
        *,
        client_config=None,
    ) -> Iterator[str]:
        sources = self.enlist_sources(
            sources,
            ttl,
            update,
            client_config=client_config or self.client_config,
        )
        if not columns:
            columns = ["path"]
        field_set = set()
        for column in columns:
            if column == "du":
                field_set.add("dir_type")
                field_set.add("size")
                field_set.add("path_str")
            elif column == "name":
                field_set.add("name")
            elif column == "owner":
                field_set.add("owner_name")
            elif column == "path":
                field_set.add("dir_type")
                field_set.add("path_str")
            elif column == "size":
                field_set.add("size")
            elif column == "type":
                field_set.add("dir_type")
        fields = list(field_set)
        field_lookup = {f: i for i, f in enumerate(fields)}
        for src in sources:
            results = src.listing.find(
                src.node, fields, names, inames, paths, ipaths, size, typ, jmespath
            )
            for row in results:
                yield "\t".join(
                    find_column_to_str(row, field_lookup, src, column)
                    for column in columns
                )

    def index(
        self,
        sources,
        ttl=TTL_INT,
        update=False,
        *,
        client_config=None,
        index_processor: Optional[IndexingFormat] = None,
    ) -> List["DataSource"]:
        root_sources = [
            src for src in sources if Client.get_implementation(src).is_root_url(src)
        ]
        non_root_sources = [
            src
            for src in sources
            if not Client.get_implementation(src).is_root_url(src)
        ]

        client_config = client_config or self.client_config or {}

        # for root sources (e.g s3://) we are just getting all buckets and
        # saving them as storages, without further indexing in each bucket
        for source in root_sources:
            for bucket in Client.get_implementation(source).ls_buckets(**client_config):
                client, _ = self.parse_url(bucket.uri, **client_config)
                print(f"Registering storage {client.uri}")
                self.data_storage.create_storage_if_not_registered(client.uri)

        sources = self.enlist_sources(
            non_root_sources,
            ttl,
            update,
            client_config=client_config,
            index_processor=index_processor,
        )

        return sources

    def find_stale_storages(self) -> None:
        self.data_storage.find_stale_storages()

    async def _apply_processor(
        self, listing: "Listing", path: str, processor: IndexingFormat
    ):
        with tqdm(desc="Processing", unit=" objects") as pbar:
            listing = listing.clone()
            for entry in processor.filter(listing, path):
                subentries = processor.process(listing, entry)
                for batch in _batch(subentries, PROCESSING_BATCH_SIZE):
                    pbar.update(len(batch))
                    await listing.data_storage.insert_entries(batch)


def _batch(it, size):
    while batch := list(islice(it, size)):
        yield batch

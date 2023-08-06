import os
from collections import defaultdict
from itertools import zip_longest
from typing import DefaultDict, List

import yaml
from fsspec.asyn import get_loop, sync
from sqlalchemy.sql import func
from tqdm import tqdm

from dql.client import Client
from dql.data_storage import AbstractDataStorage
from dql.node import DirType, Node, NodeWithPath
from dql.storage import Storage
from dql.utils import suffix_to_number


def check_checksums(nodes):
    for node in nodes:
        if node.name and not node.checksum:
            raise ValueError(f"Instantiation Error: Missing checksum for node: {node}")


class Listing:
    def __init__(
        self,
        storage: Storage,
        data_storage: AbstractDataStorage,
        client: Client,
    ):
        self.storage = storage
        self.data_storage = data_storage
        self.client = client

    def clone(self) -> "Listing":
        return Listing(
            self.storage, self.data_storage.clone(self.client.uri), self.client
        )

    @property
    def id(self):
        return self.storage.id

    def fetch(self, start_prefix="", partial_id=0):
        sync(get_loop(), self.client.fetch, self, start_prefix, partial_id)

    @staticmethod
    async def _insert_dir(data_storage, parent_id, name, time, path, partial_id):
        return await data_storage.insert_entry(
            {
                "is_dir": True,
                "parent_id": parent_id,
                "path": path,
                "name": name,
                "last_modified": time,
                "checksum": "",
                "etag": "",
                "version": "",
                "is_latest": True,
                "size": 0,
                "owner_name": "",
                "owner_id": "",
                "partial_id": partial_id,
            },
        )

    async def insert_dir(
        self, parent_id, name, time, path, partial_id, data_storage=None
    ):
        return await Listing._insert_dir(
            data_storage or self.data_storage,
            parent_id,
            name,
            time,
            path,
            partial_id,
        )

    async def insert_file(self, parent_id, name, time, path_str, partial_id):
        node = Node(
            0,
            DirType.FILE,
            parent_id,
            name,
            last_modified=time,
            path_str=path_str,
        )
        await self.insert_file_from_node(node, partial_id)

    async def insert_file_from_node(self, node, partial_id):
        await self.data_storage.insert_entry(
            {**node._asdict(), "is_dir": False, "partial_id": partial_id}
        )

    async def insert_root(self, data_storage=None) -> int:
        return await (data_storage or self.data_storage).insert_root()

    def expand_path(self, path) -> List[Node]:
        return self.data_storage.expand_path(path)

    def resolve_path(self, path) -> NodeWithPath:
        return self.data_storage.get_node_by_path(path)

    def ls_path(self, node, fields):
        if node.dir_type in (DirType.TAR_DIR, DirType.TAR_ARCHIVE):
            return self.data_storage.select_node_fields_by_parent_path(
                node.path_str, fields
            )
        return self.data_storage.select_node_fields_by_parent_id(node.id, fields)

    def metafile_for_subtree(
        self,
        file_path,
        node,
        dataset_file,
    ):
        nodes = self.data_storage.walk_subtree(node, sort="size desc")

        print(f"Creating '{dataset_file}'")

        with open(dataset_file, "w", encoding="utf-8") as fd:
            yaml.dump(
                {
                    "data-source": self.storage.to_dict(file_path),
                },
                fd,
                sort_keys=False,
            )

            fd.write("files:\n")

            for node in nodes:
                if not node.is_dir:
                    node.append_to_file(fd)

    def collect_nodes_to_instantiate(
        self,
        nodes,
        recursive=False,
        copy_dir_contents=False,
        relative_path=None,
    ):
        rel_path_elements = relative_path.split("/") if relative_path else []
        all_nodes = []
        for node in nodes:
            node_path = []
            for rpe, npe in zip_longest(rel_path_elements, node.path):
                if rpe == npe:
                    continue
                if npe:
                    node_path.append(npe)
            if recursive and node.is_dir:
                dir_path = node_path[:-1]
                if not copy_dir_contents:
                    dir_path.append(node.name)
                subtree_nodes = self.data_storage.walk_subtree(
                    node,
                    sort=["parent_id", "path_str"],
                    type="files",
                )
                all_nodes.extend(
                    n._replace(path=dir_path + n.path) for n in subtree_nodes
                )
            else:
                all_nodes.append(node._replace(path=node_path + [node.name]))
        return all_nodes

    def instantiate_nodes(
        self,
        all_nodes,
        output,
        cache,
        total_files=None,
        force=False,
        shared_progress_bar=None,
    ):
        check_checksums(all_nodes)
        nodes = iter(all_nodes)

        progress_bar = shared_progress_bar or tqdm(
            desc=f"Instantiating '{output}'",
            unit=" files",
            unit_scale=True,
            unit_divisor=1000,
            total=total_files,
        )

        os.makedirs(output, exist_ok=True)
        node = next(nodes, None)
        counter = 0
        while node:
            curr_dir_path = node.path[:-1]
            curr_dir_path_str = os.path.join(output, *curr_dir_path)
            curr_parent_id = node.parent_id

            os.makedirs(curr_dir_path_str, exist_ok=True)

            while node and node.parent_id == curr_parent_id:
                self.client.instantiate_node(node, cache, output, progress_bar, force)
                counter += 1
                if counter > 1000:
                    progress_bar.update(counter)
                    counter = 0
                node = next(nodes, None)

        progress_bar.update(counter)

    def instantiate_subtree(self, node, output, cache, total_files=None):
        nodes = self.collect_nodes_to_instantiate(
            [node], recursive=True, copy_dir_contents=True
        )
        self.instantiate_nodes(nodes, output, cache, total_files)

    def download_nodes(
        self,
        nodes,
        cache,
        total_size=None,
        recursive=False,
        shared_progress_bar=None,
    ):
        nodes_by_path: DefaultDict[str, List] = defaultdict(list)
        for node in nodes:
            node_path = "/".join(node.path)
            if recursive and node.is_dir:
                nodes_by_path[node_path].extend(
                    self.data_storage.walk_subtree(node, sort="size desc")
                )
            else:
                nodes_by_path[node_path].append(node._replace(path=[node.name]))

        updated_node_lookup = {}
        for group_path, all_nodes in nodes_by_path.items():
            updated_nodes = self.client.fetch_nodes(
                group_path,
                iter(all_nodes),
                cache,
                self.data_storage,
                total_size,
                shared_progress_bar=shared_progress_bar,
            )
            # This assert is hopefully not necessary, but is here mostly to
            # ensure this functionality stays consistent (and catch any bugs)
            assert len(updated_nodes) <= len(all_nodes)

            if group_path:
                group_path_elements = group_path.strip("/").split("/")
            else:
                group_path_elements = []
            for node in updated_nodes:
                updated_node_lookup[node.id] = node._replace(path=group_path_elements)

        # Since nodes can have updated information (such as checksums)
        # after they are downloaded
        updated_nodes = []
        for node in nodes:
            if node.id in updated_node_lookup:
                # Node has updated information
                updated_nodes.append(updated_node_lookup[node.id])
            else:
                # No updates
                updated_nodes.append(node)

        return updated_nodes, {i: n.checksum for i, n in updated_node_lookup.items()}

    def download_subtree(
        self,
        node,
        cache,
        total_size=None,
    ):
        return self.download_nodes([node], cache, total_size, recursive=True)

    def find(
        self,
        node,
        fields,
        names=None,
        inames=None,
        paths=None,
        ipaths=None,
        size=None,
        type=None,  # pylint: disable=redefined-builtin
        jmespath=None,
    ):
        n = self.data_storage.nodes
        glob_op = self.data_storage.glob_op
        compile_glob = self.data_storage.compile_glob
        conds = []
        if names:
            for name in names:
                conds.append(n.c.name.op(glob_op)(compile_glob(name)))
        if inames:
            for iname in inames:
                conds.append(
                    func.lower(n.c.name).op(glob_op)(compile_glob(iname.lower()))
                )
        if paths:
            for path in paths:
                conds.append(n.c.path_str.op(glob_op)(compile_glob(path)))
        if ipaths:
            for ipath in ipaths:
                conds.append(
                    func.lower(n.c.path_str).op(glob_op)(compile_glob(ipath.lower()))
                )

        if size is not None:
            size_limit = suffix_to_number(size)
            if size_limit >= 0:
                conds.append(n.c.size >= size_limit)
            else:
                conds.append(n.c.size <= -size_limit)

        return self.data_storage.find(
            node, fields, jmespath=jmespath, type=type, conds=conds
        )

    def du(self, node, count_files: bool = False):
        return self.data_storage.size(node, count_files)

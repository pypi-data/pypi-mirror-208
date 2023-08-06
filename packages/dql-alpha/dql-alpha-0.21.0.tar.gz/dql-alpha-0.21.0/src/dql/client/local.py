import os
import posixpath
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple

from fsspec.implementations.local import LocalFileSystem

from dql.data_storage import AbstractDataStorage
from dql.error import StorageNotFoundError
from dql.nodes_fetcher import NodesFetcher

from .checksum import file_digest
from .fsspec import FSSpecClient


class FileClient(FSSpecClient):
    FS_CLASS = LocalFileSystem
    PREFIX = "file://"
    protocol = "file"

    def __init__(
        self, name: str, fs: LocalFileSystem, use_symlinks: bool = False
    ) -> None:
        super().__init__(name, fs)
        self.use_symlinks = use_symlinks

    def url(self, path: str, expires: int = 3600) -> str:
        raise TypeError("Signed urls are not implemented for local file system")

    @classmethod
    def ls_buckets(cls, **kwargs):
        return []

    @classmethod
    def split_url(cls, url: str, data_storage) -> Tuple[str, str]:
        # pylint:disable=protected-access
        def _storage_exists(uri: str) -> bool:
            try:
                data_storage.get_storage(uri)
            except StorageNotFoundError:
                return False
            return True

        # lowercasing scheme just in case it's uppercase
        scheme, rest = url.split(":", 1)
        url = f"{scheme.lower()}:{rest}"
        if _storage_exists(url):
            return LocalFileSystem._strip_protocol(url), ""
        for pos in range(len(url) - 1, len(cls.PREFIX), -1):
            if url[pos] == "/" and _storage_exists(url[:pos]):
                return LocalFileSystem._strip_protocol(url[:pos]), url[pos + 1 :]
        raise RuntimeError(f"Invalid file path '{url}'")

    @classmethod
    def from_url(cls, url: str, data_storage, kwargs):
        result = cls(url, cls.create_fs(**kwargs))
        storage = data_storage.get_storage(result.uri)
        result.use_symlinks = storage.symlinks
        return result

    async def ls_dir(self, path):
        return self.fs.ls(path, detail=True)

    def rel_path(self, path):
        return posixpath.relpath(path, self.name)

    @property
    def uri(self):
        return Path(self.name).as_uri()

    def get_full_path(self, rel_path):
        full_path = Path(self.name, rel_path).as_uri()
        if rel_path.endswith("/") or not rel_path:
            full_path += "/"
        return full_path

    def _dict_from_info(self, v, parent_id, path, partial_id):
        name = posixpath.basename(path)
        return {
            "dir_id": None,
            "parent_id": parent_id,
            "path": self.rel_path(v["name"]),
            "name": name,
            "checksum": "",
            "etag": "",
            "version": "",
            "is_latest": True,
            "last_modified": datetime.fromtimestamp(v["mtime"], timezone.utc),
            "size": v.get("size", ""),
            "owner_name": "",
            "owner_id": "",
            "anno": None,
            "partial_id": partial_id,
        }

    def fetch_nodes(
        self,
        file_path,
        nodes,
        cache,
        data_storage: AbstractDataStorage,
        total_size=None,
        cls=NodesFetcher,
        pb_descr="Download",
        shared_progress_bar=None,
    ):
        if self.use_symlinks:
            return self._fetch_symlinks(nodes, data_storage)
        else:
            return super().fetch_nodes(
                file_path,
                nodes,
                cache,
                data_storage,
                total_size,
                cls,
                pb_descr,
                shared_progress_bar,
            )

    def _fetch_symlinks(self, nodes, data_storage):
        updated_nodes = []
        for node in nodes:
            if not node.is_downloadable:
                continue
            src_path = f"{self.name}/{node.path_str}"
            with open(src_path, "rb") as fileobj:
                md5_hash = file_digest(fileobj)
            data_storage.update_checksum(node, md5_hash)
            updated_nodes.append(node._replace(checksum=md5_hash))
        return updated_nodes

    def do_instantiate_node(self, node, cache, dst):
        if self.use_symlinks:
            os.symlink(Path(self.name, node.path_str), dst)
        else:
            super().do_instantiate_node(node, cache, dst)

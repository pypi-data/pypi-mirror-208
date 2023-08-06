import asyncio
import multiprocessing
import os
import posixpath
from abc import abstractmethod
from datetime import datetime, timezone
from shutil import copy2
from typing import TYPE_CHECKING, Any, ClassVar, Iterator, Tuple, Type

from botocore.exceptions import ClientError
from dvc_data.hashfile.db.local import LocalHashFileDB
from fsspec.asyn import get_loop
from reflink import reflink
from reflink.error import ReflinkImpossibleError
from tqdm import tqdm

from dql.client.base import Bucket, Client
from dql.data_storage import AbstractDataStorage
from dql.nodes_fetcher import NodesFetcher
from dql.nodes_thread_pool import NodeChunk

if TYPE_CHECKING:
    from fsspec.spec import AbstractFileSystem

    from dql.node import NodeWithPath

FETCH_WORKERS = 100
DELIMITER = "/"  # Path delimiter.
TIME_ZERO = datetime.fromtimestamp(0, tz=timezone.utc)


class FSSpecClient(Client):
    MAX_THREADS = multiprocessing.cpu_count()
    FS_CLASS: ClassVar[Type["AbstractFileSystem"]]
    PREFIX: ClassVar[str]

    def __init__(self, name: str, fs: "AbstractFileSystem") -> None:
        self.name = name
        self.fs = fs

    @classmethod
    def create_fs(cls, **kwargs) -> "AbstractFileSystem":
        kwargs.setdefault("version_aware", True)
        fs = cls.FS_CLASS(**kwargs)
        fs.invalidate_cache()
        return fs

    @classmethod
    def from_url(cls, url: str, data_storage, kwargs):
        return cls(url, cls.create_fs(**kwargs))

    @classmethod
    def ls_buckets(cls, **kwargs) -> Iterator[Bucket]:
        for entry in cls.create_fs(**kwargs).ls(cls.PREFIX, detail=True):
            name = entry["name"].rstrip("/")
            yield Bucket(
                name=name,
                uri=f"{cls.PREFIX}{name}",
                created=entry.get("CreationDate"),
            )

    @classmethod
    def is_root_url(cls, url) -> bool:
        return url == cls.PREFIX

    @property
    def uri(self):
        return f"{self.PREFIX}{self.name}"

    @classmethod
    def split_url(cls, url: str, data_storage) -> Tuple[str, str]:
        fill_path = url[len(cls.PREFIX) :]
        path_split = fill_path.split("/", 1)
        bucket = path_split[0]
        path = path_split[1] if len(path_split) > 1 else ""
        return bucket, path

    async def fetch(self, listing, start_prefix="", partial_id=0):
        data_storage = listing.data_storage.clone()
        if start_prefix:
            start_prefix = start_prefix.rstrip("/")
            start_id = await listing.insert_dir(
                None,
                posixpath.basename(start_prefix),
                TIME_ZERO,
                start_prefix,
                partial_id,
                data_storage=data_storage,
            )
        else:
            start_id = await listing.insert_root(data_storage=data_storage)

        progress_bar = tqdm(desc=f"Listing {self.uri}", unit=" objects")
        loop = get_loop()

        queue = asyncio.Queue()
        queue.put_nowait((start_id, start_prefix))

        async def worker(queue, data_storage):
            while True:
                dir_id, prefix = await queue.get()
                try:
                    subdirs = await self._fetch_dir(
                        dir_id,
                        prefix,
                        progress_bar,
                        listing,
                        data_storage,
                        partial_id,
                    )
                    for subdir in subdirs:
                        queue.put_nowait(subdir)
                finally:
                    queue.task_done()

        try:
            workers = []
            for _ in range(FETCH_WORKERS):
                workers.append(loop.create_task(worker(queue, data_storage)))

            await queue.join()
            for worker in workers:
                worker.cancel()
            await asyncio.gather(*workers)
        except ClientError as exc:
            raise RuntimeError(
                exc.response.get("Error", {}).get("Message") or exc
            ) from exc
        finally:
            data_storage.inserts_done()
            # This ensures the progress bar is closed before any exceptions are raised
            progress_bar.close()

    async def _fetch_dir(self, dir_id, prefix, pbar, listing, data_storage, partial_id):
        path = f"{self.name}/{prefix}"
        infos = await self.ls_dir(path)
        files = []
        subdirs = set()
        for info in infos:
            full_path = info["name"]
            subprefix = self.rel_path(full_path)
            if info["type"] == "directory":
                name = full_path.split(DELIMITER)[-1]
                new_dir_id = await listing.insert_dir(
                    dir_id,
                    name,
                    TIME_ZERO,
                    subprefix,
                    partial_id,
                    data_storage=data_storage,
                )
                subdirs.add((new_dir_id, subprefix))
            else:
                files.append(self._dict_from_info(info, dir_id, subprefix, partial_id))
        if files:
            await data_storage.insert_entries(files)
            await data_storage.update_last_inserted_at()
        pbar.update(len(subdirs) + len(files))
        return subdirs

    async def ls_dir(self, path):
        # pylint:disable-next=protected-access
        return await self.fs._ls(path, detail=True, versions=True)

    def rel_path(self, path):
        return self.fs.split_path(path)[1]

    def get_full_path(self, rel_path):
        return f"{self.PREFIX}{self.name}/{rel_path}"

    @abstractmethod
    def _dict_from_info(self, v, parent_id, path, partial_id):
        ...

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
        fetcher = cls(
            self,
            data_storage,
            file_path,
            self.MAX_THREADS,
            cache,
        )

        chunk_gen = NodeChunk(nodes)
        target_name = self.visual_file_name(file_path)
        pb_descr = f"{pb_descr} {target_name}"
        return fetcher.run(chunk_gen, pb_descr, total_size, shared_progress_bar)

    def iter_object_chunks(self, bucket, path, version=None):
        with self.fs.open(f"{bucket}/{path}", version_id=version) as f:
            chunk = f.read()
            while chunk:
                yield chunk
                chunk = f.read()

    @staticmethod
    def visual_file_name(file_path):
        target_name = file_path.rstrip("/").split("/")[-1]
        max_len = 25
        if len(target_name) > max_len:
            target_name = "..." + target_name[max_len - 3 :]
        return target_name

    def instantiate_node(
        self,
        node: "NodeWithPath",
        cache: LocalHashFileDB,
        output: str,
        progress_bar: tqdm,
        force: bool = False,
    ) -> None:
        if not node.name:
            return
        dst = os.path.join(output, *node.path)  # type: ignore[attr-defined]
        if os.path.exists(dst):
            if force:
                os.remove(dst)
            else:
                progress_bar.close()
                raise FileExistsError(f"Path {dst} already exists")
        self.do_instantiate_node(node, cache, dst)

    def do_instantiate_node(
        self, node: "NodeWithPath", cache: LocalHashFileDB, dst: str
    ) -> None:
        src = cache.oid_to_path(node.checksum)  # type: ignore[attr-defined]
        try:
            reflink(src, dst)
        except (NotImplementedError, ReflinkImpossibleError):
            # Default to copy if reflinks are not supported
            copy2(src, dst)

    def open(self, path: str, mode="rb") -> Any:
        return self.fs.open(self.get_full_path(path), mode=mode)

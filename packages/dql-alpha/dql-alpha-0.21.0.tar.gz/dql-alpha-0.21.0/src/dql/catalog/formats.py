import json
import os
import tarfile
import tempfile
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, Iterator, Tuple

from dql.node import DirType

if TYPE_CHECKING:
    from dql.listing import Listing


class IndexingFormat(ABC):
    """
    Indexing formats allow additional transformations on indexed
    objects, such as listing contents of archives.
    """

    @abstractmethod
    def filter(self, listing: "Listing", path: str) -> Iterator[Tuple[Any, ...]]:
        """Create a list of entries to process"""

    @abstractmethod
    def process(self, listing, entry):
        """Process an entry and return additional entries to store."""


class Webdataset(IndexingFormat):
    """
    Webdataset indexes buckets containing uncompressed tar archives. The contents of
    the archives is indexed as well.
    """

    def filter(self, listing: "Listing", path: str) -> Iterator[Tuple[Any, ...]]:
        for node in listing.expand_path(path):
            found = listing.find(
                node,
                ["path_str", "id", "is_latest", "partial_id"],
                names=["*.tar"],
            )
            yield from found

    def process(self, listing: "Listing", entry):
        pth, parent_id, is_latest, partial_id = entry
        local_path = tempfile.gettempdir() + f"/dql_cache_{parent_id}"
        client = listing.client
        # Download tarball to local storage first.
        client.fs.get_file(client.get_full_path(pth), local_path)
        with tarfile.open(name=local_path, mode="r") as tar:
            for info in tar:
                if info.isdir():
                    yield self.tardir_from_info(
                        info, parent_id, pth, is_latest, partial_id
                    )
                elif info.isfile():
                    yield self.tarmember_from_info(
                        info, parent_id, pth, is_latest, partial_id
                    )
        os.remove(local_path)
        listing.data_storage.update_type(parent_id, DirType.TAR_ARCHIVE)

    def tarmember_from_info(self, info, parent_id, path_str, is_latest, partial_id):
        sub_meta = json.dumps({"offset": info.offset_data})
        return {
            "dir_type": DirType.TAR_FILE,
            "parent_id": parent_id,
            "path_str": f"{path_str}/{info.name}",
            "name": info.name,
            "checksum": "",
            "etag": "",
            "version": "",
            "is_latest": is_latest,
            "last_modified": datetime.fromtimestamp(info.mtime, timezone.utc),
            "size": info.size,
            "owner_name": info.uname,
            "owner_id": info.uid,
            "sub_meta": sub_meta,
            "partial_id": partial_id,
        }

    def tardir_from_info(self, info, parent_id, path_str, is_latest, partial_id):
        return {
            "dir_type": DirType.TAR_DIR,
            "parent_id": parent_id,
            "path_str": f"{path_str}/{info.name.rstrip('/')}",
            "name": info.name,
            "checksum": "",
            "etag": "",
            "version": "",
            "is_latest": is_latest,
            "last_modified": datetime.fromtimestamp(info.mtime, timezone.utc),
            "size": info.size,
            "owner_name": info.uname,
            "owner_id": info.uid,
            "partial_id": partial_id,
        }


indexer_formats: Dict[str, IndexingFormat] = {
    "webdataset": Webdataset(),
}

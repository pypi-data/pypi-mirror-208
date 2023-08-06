import json
import tarfile
from datetime import datetime, timezone
from random import getrandbits
from typing import TYPE_CHECKING, Any

from sqlalchemy import String

from dql.catalog import Catalog
from dql.client.checksum import file_digest
from dql.data_storage.abstract import RANDOM_BITS
from dql.node import DirType

from .udf import generator

if TYPE_CHECKING:
    from dql.dataset import DatasetRow


__all__ = ["index_tar", "checksum"]


def tarmember_from_info(info, parent):
    sub_meta = json.dumps({"offset": info.offset_data})
    return {
        "dir_type": DirType.TAR_FILE,
        "parent_id": parent.id,
        "path_str": f"{parent.path_str}/{info.name}",
        "name": info.name,
        "checksum": "",
        "etag": "",
        "version": "",
        "is_latest": parent.is_latest,
        "last_modified": datetime.fromtimestamp(info.mtime, timezone.utc),
        "size": info.size,
        "owner_name": info.uname,
        "owner_id": info.uid,
        "anno": None,
        "source": parent.source,
        "random": getrandbits(RANDOM_BITS),
        "sub_meta": sub_meta,
    }


@generator(Catalog)
def index_tar(row, catalog):
    with catalog.open_object(row) as f:
        with tarfile.open(fileobj=f, mode="r:") as archive:
            for info in archive:
                if info.isdir():
                    continue
                yield tarmember_from_info(info, parent=row)


class ChecksumFunc:
    """Calculate checksums for objects reference by dataset rows."""

    output_type = String

    column = "checksum"

    def __init__(self):
        pass

    def __call__(self, catalog: "Catalog", row: "DatasetRow") -> Any:
        with catalog.open_object(row) as f:
            return file_digest(f)


checksum = ChecksumFunc()

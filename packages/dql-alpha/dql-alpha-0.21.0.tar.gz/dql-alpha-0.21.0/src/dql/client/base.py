from abc import ABC, abstractmethod
from datetime import datetime
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Dict,
    Iterator,
    NamedTuple,
    Optional,
    Tuple,
    Type,
)

if TYPE_CHECKING:
    from fsspec.spec import AbstractFileSystem

    from dql.data_storage import AbstractDataStorage


class Bucket(NamedTuple):
    name: str
    uri: str
    created: Optional[datetime]


class Client(ABC):
    name: str
    protocol: ClassVar[str]
    fs: "AbstractFileSystem"

    @staticmethod
    def get_implementation(url: str) -> Type["Client"]:
        from .azure import AzureClient
        from .gcs import GCSClient
        from .local import FileClient
        from .s3 import ClientS3

        if url.lower().startswith(ClientS3.PREFIX):
            return ClientS3
        elif url.lower().startswith(GCSClient.PREFIX):
            return GCSClient
        elif url.lower().startswith(AzureClient.PREFIX):
            return AzureClient
        elif url.lower().startswith(FileClient.PREFIX):
            return FileClient
        raise RuntimeError(f"Unsupported data source format '{url}'")

    @staticmethod
    def parse_url(
        source: str, data_storage: "AbstractDataStorage", **kwargs
    ) -> Tuple["Client", str]:
        cls = Client.get_implementation(source)
        storage_url, rel_path = cls.split_url(source, data_storage)
        client = cls.from_url(storage_url, data_storage, kwargs)
        return client, rel_path

    @classmethod
    @abstractmethod
    def from_url(
        cls, url: str, data_storage: "AbstractDataStorage", kwargs: Dict[str, Any]
    ) -> "Client":
        ...

    @classmethod
    @abstractmethod
    def is_root_url(cls, url) -> bool:
        ...

    @classmethod
    @abstractmethod
    def split_url(
        cls, url: str, data_storage: "AbstractDataStorage"
    ) -> Tuple[str, str]:
        ...

    @classmethod
    @abstractmethod
    def ls_buckets(cls, **kwargs) -> Iterator[Bucket]:
        ...

    @property
    @abstractmethod
    def uri(self) -> str:
        ...

    @abstractmethod
    def url(self, path: str, expires: int = 3600) -> str:
        ...

    @abstractmethod
    def open(self, path: str, mode="rb") -> Any:
        ...

    @abstractmethod
    def get_full_path(self, rel_path) -> str:
        ...

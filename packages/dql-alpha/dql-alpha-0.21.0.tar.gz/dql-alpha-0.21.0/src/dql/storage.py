import posixpath
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from functools import cached_property
from typing import NamedTuple, Optional, Union
from urllib.parse import urlparse

from dql.utils import is_expired, time_to_local_str, time_to_str

STALE_HOURS_LIMIT = 4


class Status:
    CREATED = 1
    PENDING = 2
    FAILED = 3
    COMPLETE = 4
    PARTIAL = 5
    STALE = 6


class AbstractStorage(ABC):
    @property
    @abstractmethod
    def uri(self) -> str:
        ...

    @property
    @abstractmethod
    def timestamp(self) -> Optional[Union[datetime, str]]:
        ...

    @property
    @abstractmethod
    def expires(self) -> Optional[Union[datetime, str]]:
        ...

    @property
    @abstractmethod
    def status(self) -> int:
        ...

    @property
    def type(self):
        return self._parsed_uri.scheme

    @property
    def name(self):
        return self._parsed_uri.netloc

    @cached_property
    def _parsed_uri(self):
        return urlparse(self.uri)


class StorageRecord(NamedTuple):
    id: int
    uri: str
    timestamp: Optional[Union[datetime, str]] = None
    expires: Optional[Union[datetime, str]] = None
    started_inserting_at: Optional[Union[datetime, str]] = None
    last_inserted_at: Optional[Union[datetime, str]] = None
    status: int = Status.CREATED
    symlinks: bool = False


class Storage(StorageRecord, AbstractStorage):
    @property
    def is_indexed(self) -> bool:
        return self.status == Status.COMPLETE

    @property
    def is_expired(self) -> bool:
        return is_expired(self.expires)

    @property
    def is_pending(self) -> bool:
        return self.status == Status.PENDING

    @property
    def is_stale(self) -> bool:
        limit = datetime.now(timezone.utc) - timedelta(hours=STALE_HOURS_LIMIT)
        date_to_check = self.last_inserted_at or self.started_inserting_at

        return self.is_pending and date_to_check < limit  # type: ignore [operator]

    @property
    def need_indexing(self) -> bool:
        return self.is_expired or not self.is_indexed

    @property
    def timestamp_str(self) -> Optional[str]:
        if not self.timestamp:
            return None
        return time_to_str(self.timestamp)

    @property
    def timestamp_to_local(self) -> Optional[str]:
        if not self.timestamp:
            return None
        return time_to_local_str(self.timestamp)

    @property
    def expires_to_local(self) -> Optional[str]:
        if not self.expires:
            return None
        return time_to_local_str(self.expires)

    @staticmethod
    def get_expiration_time(timestamp: datetime, ttl: int):
        if ttl >= 0:
            try:
                return timestamp + timedelta(seconds=ttl)
            except OverflowError:
                return datetime.max
        else:
            return datetime.max

    def to_dict(self, file_path=""):
        uri = self.uri
        if file_path:
            uri = posixpath.join(uri, *file_path.rstrip("/").split("/"))
        return {
            "uri": uri,
            "timestamp": time_to_str(self.timestamp) if self.timestamp else None,
            "expires": time_to_str(self.expires) if self.expires else None,
        }

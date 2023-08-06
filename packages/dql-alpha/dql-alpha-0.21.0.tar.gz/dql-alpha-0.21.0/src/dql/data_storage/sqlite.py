import logging
import os
import posixpath
import sqlite3
from datetime import MAXYEAR, MINYEAR, datetime, timezone
from functools import wraps
from time import sleep
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterable,
    Iterator,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Union,
)

import sqlalchemy
from sqlalchemy import MetaData, Table, UniqueConstraint, select, update
from sqlalchemy.dialects import sqlite
from sqlalchemy.schema import CreateTable, DropTable
from sqlalchemy.sql.expression import bindparam, true

from dql.data_storage.abstract import AbstractDataStorage
from dql.data_storage.schema import DefaultSchema
from dql.dataset import DATASET_CORE_COLUMN_NAMES, DatasetRecord
from dql.dataset import Status as DatasetStatus
from dql.dataset import dataset_table
from dql.error import DQLError
from dql.storage import Status as StorageStatus
from dql.storage import Storage
from dql.utils import DQLDir

if TYPE_CHECKING:
    from sqlalchemy.schema import SchemaItem
    from sqlalchemy.sql.elements import ColumnClause, CompilerElement, TextClause

logger = logging.getLogger("dql")

RETRY_START_SEC = 0.01
RETRY_MAX_TIMES = 10
RETRY_FACTOR = 2

Column = Union[str, "ColumnClause[Any]", "TextClause"]

# sqlite 3.31.1 is the earliest version tested in CI
if sqlite3.sqlite_version_info < (3, 31, 1):
    logger.warning(
        "Possible sqlite incompatibility. The earliest tested version of "
        f"sqlite is 3.31.1 but you have {sqlite3.sqlite_version}"
    )


sqlite_dialect = sqlite.dialect(paramstyle="named")
quote_schema = sqlite_dialect.identifier_preparer.quote_schema


def compile_statement(
    statement: "CompilerElement",
) -> Union[Tuple[str], Tuple[str, Dict[str, Any]]]:
    # render_postcompile is needed for in_ queries to work
    compiled = statement.compile(
        dialect=sqlite_dialect, compile_kwargs={"render_postcompile": True}
    )
    if compiled.params is None:
        return (compiled.string,)
    return compiled.string, compiled.params


def adapt_datetime(val: datetime) -> str:
    if not (val.tzinfo is timezone.utc or val.tzname() == "UTC"):
        try:
            val = val.astimezone(timezone.utc)
        except (OverflowError, ValueError, OSError):
            if val.year == MAXYEAR:
                val = datetime.max
            elif val.year == MINYEAR:
                val = datetime.min
            else:
                raise
    return val.replace(tzinfo=None).isoformat(" ")


def convert_datetime(val: bytes) -> datetime:
    return datetime.fromisoformat(val.decode()).replace(tzinfo=timezone.utc)


sqlite3.register_adapter(datetime, adapt_datetime)
sqlite3.register_converter("datetime", convert_datetime)


def get_retry_sleep_sec(retry_count: int) -> int:
    return RETRY_START_SEC * (RETRY_FACTOR**retry_count)


def retry_sqlite_locks(func):  # pylint: disable=redefined-outer-name
    # This retries the database modification in case of concurrent access
    @wraps(func)
    def wrapper(*args, **kwargs):
        exc = None
        for retry_count in range(RETRY_MAX_TIMES):
            try:
                return func(*args, **kwargs)
            except sqlite3.OperationalError as operror:
                exc = operror
                sleep(get_retry_sleep_sec(retry_count))
        raise exc

    return wrapper


class SQLiteDataStorage(AbstractDataStorage):
    """
    SQLite data storage uses SQLite3 for storing indexed data locally.
    This is currently used for the local cli.
    """

    def __init__(self, db_file: Optional[str] = None, uri: str = ""):
        self.schema: "DefaultSchema" = DefaultSchema()
        super().__init__(uri)
        self.db_file = db_file if db_file else DQLDir.find().db
        detect_types = sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES

        try:
            if self.db_file == ":memory:":
                # Enable multithreaded usage of the same in-memory db
                self.db = sqlite3.connect(
                    "file::memory:?cache=shared", uri=True, detect_types=detect_types
                )
            else:
                self.db = sqlite3.connect(self.db_file, detect_types=detect_types)
            self.engine = sqlalchemy.create_engine(
                "sqlite+pysqlite:///", creator=lambda: self.db, future=True
            )

            self.db.isolation_level = None  # Use autocommit mode
            self.db.execute("PRAGMA foreign_keys = ON")
            self.db.execute("PRAGMA cache_size = -102400")  # 100 MiB
            # Enable Write-Ahead Log Journaling
            self.db.execute("PRAGMA journal_mode = WAL")
            self.db.execute("PRAGMA synchronous = NORMAL")
            self.db.execute("PRAGMA case_sensitive_like = ON")
            if os.environ.get("DEBUG_SHOW_SQL_QUERIES"):
                self.db.set_trace_callback(print)

            self._init_storage_table()
            self._init_datasets_tables()
        except RuntimeError:
            raise DQLError("Can't connect to SQLite DB")

    @staticmethod
    def buckets_constraints() -> List["SchemaItem"]:
        return [
            UniqueConstraint("uri"),
        ]

    @staticmethod
    def datasets_constraints() -> List["SchemaItem"]:
        return [
            UniqueConstraint("name"),
        ]

    @staticmethod
    def buckets_columns() -> List["SchemaItem"]:
        columns = super(SQLiteDataStorage, SQLiteDataStorage).buckets_columns()
        return columns + SQLiteDataStorage.buckets_constraints()

    @staticmethod
    def datasets_columns() -> List["SchemaItem"]:
        columns = super(SQLiteDataStorage, SQLiteDataStorage).datasets_columns()
        return columns + SQLiteDataStorage.datasets_constraints()

    def _init_storage_table(self):
        """Initialize only tables related to storage, e.g s3"""
        self.execute(CreateTable(self.storages, if_not_exists=True))

    def _init_datasets_tables(self) -> None:
        self.execute(CreateTable(self.datasets, if_not_exists=True))
        self.execute(CreateTable(self.datasets_versions, if_not_exists=True))

    def init_db(self, prefix: str = "", is_new: bool = True):
        assert self.listing_table_name, "Missing listing_table_name"
        table = self.nodes.table
        partials_table = self.partials
        ig = self.id_generator
        if not prefix or is_new:
            self.execute(DropTable(table, if_exists=True))
            self.execute(DropTable(partials_table, if_exists=True))
            # Do not drop ID Generator, as this is shared across all buckets
        self.execute(CreateTable(table, if_not_exists=True))
        self.execute(CreateTable(partials_table, if_not_exists=True))
        self.execute(CreateTable(ig, if_not_exists=True))
        if not prefix or is_new:
            # If there is no prefix (indexing the whole bucket) or this is a new
            # bucket entry, then reset the id_generator for this bucket by deleting
            # any existing used last_id entries, and reinsert the zero last_id
            # as the start, as that indicates no ids have been used yet.
            partials_uri = f"partials:{self.uri}"
            self.execute(
                self.id_generator_delete().where(
                    (ig.c.uri == self.uri) | (ig.c.uri == partials_uri)
                )
            )
            self.execute(self.id_generator.insert().values(uri=self.uri, last_id=0))
            self.execute(self.id_generator.insert().values(uri=partials_uri, last_id=0))

    def clone(self, uri: Optional[str] = None) -> "SQLiteDataStorage":
        uri = uri or self.uri
        return SQLiteDataStorage(db_file=self.db_file, uri=uri)

    @retry_sqlite_locks
    def execute(
        self, query, cursor: Optional[sqlite3.Cursor] = None, conn=None
    ) -> sqlite3.Cursor:
        if cursor:
            return cursor.execute(*compile_statement(query))
        return self.db.execute(*compile_statement(query))

    @retry_sqlite_locks
    def executemany(
        self, query, params, cursor: Optional[sqlite3.Cursor] = None
    ) -> sqlite3.Cursor:
        if cursor:
            return cursor.executemany(compile_statement(query)[0], params)
        return self.db.executemany(compile_statement(query)[0], params)

    def _get_next_ids(self, uri: str, count: int) -> range:
        with self.db:
            # Transactions ensure no concurrency conflicts
            self.db.execute("BEGIN")
            ig = self.id_generator
            self.execute(
                self.id_generator_update()
                .where(ig.c.uri == uri)
                .values(last_id=ig.c.last_id + count)
            )
            # TODO: RETURNING might be a better option,
            # but is only supported on SQLite 3.35.0 or newer
            last_id = self.execute(
                self.id_generator_select(ig.c.last_id).where(ig.c.uri == uri)
            ).fetchone()[0]

        return range(last_id - count + 1, last_id + 1)

    def create_dataset_rows_table(
        self,
        name: str,
        custom_columns: Sequence["sqlalchemy.Column"] = (),
        if_not_exists: bool = True,
    ) -> None:
        q = CreateTable(
            dataset_table(name, custom_columns=custom_columns),
            if_not_exists=if_not_exists,
        )
        self.execute(q)

    def _get_dataset_row_values(
        self,
        name: str,
        columns: Optional[Sequence[str]] = None,
        limit: Optional[int] = 20,
        version=None,
    ) -> Iterator[Mapping[str, Any]]:
        dataset = self.get_dataset(name)

        dr = self.dataset_rows(dataset.id, version)
        select_columns = []
        if columns:
            select_columns = [getattr(dr.c, c) for c in columns]
        query = dr.select(*select_columns)
        if limit:
            query = query.limit(limit)

        cur = self.db.cursor()
        cur.row_factory = sqlite3.Row  # type: ignore[assignment]
        yield from self.execute(query, cursor=cur)

    def create_shadow_dataset(
        self, name: str, create_rows: Optional[bool] = True
    ) -> DatasetRecord:
        """Creates new shadow dataset if it doesn't exist yet"""
        with self.db:
            self.db.execute("begin")

            d = self.datasets
            self.execute(
                sqlite.insert(d)
                .values(
                    name=name,
                    shadow=True,
                    status=DatasetStatus.CREATED,
                    created_at=datetime.now(timezone.utc),
                )
                .on_conflict_do_nothing(index_elements=["name"])
            )
            dataset = self.get_dataset(name)
            assert dataset.shadow

            if create_rows:
                table_name = self.dataset_table_name(dataset.id)
                self.create_dataset_rows_table(table_name)
                dataset = self.update_dataset_status(dataset, DatasetStatus.PENDING)

            return dataset  # type: ignore[return-value]

    def insert_into_shadow_dataset(
        self, name: str, uri: str, path: str, recursive=False
    ) -> None:
        dataset = self.get_dataset(name)
        assert dataset.shadow

        # Not including id
        transfer_fields = [c for c in DATASET_CORE_COLUMN_NAMES if c != "id"]
        select_query = self.nodes_dataset_query(
            transfer_fields, path=path, recursive=recursive, uri=uri
        )

        dr = self.dataset_rows(dataset.id)
        insert_query = dr.insert().from_select(transfer_fields, select_query)
        self.execute(insert_query)

    def _rename_table(self, old_name: str, new_name: str):
        old_name = quote_schema(old_name)
        new_name = quote_schema(new_name)
        self.db.execute(f"ALTER TABLE {old_name} RENAME TO {new_name}")

    def create_dataset_version(
        self, name: str, version: int, create_rows_table=True
    ) -> DatasetRecord:
        with self.db:
            self.db.execute("begin")

            dataset = self.get_dataset(name)

            dv = self.datasets_versions
            self.execute(
                sqlite.insert(dv)
                .values(
                    dataset_id=dataset.id,
                    version=version,
                    created_at=datetime.now(timezone.utc),
                )
                .on_conflict_do_nothing(index_elements=["dataset_id", "version"])
            )

            if create_rows_table:
                table_name = self.dataset_table_name(dataset.id, version)
                self.create_dataset_rows_table(table_name)

            return dataset

    def merge_dataset_rows(
        self,
        src: DatasetRecord,
        dst: DatasetRecord,
        src_version: Optional[int] = None,
        dst_version: Optional[int] = None,
    ) -> None:
        dst_empty = False

        if not self.has_table(self.dataset_table_name(src.id, src_version)):
            # source table doesn't exist, nothing to do
            return

        if not self.has_table(self.dataset_table_name(dst.id, dst_version)):
            # destination table doesn't exist, create it
            self.create_dataset_rows_table(self.dataset_table_name(dst.id))
            dst_empty = True

        src_dr = self.dataset_rows(src.id, src_version).table
        dst_dr = self.dataset_rows(dst.id, dst_version).table
        dst_dr_latest = self.dataset_rows(dst.id, dst.latest_version).table

        # Not including id
        merge_fields = [c for c in DATASET_CORE_COLUMN_NAMES if c != "id"]

        select_src = select(*(getattr(src_dr.c, f) for f in merge_fields))
        select_dst_latest = select(*(getattr(dst_dr_latest.c, f) for f in merge_fields))

        union_query = sqlalchemy.union(select_src, select_dst_latest)

        if dst_empty:
            # we don't need union, but just select from source to destination
            insert_query = sqlite.insert(dst_dr).from_select(merge_fields, select_src)
        else:
            insert_query = (
                sqlite.insert(dst_dr)
                .from_select(merge_fields, union_query)
                .prefix_with("OR IGNORE")
            )

        self.execute(insert_query)

    def remove_shadow_dataset(self, dataset: DatasetRecord, drop_rows=True) -> None:
        with self.db:
            self.db.execute("begin")
            d = self.datasets
            self.execute(self.datasets_delete().where(d.c.id == dataset.id))
            if drop_rows:
                table_name = self.dataset_table_name(dataset.id)
                self.execute(DropTable(Table(table_name, MetaData())))

    async def insert_entry(self, entry: Dict[str, Any]) -> int:
        return (
            self.execute(
                self.nodes.insert().values(self._prepare_node(entry))
            ).lastrowid
            or 0
        )

    async def insert_entries(self, entries: Iterable[Dict[str, Any]]) -> None:
        self.executemany(
            self.nodes.insert().values({f: bindparam(f) for f in self.node_fields[1:]}),
            map(self._prepare_node, entries),
        )

    def create_storage_if_not_registered(
        self, uri: str, symlinks: bool = False
    ) -> None:
        s = self.storages
        self.execute(
            sqlite.insert(s)
            .values(uri=uri, status=StorageStatus.CREATED, symlinks=symlinks)
            .on_conflict_do_nothing()
        )

    def find_stale_storages(self):
        """
        Finds all pending storages for which the last inserted node has happened
        before STALE_HOURS_LIMIT hours, and marks it as STALE
        """
        with self.db:
            self.db.execute("begin")
            s = self.storages
            pending_storages = map(
                Storage._make,
                self.execute(
                    self.storages_select().where(s.c.status == StorageStatus.PENDING)
                ),
            )
            for storage in pending_storages:
                if storage.is_stale:
                    print(f"Marking storage {storage.uri} as stale")
                    self._mark_storage_stale(storage.id)

    def register_storage_for_indexing(
        self,
        uri: str,
        force_update: bool = True,
        prefix: str = "",
    ) -> Tuple[Storage, bool, bool, bool]:
        """
        Prepares storage for indexing operation.
        This method should be called before index operation is started
        It returns:
            - storage, prepared for indexing
            - boolean saying if indexing is needed
            - boolean saying if indexing is currently pending (running)
            - boolean saying if the storage is newly registered
        """
        # This ensures that all calls to the DB are in a single transaction
        # and commit is automatically called once this function returns
        with self.db:
            self.db.execute("begin")

            # Create storage if it doesn't exist
            self.create_storage_if_not_registered(uri)
            storage = self.get_storage(uri)

            if storage.status == StorageStatus.PENDING:
                return storage, False, True, False

            elif storage.is_expired or storage.status == StorageStatus.STALE:
                storage = self.mark_storage_pending(storage)
                return storage, True, False, False

            elif storage.status == StorageStatus.COMPLETE and not force_update:
                return storage, False, False, False

            elif (
                storage.status == StorageStatus.PARTIAL and prefix and not force_update
            ):
                if self._check_partial_index_valid(prefix):
                    return storage, False, False, False
                self._delete_partial_index(prefix)
                return storage, True, False, False

            else:
                is_new = storage.status == StorageStatus.CREATED
                storage = self.mark_storage_pending(storage)
                return storage, True, False, is_new

    def mark_storage_indexed(
        self,
        uri: str,
        status: int,
        ttl: int,
        end_time: Optional[datetime] = None,
        prefix: str = "",
        partial_id: int = 0,
    ) -> None:
        if status == StorageStatus.PARTIAL and not prefix:
            raise AssertionError("Partial indexing requires a prefix")

        if end_time is None:
            end_time = datetime.now(timezone.utc)
        expires = Storage.get_expiration_time(end_time, ttl)

        with self.db:
            self.db.execute("BEGIN")

            s = self.storages
            self.execute(
                self.storages_update()
                .where(s.c.uri == uri)
                .values(  # type: ignore [attr-defined]
                    timestamp=end_time,
                    expires=expires,
                    status=status,
                    last_inserted_at=end_time,
                )
            )

            if not self.listing_table_name:
                # This only occurs in tests
                return

            p = self.partials
            if status in {StorageStatus.COMPLETE, StorageStatus.FAILED}:
                # Delete remaining partial index paths
                self.execute(self.partials_delete())
            elif status == StorageStatus.PARTIAL:
                dirprefix = posixpath.join(prefix, "")
                self.execute(
                    sqlite.insert(p)
                    .values(
                        path_str=dirprefix,
                        timestamp=end_time,
                        expires=expires,
                        partial_id=partial_id,
                    )
                    .on_conflict_do_update(
                        index_elements=["path_str"],
                        set_={"timestamp": end_time, "expires": expires},
                    )
                )

    def validate_paths(self) -> int:
        """Find and mark any invalid paths."""
        t1 = self.nodes.table
        t2 = t1.alias("t2")
        t3 = t1.alias("t3")
        id_query = (
            select(t2.c.id)  # type: ignore[attr-defined]
            .select_from(t2)
            .join(t3, (t2.c.path_str == t3.c.path_str) & (t2.c.id != t3.c.id))
            .where(
                t2.c.valid == true(),
                t2.c.dir_type == 0,
            )
        )
        query = (
            update(t1)
            .values(valid=False)
            .where(t1.c.id.in_(id_query))  # type: ignore[attr-defined]
        )

        row_count = self.execute(query).rowcount
        if row_count:
            logger.warning(
                "File names that collide with directory names will be ignored. "
                f"Number found: {row_count}"
            )
        return row_count

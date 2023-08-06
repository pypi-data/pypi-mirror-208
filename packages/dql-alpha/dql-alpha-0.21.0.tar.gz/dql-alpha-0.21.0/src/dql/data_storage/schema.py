from typing import TYPE_CHECKING, Generic, List, Optional, Type, TypeVar

import sqlalchemy as sa
from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Integer,
    MetaData,
    Text,
)

if TYPE_CHECKING:
    from sqlalchemy import Engine
    from sqlalchemy.sql.base import Executable


class Table:
    def __init__(self, name: str, metadata: Optional["MetaData"] = None):
        self.metadata: "MetaData" = metadata if metadata is not None else MetaData()
        self.name: str = name
        self.table: "sa.Table" = self.get_table()

    @property
    def columns(self):
        return self.table.columns

    @property
    def c(self):
        return self.table.columns

    @staticmethod
    def default_columns() -> List[Column]:
        return []

    def get_table(self) -> "sa.Table":
        table = self.metadata.tables.get(self.name)
        if table is None:
            table = sa.Table(
                self.name,
                self.metadata,
                *self.default_columns(),
            )
        return table

    def apply_conditions(self, query: "Executable") -> "Executable":
        """
        Apply any conditions that belong on all selecting queries.

        This could be used to filter tables that use access control.
        """
        return query

    def select(self, *columns):
        if not columns:
            query = self.table.select()
        else:
            query = sa.select(*columns).select_from(self.table)
        return self.apply_conditions(query)

    def insert(self):
        return self.table.insert()

    def update(self):
        return self.apply_conditions(self.table.update())

    def delete(self):
        return self.apply_conditions(self.table.delete())


class Node(Table):
    @staticmethod
    def default_columns() -> List[Column]:
        return [
            Column("id", Integer, primary_key=True),
            Column("dir_type", Integer, index=True),
            Column("parent_id", Integer, index=True),
            Column("name", Text, nullable=False, index=True),
            Column("checksum", Text),
            Column("etag", Text),
            Column("version", Text),
            Column("is_latest", Boolean),
            Column("last_modified", DateTime),
            Column("size", BigInteger, nullable=False, index=True),
            Column("owner_name", Text),
            Column("owner_id", Text),
            Column("path_str", Text, index=True),
            Column("anno", JSON),
            Column("valid", Boolean, default=True, nullable=False),
            Column("random", BigInteger, nullable=False),
            Column("sub_meta", JSON),
            Column("partial_id", Integer),
        ]


class DatasetRow(Table):
    def __init__(
        self, name: str, engine: "Engine", metadata: Optional["MetaData"] = None
    ):
        self.engine = engine
        super().__init__(name, metadata)

    def get_table(self) -> "sa.Table":
        table = self.metadata.tables.get(self.name)
        if table is None:
            return sa.Table(self.name, self.metadata, autoload_with=self.engine)
        return table


NodeT = TypeVar("NodeT", bound=Node)
DatasetRowT = TypeVar("DatasetRowT", bound=DatasetRow)


class Schema(Generic[NodeT, DatasetRowT]):
    node_cls: Type[NodeT]
    dataset_row_cls: Type[DatasetRowT]


class DefaultSchema(Schema[Node, DatasetRow]):
    def __init__(self):
        self.node_cls = Node
        self.dataset_row_cls = DatasetRow

import random
import string
from abc import ABC, abstractmethod
from copy import copy
from typing import TYPE_CHECKING, Iterable, List, Optional, TypeVar

import sqlalchemy
from sqlalchemy.sql.expression import label

from dql.catalog import get_catalog
from dql.data_storage.sqlite import compile_statement
from dql.dataset import DATASET_CORE_COLUMN_NAMES, DatasetRow
from dql.dataset import Status as DatasetStatus

from .schema import create_udf_table
from .udf import UDFType

if TYPE_CHECKING:
    from sqlalchemy.sql.base import Executable
    from sqlalchemy.sql.elements import ColumnElement

    from dql.catalog import Catalog
    from dql.query.udf import Generator


BATCH_SIZE = 1000


class StartingStep(ABC):
    """An initial query processing step, referencing a data source."""

    @abstractmethod
    def apply(self) -> "QueryGenerator":
        ...


class Step(ABC):
    """A query processing step (filtering, mutation, etc.)"""

    @abstractmethod
    def apply(self, query: "Executable") -> "QueryGenerator":
        """Apply the processing step."""


class QueryStep(StartingStep):
    def __init__(self, table):
        self.table = table

    def apply(self):
        """Return the query for the table the query refers to."""
        table = self.table

        def q(*columns):
            return sqlalchemy.select(*columns).select_from(table)

        return QueryGenerator(q, table.c)


class IndexingStep(StartingStep):
    def __init__(self, path, catalog, **kwargs):
        self.path = path
        self.catalog = catalog
        self.kwargs = kwargs

    def apply(self):
        """Return the query for the table the query refers to."""
        self.catalog.index([self.path], **self.kwargs)
        client_config = self.kwargs.get("client_config") or {}
        client, path = self.catalog.parse_url(self.path, **client_config)
        uri = client.uri

        def q(*columns):
            col_names = [c.name for c in columns]
            return self.catalog.data_storage.nodes_dataset_query(
                columns=col_names, path=path, recursive=True, uri=uri
            )

        column_objs = [sqlalchemy.column(c) for c in DATASET_CORE_COLUMN_NAMES]
        return QueryGenerator(q, column_objs)


class QueryGenerator:
    def __init__(self, func, columns):
        self.func = func
        self.columns = columns

    def exclude(self, column_names):
        return self.func(*[c for c in self.columns if c.name not in column_names])

    def select(self, column_names=None):
        if column_names is None:
            return self.func(*self.columns)
        return self.func(*[c for c in self.columns if c.name in column_names])


class UDFSignal(Step):
    """Add a custom column to the result set."""

    def __init__(self, name: str, udf: UDFType, catalog: "Catalog"):
        self.catalog = catalog
        self.name = name
        self.udf = udf

    def clone(self):
        return self.__class__(self.name, self.udf, self.catalog)

    def apply(self, query):
        if self.name in DATASET_CORE_COLUMN_NAMES:
            # populating a core dataset column
            return self.overwrite_existing(query)
        return self.new_column(query)

    def overwrite_existing(self, query):
        """Handler for udfs populating core columns (e.g. the checksum column)."""
        tbl, col = self.udf_results_table(query)
        # Construct a new query that will join the udf-generated partial table.

        subquery = query.subquery()
        q_cols = [c if c.name != self.name else col for c in subquery.c]

        def q(*columns):
            cols = []
            for c in columns:
                if c.name == col.name:
                    cols.append(col)
                else:
                    cols.append(c)

            q = subquery.join(tbl, tbl.c.id == subquery.c.id)
            if cols:
                return sqlalchemy.select(*cols).select_from(q)
            return sqlalchemy.select(cols).select_from(q)

        return QueryGenerator(q, q_cols)

    def new_column(self, query):
        """Handler for udfs adding custom signals."""
        tbl, col = self.udf_results_table(query)
        # Construct a new query that will join the udf-generated partial table.
        subq = query.subquery()

        def q(*columns):
            cols1 = []
            cols2 = []
            for c in columns:
                if c.name == col.name:
                    cols2.append(c)
                else:
                    cols1.append(c)

            if cols2:
                return (
                    sqlalchemy.select(*cols1)
                    .select_from(subq)
                    .join(tbl, tbl.c.id == subq.c.id)
                    .add_columns(*cols2)
                )
            return sqlalchemy.select(*cols1).select_from(subq)

        return QueryGenerator(q, [*subq.c, col])

    def udf_results_table(self, query):
        """
        Create and populate a temporary UDF results table, this table
        will have two columns:
         - id, for joining to the original query
         - {self.name}, for storing UDF results.
        """
        # TODO remove ad-hoc connection and sqlite3 features
        # https://github.com/iterative/dql/issues/511
        with self.catalog.data_storage.engine.connect() as connection:
            # use the sqlite3 dbapi directly for consistency with
            # SQLiteDataStorage, until we can use sqlalchemy
            # connections for everything
            conn = connection.connection.driver_connection
            cursor = conn.cursor()

            temp_table_name = f"udf_{self.name}_" + _random_string(6)
            col = sqlalchemy.Column(self.name, self.udf.output_type, nullable=True)
            tbl = create_udf_table(
                conn,
                temp_table_name,
                [col],
            )
            cursor = conn.cursor()
            cursor.row_factory = DatasetRow.from_cursor
            results = cursor.execute(*compile_statement(query))
            rows = []
            for row in results:
                signal = {self.name: self.udf(self.catalog, row)}
                rows.append(dict(id=row.id, **signal))
                if len(rows) > BATCH_SIZE:
                    update = tbl.insert().values(rows)
                    conn.execute(*compile_statement(update))
                    rows.clear()
            if rows:
                update = tbl.insert().values(rows)
                conn.execute(*compile_statement(update))
            return tbl, col


class RowGenerator(Step):
    """Extend dataset with new rows."""

    def __init__(self, generator: "Generator", catalog: "Catalog"):
        self.generator = generator
        self.catalog = catalog
        self.engine = catalog.data_storage.engine

    def clone(self):
        return self.__class__(self.generator, self.catalog)

    def apply(self, query):
        # Create a temporary table.
        temp_table_name = "generated_" + _random_string(6)
        columns: List["sqlalchemy.Column"] = [
            sqlalchemy.Column(col.name, col.type)
            for col in query.selected_columns
            if col.name not in DATASET_CORE_COLUMN_NAMES
        ]
        self.catalog.data_storage.create_dataset_rows_table(
            temp_table_name,
            custom_columns=columns,
            if_not_exists=False,
        )
        tbl = sqlalchemy.Table(
            temp_table_name, sqlalchemy.MetaData(), autoload_with=self.engine
        )

        # TODO remove ad-hoc connection and sqlite3 features
        # https://github.com/iterative/dql/issues/511
        with self.catalog.data_storage.engine.connect() as connection:
            # use the sqlite3 dbapi directly for consistency with
            # SQLiteDataStorage, until we can use sqlalchemy
            # connections for everything
            conn = connection.connection.driver_connection

            cursor = conn.cursor()
            cursor.row_factory = DatasetRow.from_cursor
            results = cursor.execute(*compile_statement(query))

            def execute_stmt(stmt):
                conn.execute(*compile_statement(stmt))

            rows = []
            for row in results:
                for new_entry in self.generator(self.catalog, row):
                    rows.append(new_entry)
                    if len(rows) >= BATCH_SIZE:
                        execute_stmt(tbl.insert().values(rows))
                        rows.clear()
            if rows:
                execute_stmt(tbl.insert().values(rows))

        original_query = query.subquery()
        table_query = tbl.select().subquery()
        original_cols = [label(c.name, c) for c in original_query.columns]
        table_cols = [label(c.name, c) for c in table_query.columns]

        def q(*columns):
            names = {c.name for c in columns}
            cols1 = [c for c in original_cols if c.name in names]
            cols2 = [
                c for c in table_cols if c.name in names
            ]  # Columns for the generated table.
            q = sqlalchemy.union_all(
                sqlalchemy.select(*cols1).select_from(original_query),
                sqlalchemy.select(*cols2).select_from(table_query),
            )
            return q

        return QueryGenerator(q, [*original_cols])


class SQLFilter(Step):
    def __init__(self, *args):  # pylint: disable=super-init-not-called
        self.expressions = args

    def __and__(self, other):
        return self.__class__(*(self.expressions + other))

    def clone(self):
        return self.__class__(*self.expressions)

    def apply(self, query):
        new_query = query.filter(*self.expressions)

        def q(*columns):
            return new_query.with_only_columns(*columns)

        return QueryGenerator(q, new_query.selected_columns)


class SQLUnion(Step):
    def __init__(self, query1, query2):
        self.query1 = query1
        self.query2 = query2

    def apply(self, query):
        q1 = self.query1.apply_steps().select().subquery()
        q2 = self.query2.apply_steps().select().subquery()
        columns1, columns2 = fill_columns(q1.columns, q2.columns)

        def q(*columns):
            names = {c.name for c in columns}
            col1 = [c for c in columns1 if c.name in names]
            col2 = [c for c in columns2 if c.name in names]
            return (
                sqlalchemy.select(*col1)
                .select_from(q1)
                .union(sqlalchemy.select(*col2).select_from(q2))
            )

        return QueryGenerator(q, columns1)


def fill_columns(
    *column_iterables: Iterable["ColumnElement"],
) -> List[List["ColumnElement"]]:
    column_dicts = [{c.name: c for c in columns} for columns in column_iterables]
    combined_columns = {n: c for col_dict in column_dicts for n, c in col_dict.items()}

    result: List[List["ColumnElement"]] = [[] for _ in column_dicts]
    for n in combined_columns:
        col = next(col_dict[n] for col_dict in column_dicts if n in col_dict)
        for col_dict, out in zip(column_dicts, result):
            if n in col_dict:
                out.append(col_dict[n])
            else:
                # Cast the NULL to ensure all columns are aware of their type
                # Label it to ensure it's aware of its name
                out.append(sqlalchemy.cast(sqlalchemy.null(), col.type).label(n))
    return result


SQLQueryT = TypeVar("SQLQueryT", bound="SQLQuery")


class SQLQuery:
    def __init__(
        self,
        starting_step: StartingStep,
        steps: Optional[Iterable["Step"]] = None,
        catalog: Optional["Catalog"] = None,
        client_config=None,
    ):  # pylint: disable=super-init-not-called
        self.steps: List["Step"] = list(steps) if steps is not None else []
        self.starting_step: StartingStep = starting_step
        self.catalog = catalog or get_catalog(client_config=client_config)

    def __iter__(self):
        return iter(self.results())

    def __or__(self, other):
        return self.union(other)

    def apply_steps(self):
        """
        Apply the steps in the query and return the resulting
        sqlalchemy.Executable.
        """
        query = self.starting_step.apply()
        for step in self.steps:
            query = step.apply(query.select())  # a chain of steps linked by results
        return query

    def results(self, row_factory=None):
        engine = self.catalog.data_storage.engine
        query = self.apply_steps()
        # TODO remove ad-hoc connection and sqlite3 features
        # https://github.com/iterative/dql/issues/511
        with engine.connect() as connection:
            conn = connection.connection.driver_connection
            cursor = conn.cursor()
            if row_factory:
                cursor.row_factory = row_factory
            result = cursor.execute(*compile_statement(query.select())).fetchall()
        return result

    def clone(self: SQLQueryT) -> SQLQueryT:
        obj = copy(self)
        obj.steps = obj.steps.copy()
        return obj

    def filter(self, *args):
        query = self.clone()
        steps = query.steps
        if steps and isinstance(steps[-1], SQLFilter):
            steps[-1] = steps[-1] & args
        else:
            steps.append(SQLFilter(*args))
        return query

    def union(self, dataset_query):
        left = self.clone()
        right = dataset_query.clone()
        new_query = self.clone()
        new_query.steps = [SQLUnion(left, right)]
        return new_query


class DatasetQuery(SQLQuery):
    def __init__(
        self,
        path: str = "",
        name: str = "",
        version: Optional[int] = None,
        catalog=None,
        client_config=None,
    ):
        if catalog is None:
            catalog = get_catalog(client_config=client_config)

        data_storage = catalog.data_storage
        starting_step: StartingStep
        if path:
            starting_step = IndexingStep(path, catalog, client_config=client_config)
        elif name:
            ds = data_storage.get_dataset(name)
            version = version or ds.latest_version
            table = data_storage.dataset_table_name(dataset_id=ds.id, version=version)
            table_obj = sqlalchemy.Table(
                table, sqlalchemy.MetaData(), autoload_with=catalog.data_storage.engine
            )
            starting_step = QueryStep(table_obj)
        else:
            raise ValueError("must provide path or name")

        super().__init__(
            starting_step=starting_step, catalog=catalog, client_config=client_config
        )

    def add_signal(self, udf: UDFType, name: Optional[str] = None):
        query = self.clone()
        steps = query.steps
        column_name = name or getattr(udf, "column", None)
        if not column_name:
            raise ValueError("column name not specified")
        steps.append(UDFSignal(column_name, udf, self.catalog))
        return query

    def generate(self, generator: "Generator"):
        query = self.clone()
        steps = query.steps
        steps.append(RowGenerator(generator, self.catalog))
        return query

    def save(self, name: str):
        """Save the query as a shadow dataset."""
        query = self.apply_steps()

        # Save to a temporary table first.
        temp_tbl = f"tmp_{name}_" + _random_string(6)
        columns: List["sqlalchemy.Column"] = [
            sqlalchemy.Column(col.name, col.type)
            for col in query.columns
            if col.name not in DATASET_CORE_COLUMN_NAMES
        ]
        self.catalog.data_storage.create_dataset_rows_table(
            temp_tbl,
            custom_columns=columns,
            if_not_exists=False,
        )
        tbl = sqlalchemy.Table(
            temp_tbl,
            sqlalchemy.MetaData(),
            autoload_with=self.catalog.data_storage.engine,
        )
        # Exclude the id column and let the db create it to avoid unique
        # constraint violations
        cols = [col.name for col in tbl.c if col.name != "id"]

        self.catalog.data_storage.execute(
            sqlalchemy.insert(tbl).from_select(cols, query.exclude("id"))
        )

        # Create a shadow dataset.
        self.catalog.data_storage.create_shadow_dataset(name, create_rows=False)
        dataset = self.catalog.data_storage.get_dataset(name)
        if dataset is None:
            raise RuntimeError(f"No dataset found with {name=}")
        # pylint: disable=protected-access
        table_name = self.catalog.data_storage.dataset_table_name(dataset.id)

        self.catalog.data_storage._rename_table(temp_tbl, table_name)
        self.catalog.data_storage.update_dataset_status(dataset, DatasetStatus.COMPLETE)


T = TypeVar("T")


def return_ds(dataset_query: T) -> T:
    if isinstance(dataset_query, DatasetQuery):
        ds_id = _random_string(6)
        ds_name = f"ds_return_{ds_id}"
        dataset_query.catalog.data_storage.return_ds_hook(ds_name)
        dataset_query.save(ds_name)
    return dataset_query


def _random_string(length: int) -> str:
    return "".join(
        random.choice(string.ascii_letters + string.digits)  # nosec B311
        for i in range(length)
    )

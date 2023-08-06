from typing import TYPE_CHECKING, Any, Callable, Type, Union

from dql.catalog import Catalog

from .schema import Column, Object

if TYPE_CHECKING:
    from dql.dataset import DatasetRow

UDFType = Callable[["Catalog", "DatasetRow"], Any]


def udf(output_type: Any, *parameters: Union["Column", "Object"]):
    """Decorate a function to be usable as a UDF."""

    def decorator(func: Callable):
        return UDF(func, output_type, *parameters)

    return decorator


class UDF:
    """A wrapper class for UDFs to be used in custom signal generation."""

    def __init__(
        self,
        func: Callable,
        output_type: Any,
        *parameters: Union["Column", "Object"],
    ):
        self.func = func
        self.output_type = output_type
        self.parameters = parameters

    def __call__(self, catalog: "Catalog", row: "DatasetRow") -> Any:
        params = []
        for p in self.parameters:
            if isinstance(p, Column):
                params.append(row[p.name])
            elif isinstance(p, Object):
                with catalog.open_object(row) as f:
                    obj: Any = p.reader(f)
                params.append(obj)
            else:
                raise ValueError("unknown udf parameter")
        return self.func(*params)


def generator(*parameters: Union["Column", "Object", Type["Catalog"]]):
    def decorator(func: Callable):
        return Generator(func, *parameters)

    return decorator


class Generator:
    """A wrapper class for UDFs used to generate new dataset rows."""

    def __init__(
        self, func: Callable, *parameters: Union["Column", "Object", Type["Catalog"]]
    ):
        self.func = func
        self.parameters = parameters

    def __call__(self, catalog: "Catalog", row: "DatasetRow"):
        params = []
        for p in self.parameters:
            if isinstance(p, Column):
                params.append(row[p.name])
            elif isinstance(p, Object):
                with catalog.open_object(row) as f:
                    obj: Any = p.reader(f)
                params.append(obj)
            elif p is Catalog:
                params.append(catalog)
            else:
                raise ValueError("unknown udf parameter")
        yield from self.func(row, *params)

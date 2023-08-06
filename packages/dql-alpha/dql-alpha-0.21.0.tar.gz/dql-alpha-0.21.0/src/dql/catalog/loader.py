import os
from importlib import import_module

from dql.catalog import Catalog
from dql.data_storage import SQLiteDataStorage
from dql.utils import get_envs_by_prefix

ADAPTER_ARG_PREFIX = "DQL_ADAPTER_ARG_"


def get_catalog(client_config=None) -> Catalog:
    """
    Function that creates Catalog instance with appropriate data storage class
    Data storage class can be provided with env variable DQL_DB_ADAPTER and if
    not provided, default one is used

    If data storage class expects some kwargs, they can be provided via
    env variables by adding them with prefix DQL_DB_ADAPTER_ARG_ and
    name of variable after, e.g if it accepts team_id as kwargs we can provide
    DQL_DB_ADAPTER_ARG_TEAM_ID=12345 env variable
    """
    db_adapter_import_path = os.environ.get("DQL_DB_ADAPTER")
    adapter_arg_envs = get_envs_by_prefix(ADAPTER_ARG_PREFIX)
    # convert env variable names to keyword argument names by lowercasing it
    adapter_args = {k.lower(): v for k, v in adapter_arg_envs.items()}

    if db_adapter_import_path:
        # DB Adapter paths are specified as (for example):
        # dql.data_storage.SQLiteDataStorage
        if "." not in db_adapter_import_path:
            raise RuntimeError(
                f"Invalid DQL_DB_ADAPTER import path: {db_adapter_import_path}"
            )
        module_name, _, class_name = db_adapter_import_path.rpartition(".")
        db_adapter = import_module(module_name)
        db_adapter_class = getattr(db_adapter, class_name)
    else:
        db_adapter_class = SQLiteDataStorage
    return Catalog(db_adapter_class(**adapter_args), client_config=client_config)

import logging
import os
import shlex
import sys
import traceback
from argparse import Action, ArgumentParser, ArgumentTypeError, Namespace
from itertools import chain
from typing import Iterable, Iterator, List, Mapping, Optional, Tuple, Union

import shtab

from dql import __version__, utils
from dql.catalog import Catalog, get_catalog, indexer_formats
from dql.cli_utils import BooleanOptionalAction
from dql.client import Client
from dql.node import DIRTYPE_DIRS, long_line_str
from dql.remote.studio import StudioClient
from dql.utils import DQLDir, get_remote_config, read_config

logger = logging.getLogger("dql")

TTL_HUMAN = "4h"
TTL_INT = 4 * 60 * 60
FIND_COLUMNS = ["du", "name", "owner", "path", "size", "type"]


def human_time_type(value_str: str, can_be_none: bool = False) -> Optional[int]:
    value = utils.human_time_to_int(value_str)

    if value:
        return value
    if can_be_none:
        return None

    raise ArgumentTypeError(
        "This option supports only a human-readable time interval like 12h or 4w."
    )


def parse_find_column(column: str) -> str:
    column_lower = column.strip().lower()
    if column_lower in FIND_COLUMNS:
        return column_lower
    raise ArgumentTypeError(
        f"Invalid column for find: '{column}' Options are: {','.join(FIND_COLUMNS)}"
    )


def find_columns_type(
    columns_str: str,
    default_colums_str: str = "path",
) -> List[str]:
    if not columns_str:
        columns_str = default_colums_str

    return [parse_find_column(c) for c in columns_str.split(",")]


def add_sources_arg(parser: ArgumentParser, nargs: Union[str, int] = "+") -> Action:
    return parser.add_argument(
        "sources",
        type=str,
        nargs=nargs,
        help="Data sources - paths to cloud storage dirs",
    )


def get_parser() -> ArgumentParser:
    parser = ArgumentParser(description="DQL: Data Query Language", prog="dql")

    parser.add_argument("-V", "--version", action="version", version=__version__)

    parent_parser = ArgumentParser(add_help=False)
    parent_parser.add_argument(
        "--aws-endpoint-url",
        type=str,
        help="AWS endpoint URL",
    )
    parent_parser.add_argument(
        "--aws-anon",
        action="store_true",
        help="AWS anon (aka awscli's --no-sign-request)",
    )
    parent_parser.add_argument(
        "--ttl",
        type=human_time_type,
        default=TTL_HUMAN,
        help="Time-to-live of data source cache. Negative equals forever.",
    )
    parent_parser.add_argument(
        "-u", "--update", action="count", default=0, help="Update cache"
    )
    parent_parser.add_argument(
        "-v", "--verbose", action="count", default=0, help="Verbose"
    )
    parent_parser.add_argument(
        "-q", "--quiet", action="count", default=0, help="Be quiet"
    )

    subp = parser.add_subparsers(help="Sub-command help", dest="command")
    parse_get = subp.add_parser("get", parents=[parent_parser], help="Fetch a dataset")
    parse_get.add_argument(
        "source", type=str, help="Data source - a path to a cloud storage dir"
    )
    parse_get.add_argument(  # type: ignore[attr-defined]
        "-o", "--output", type=str, help="Output"
    ).complete = shtab.DIR
    parse_get.add_argument(
        "-f",
        "--force",
        action="count",
        default=0,
        help="Force creating outputs",
    )
    parse_get.add_argument("-d", "--descr", type=str, help="Description")

    parse_cp = subp.add_parser(
        "cp", parents=[parent_parser], help="Copy data files from the cloud"
    )
    add_sources_arg(parse_cp).complete = shtab.DIR  # type: ignore[attr-defined] # noqa: E501
    parse_cp.add_argument("output", type=str, help="Output")
    parse_cp.add_argument(
        "-f",
        "--force",
        default=False,
        action="store_true",
        help="Force creating outputs",
    )
    parse_cp.add_argument(
        "-r",
        "-R",
        "--recursive",
        default=False,
        action="store_true",
        help="Copy directories recursively",
    )
    parse_cp.add_argument(
        "--no-glob",
        default=False,
        action="store_true",
        help="Do not expand globs (such as * or ?)",
    )

    parse_clone = subp.add_parser(
        "clone", parents=[parent_parser], help="Copy data files from the cloud"
    )
    add_sources_arg(parse_clone).complete = shtab.DIR  # type: ignore[attr-defined] # noqa: E501
    parse_clone.add_argument("output", type=str, help="Output")
    parse_clone.add_argument(
        "-f",
        "--force",
        default=False,
        action="store_true",
        help="Force creating outputs",
    )
    parse_clone.add_argument(
        "-r",
        "-R",
        "--recursive",
        default=False,
        action="store_true",
        help="Copy directories recursively",
    )
    parse_clone.add_argument(
        "--no-glob",
        default=False,
        action="store_true",
        help="Do not expand globs (such as * or ?)",
    )
    parse_clone.add_argument(
        "--no-cp",
        default=False,
        action="store_true",
        help="Do not copy files, just create a shadow dataset",
    )
    parse_clone.add_argument(
        "--edql",
        default=False,
        action="store_true",
        help="Create a .edql file",
    )
    parse_clone.add_argument(
        "--edql-file",
        help="Use a different filename for the resulting .edql file",
    )

    parse_register = subp.add_parser(
        "register", parents=[parent_parser], help="Register a dataset"
    )
    parse_register.add_argument("name", type=str, help="Dataset name")
    parse_register.add_argument(
        "--registered-name",
        action="store",
        default="",
        help="Registered dataset name",
    )
    parse_register.add_argument(
        "--version",
        action="store",
        default=None,
        type=int,
        help="New registered dataset version",
    )
    parse_register.add_argument(
        "--description",
        action="store",
        default="",
        help="Dataset description",
    )
    parse_register.add_argument(
        "--labels",
        default=[],
        nargs="+",
        help="Dataset labels",
    )

    parse_edit_dataset = subp.add_parser(
        "edit-dataset", parents=[parent_parser], help="Edit dataset metadata"
    )
    parse_edit_dataset.add_argument("name", type=str, help="Dataset name")
    parse_edit_dataset.add_argument(
        "--new-name",
        action="store",
        default="",
        help="Dataset new name",
    )
    parse_edit_dataset.add_argument(
        "--description",
        action="store",
        default="",
        help="Dataset description",
    )
    parse_edit_dataset.add_argument(
        "--labels",
        default=[],
        nargs="+",
        help="Dataset labels",
    )

    ls_datasets_parser = subp.add_parser(
        "ls-datasets", parents=[parent_parser], help="List datasets"
    )
    ls_datasets_parser.add_argument(
        "--shadow",
        default=None,
        action=BooleanOptionalAction,
        help="List only shadow datasets, or only registered datasets",
    )

    ls_dataset_rows_parser = subp.add_parser(
        "ls-dataset-rows", parents=[parent_parser], help="List dataset rows"
    )
    ls_dataset_rows_parser.add_argument("name", type=str, help="Dataset name")
    ls_dataset_rows_parser.add_argument(
        "--version",
        action="store",
        default=None,
        type=int,
        help="Dataset version",
    )

    rm_dataset_parser = subp.add_parser(
        "rm-dataset", parents=[parent_parser], help="Removes dataset"
    )
    rm_dataset_parser.add_argument("name", type=str, help="Dataset name")
    rm_dataset_parser.add_argument(
        "--version",
        action="store",
        default=None,
        type=int,
        help="Dataset version",
    )
    rm_dataset_parser.add_argument(
        "--force",
        default=False,
        action=BooleanOptionalAction,
        help="Force delete registered dataset with all of it's versions",
    )

    parse_merge_datasets = subp.add_parser(
        "merge-datasets", parents=[parent_parser], help="Merges datasets"
    )
    parse_merge_datasets.add_argument(
        "--src",
        action="store",
        default=None,
        help="Source dataset name",
    )
    parse_merge_datasets.add_argument(
        "--dst",
        action="store",
        default=None,
        help="Destination dataset name",
    )
    parse_merge_datasets.add_argument(
        "--src-version",
        action="store",
        default=None,
        type=int,
        help="Source dataset version",
    )
    parse_merge_datasets.add_argument(
        "--dst-version",
        action="store",
        default=None,
        type=int,
        help="Destination dataset version",
    )

    parse_ls = subp.add_parser(
        "ls", parents=[parent_parser], help="List storage contents"
    )
    add_sources_arg(parse_ls, nargs="*")
    parse_ls.add_argument(
        "-l",
        "--long",
        action="count",
        default=0,
        help="List files in the long format",
    )
    parse_ls.add_argument(
        "--remote",
        action="store",
        default="",
        help="Name of remote to use",
    )

    parse_du = subp.add_parser(
        "du", parents=[parent_parser], help="Display space usage"
    )
    add_sources_arg(parse_du)
    parse_du.add_argument(
        "-b",
        "--bytes",
        default=False,
        action="store_true",
        help="Display sizes in bytes instead of human-readable sizes",
    )
    parse_du.add_argument(
        "-d",
        "--depth",
        "--max-depth",
        default=0,
        type=int,
        metavar="N",
        help=(
            "Display sizes for N directory depths below the given directory, "
            "the default is 0 (summarize provided directory only)."
        ),
    )
    parse_du.add_argument(
        "--si",
        default=False,
        action="store_true",
        help="Display sizes using powers of 1000 not 1024",
    )

    parse_find = subp.add_parser(
        "find", parents=[parent_parser], help="Search in a directory hierarchy"
    )
    add_sources_arg(parse_find)
    parse_find.add_argument(
        "-name",
        "--name",
        type=str,
        action="append",
        help="Filename to match pattern.",
    )
    parse_find.add_argument(
        "-iname",
        "--iname",
        type=str,
        action="append",
        help="Like -name but case insensitive.",
    )
    parse_find.add_argument(
        "-path",
        "--path",
        type=str,
        action="append",
        help="Path to match pattern.",
    )
    parse_find.add_argument(
        "-ipath",
        "--ipath",
        type=str,
        action="append",
        help="Like -path but case insensitive.",
    )
    parse_find.add_argument(
        "-size",
        "--size",
        type=str,
        help=(
            "Filter by size (+ is greater or equal, - is less or equal). "
            "Specified size is in bytes, or use a suffix like K, M, G for "
            "kilobytes, megabytes, gigabytes, etc."
        ),
    )
    parse_find.add_argument(
        "-type",
        "--type",
        type=str,
        help='File type: "f" - regular, "d" - directory',
    )
    parse_find.add_argument(
        "-jmespath",
        "--jmespath",
        type=str,
        action="append",
        help="JMESPath query to annotation (not supported currently)",
    )
    parse_find.add_argument(
        "-c",
        "--columns",
        type=find_columns_type,
        default=None,
        help=(
            "A comma-separated list of columns to print for each result. "
            f"Options are: {','.join(FIND_COLUMNS)} (Default: path)"
        ),
    )

    parse_index = subp.add_parser(
        "index", parents=[parent_parser], help="Index storage location"
    )
    parse_index.add_argument(
        "--format",
        type=str,
        default=None,
        choices=indexer_formats.keys(),
        help="Postprocessing step to apply, after indexing storage.",
    )
    add_sources_arg(parse_index)
    add_storage_parser = subp.add_parser(
        "add-storage", parents=[parent_parser], help="Register local path as storage"
    )
    add_storage_parser.add_argument("uri", type=str, help="Source URI or path")
    add_storage_parser.add_argument(
        "--symlinks",
        default=False,
        action="store_true",
        help="Use symlinks instead of full copies when downloading from storage",
    )

    subp.add_parser(
        "find-stale-storages",
        parents=[parent_parser],
        help="Finds and marks stale storages",
    )

    add_completion_parser(subp, [parent_parser])
    return parser


def add_completion_parser(subparsers, parents):
    parser = subparsers.add_parser(
        "completion",
        parents=parents,
        help="Output shell completion script",
    )
    parser.add_argument(
        "-s",
        "--shell",
        help="Shell syntax for completions.",
        default="bash",
        choices=shtab.SUPPORTED_SHELLS,
    )


def get_logging_level(args: Namespace) -> int:
    if args.quiet:
        return logging.CRITICAL
    elif args.verbose:
        return logging.DEBUG
    return logging.INFO


def ls_urls(
    sources,
    long: bool = False,
    *,
    client_config=None,
    catalog: Optional[Catalog] = None,
    **kwargs,
) -> Iterator[Tuple[str, Iterator[str]]]:
    if client_config is None:
        client_config = {}
    if catalog is None:
        catalog = get_catalog()

    curr_dir = None
    value_iterables = []
    for next_dir, values in _ls_urls_flat(
        sources, long, client_config, catalog, **kwargs
    ):
        if curr_dir is None or next_dir == curr_dir:  # type: ignore[unreachable] # noqa: E501
            value_iterables.append(values)
        else:
            yield curr_dir, chain(*value_iterables)  # type: ignore[unreachable] # noqa: E501
            value_iterables = [values]
        curr_dir = next_dir
    if curr_dir is not None:
        yield curr_dir, chain(*value_iterables)


def _node_data_to_ls_values(row, long_format=False):
    name = row[0]
    is_dir = row[1] in DIRTYPE_DIRS
    ending = "/" if is_dir else ""
    value = name + ending
    if long_format:
        last_modified = row[2]
        owner_name = row[3]
        timestamp = last_modified if not is_dir else None
        return long_line_str(value, timestamp, owner_name)
    return value


def _ls_urls_flat(
    sources,
    long: bool,
    client_config,
    catalog: Catalog,
    **kwargs,
) -> Iterator[Tuple[str, Iterator[str]]]:
    for source in sources:
        client_cls = Client.get_implementation(source)
        if client_cls.is_root_url(source):
            buckets = client_cls.ls_buckets(**client_config)
            if long:
                values = (long_line_str(b.name, b.created, "") for b in buckets)
            else:
                values = (b.name for b in buckets)
            yield source, values
        else:
            found = False
            fields = ["name", "dir_type"]
            if long:
                fields.extend(["last_modified", "owner_name"])
            for data_source, results in catalog.ls(
                [source], fields=fields, client_config=client_config, **kwargs
            ):
                values = (_node_data_to_ls_values(r, long) for r in results)
                found = True
                yield data_source.dirname(), values
            if not found:
                raise FileNotFoundError(f"No such file or directory: {source}")


def ls_indexed_storages(
    long: bool = False, catalog: Optional[Catalog] = None
) -> Iterator[str]:
    if catalog is None:
        catalog = get_catalog()
    storage_uris = catalog.ls_storage_uris()
    if long:
        for uri in storage_uris:
            # TODO: add Storage.created so it can be used here
            yield long_line_str(uri, None, "")
    else:
        yield from storage_uris


def ls_local(sources, long: bool = False, catalog: Optional[Catalog] = None, **kwargs):
    if catalog is None:
        catalog = get_catalog()
    if sources:
        if len(sources) == 1:
            for _, entries in ls_urls(sources, long=long, catalog=catalog, **kwargs):
                for entry in entries:
                    print(format_ls_entry(entry))
        else:
            first = True
            for source, entries in ls_urls(
                sources, long=long, catalog=catalog, **kwargs
            ):
                # print a newline between directory listings
                if first:
                    first = False
                else:
                    print()
                if source:
                    print(f"{source}:")
                for entry in entries:
                    print(format_ls_entry(entry))
    else:
        for entry in ls_indexed_storages(long=long, catalog=catalog):
            print(format_ls_entry(entry))


def format_ls_entry(entry: str) -> str:
    if entry.endswith("/") or not entry:
        entry = shlex.quote(entry[:-1])
        return f"{entry}/"
    return shlex.quote(entry)


def ls_remote(
    url: str,
    username: str,
    token: str,
    paths: Iterable[str],
    long: bool = False,
):
    client = StudioClient(url, username, token)
    first = True
    for path, response in client.ls(paths):
        if not first:
            print()
        if not response.ok or response.data is None:
            print(f"{path}:\n  Error: {response.message}\n")
            continue

        print(f"{path}:")
        if long:
            for row in response.data:
                entry = long_line_str(
                    row["name"] + ("/" if row["dir_type"] else ""),
                    row["last_modified"],
                    row["owner_name"],
                )
                print(format_ls_entry(entry))
        else:
            for row in response.data:
                entry = row["name"] + ("/" if row["dir_type"] else "")
                print(format_ls_entry(entry))
        first = False


def ls(
    sources,
    long: bool = False,
    remote: str = "",
    config: Optional[Mapping[str, str]] = None,
    **kwargs,
):
    if config is None:
        config = get_remote_config(read_config(DQLDir.find().root), remote=remote)
    remote_type = config["type"]
    if remote_type == "local":
        ls_local(sources, long=long, **kwargs)
    else:
        ls_remote(
            config["url"],
            config["username"],
            config["token"],
            sources,
            long=long,
        )


def ls_datasets(shadow_only=None):
    for d in get_catalog().ls_datasets(shadow_only=shadow_only):
        if d.shadow:
            print(f"(tmp) {d.name}")
        else:
            for v in d.versions or []:
                print(f"{d.name} (v{v.version})")


def ls_dataset_rows(name: str, version: Optional[int] = None):
    for row in get_catalog().ls_dataset_rows(name, version=version):
        entry = row.name + ("/" if row.dir_type else "")  # type: ignore[attr-defined]
        print(format_ls_entry(entry))


def rm_dataset(name: str, version: Optional[int] = None, force: Optional[bool] = False):
    get_catalog().remove_dataset(name, version=version, force=force)


def du(sources, show_bytes=False, si=False, **kwargs):
    for path, size in get_catalog().du(sources, **kwargs):
        if show_bytes:
            print(f"{size} {path}")
        else:
            print(f"{utils.sizeof_fmt(size, si=si): >7} {path}")


def find(sources, **kwargs):
    yield from get_catalog().find(sources, **kwargs)


def index(
    sources, catalog: Optional[Catalog] = None, indexer_format: str = None, **kwargs
):
    if catalog is None:
        catalog = get_catalog()
    fmt = None
    if indexer_format:
        fmt = indexer_formats.get(indexer_format)
    catalog.index(sources, index_processor=fmt, **kwargs)


def add_storage(uri: str, symlinks: bool = False) -> None:
    get_catalog().add_storage(uri, symlinks=symlinks)


def find_stale_storages():
    get_catalog().find_stale_storages()


def completion(shell: str) -> str:
    return shtab.complete(
        get_parser(),
        shell=shell,  # nosec B604
    )


def main(argv: Optional[List[str]] = None) -> int:  # noqa: C901
    parser = get_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 1

    logger.addHandler(logging.StreamHandler())
    logging_level = get_logging_level(args)
    logger.setLevel(logging_level)

    client_config = {
        "aws_endpoint_url": args.aws_endpoint_url,
        "aws_anon": args.aws_anon,
    }

    try:
        if args.command == "get":
            # TODO: descr = args.descr
            get_catalog().get(
                args.source,
                args.output,
                force=bool(args.force),
                update=bool(args.update),
                ttl=args.ttl,
                client_config=client_config,
            )
        elif args.command == "cp":
            get_catalog().cp(
                args.sources,
                args.output,
                force=bool(args.force),
                update=bool(args.update),
                recursive=bool(args.recursive),
                edql_file=None,
                edql_only=False,
                no_edql_file=True,
                no_glob=args.no_glob,
                ttl=args.ttl,
                client_config=client_config,
            )
        elif args.command == "clone":
            get_catalog().clone(
                args.sources,
                args.output,
                force=bool(args.force),
                update=bool(args.update),
                recursive=bool(args.recursive),
                no_glob=args.no_glob,
                ttl=args.ttl,
                no_cp=args.no_cp,
                edql=args.edql,
                edql_file=args.edql_file,
                client_config=client_config,
            )
        elif args.command == "register":
            get_catalog().register_shadow_dataset(
                args.name,
                description=args.description,
                labels=args.labels,
                registered_name=args.registered_name,
                version=args.version,
            )
            print(f"Registered dataset {args.name}")
        elif args.command == "edit-dataset":
            get_catalog().edit_dataset(
                args.name,
                description=args.description,
                new_name=args.new_name,
                labels=args.labels,
            )
        elif args.command == "merge-datasets":
            get_catalog().merge_datasets(
                args.src,
                args.dst,
                src_version=args.src_version,
                dst_version=args.dst_version,
            )
        elif args.command == "ls":
            ls(
                args.sources,
                long=bool(args.long),
                remote=args.remote,
                ttl=args.ttl,
                update=bool(args.update),
                client_config=client_config,
            )
        elif args.command == "ls-datasets":
            ls_datasets(args.shadow)
        elif args.command == "ls-dataset-rows":
            ls_dataset_rows(args.name, args.version)
        elif args.command == "rm-dataset":
            rm_dataset(args.name, version=args.version, force=args.force)
        elif args.command == "du":
            du(
                args.sources,
                show_bytes=args.bytes,
                depth=args.depth,
                si=args.si,
                ttl=args.ttl,
                update=bool(args.update),
                client_config=client_config,
            )
        elif args.command == "find":
            results_found = False
            for result in find(
                args.sources,
                ttl=args.ttl,
                update=bool(args.update),
                names=args.name,
                inames=args.iname,
                paths=args.path,
                ipaths=args.ipath,
                size=args.size,
                typ=args.type,
                jmespath=args.jmespath,
                columns=args.columns,
                client_config=client_config,
            ):
                print(result)
                results_found = True
            if not results_found:
                print("No results")
        elif args.command == "index":
            index(
                args.sources,
                ttl=args.ttl,
                indexer_format=args.format,
                update=bool(args.update),
                client_config=client_config,
            )
        elif args.command == "add-storage":
            add_storage(args.uri, symlinks=args.symlinks)
        elif args.command == "completion":
            print(completion(args.shell))
        elif args.command == "find-stale-storages":
            find_stale_storages()
        else:
            print(f"invalid command: {args.command}", file=sys.stderr)
            return 1
        return 0
    except BrokenPipeError:
        # Python flushes standard streams on exit; redirect remaining output
        # to devnull to avoid another BrokenPipeError at shutdown
        # See: https://docs.python.org/3/library/signal.html#note-on-sigpipe
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        return 141  # 128 + 13 (SIGPIPE)
    except Exception as exc:  # pylint: disable=broad-except
        print("Error:", exc, file=sys.stderr)
        if logging_level <= logging.DEBUG:
            traceback.print_exception(
                type(exc),
                exc,
                exc.__traceback__,
                file=sys.stderr,
            )
        return 1

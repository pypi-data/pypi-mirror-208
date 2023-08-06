import io
import os
import os.path as osp
import stat
from datetime import datetime
from typing import (
    TYPE_CHECKING,
    Dict,
    Iterable,
    Mapping,
    Optional,
    Type,
    TypeVar,
    Union,
)

from dateutil import tz
from dateutil.parser import isoparse
from tomlkit import parse

if TYPE_CHECKING:
    from tomlkit import TOMLDocument

GLOB_CHARS = ["?", "*", "[", "]"]
NUL = b"\0"

T = TypeVar("T", bound="DQLDir")


class DQLDir:
    DEFAULT = ".dql"
    CACHE = "cache"
    TMP = "tmp"
    DB = "db"
    ENV_VAR = "DQL_DIR"

    def __init__(
        self,
        root: Optional[str] = None,
        cache: Optional[str] = None,
        tmp: Optional[str] = None,
        db: Optional[str] = None,
    ) -> None:
        self.root = osp.abspath(root) if root is not None else self.default_root()
        self.cache = (
            osp.abspath(cache) if cache is not None else osp.join(self.root, self.CACHE)
        )
        self.tmp = (
            osp.abspath(tmp) if tmp is not None else osp.join(self.root, self.TMP)
        )
        self.db = osp.abspath(db) if db is not None else osp.join(self.root, self.DB)

    def init(self):
        os.makedirs(self.root, exist_ok=True)
        os.makedirs(self.cache, exist_ok=True)
        os.makedirs(self.tmp, exist_ok=True)
        os.makedirs(osp.split(self.db)[0], exist_ok=True)

    @classmethod
    def default_root(cls) -> str:
        return osp.join(os.getcwd(), cls.DEFAULT)

    @classmethod
    def find(cls: Type[T], create: bool = True) -> T:
        try:
            root = os.environ[cls.ENV_VAR]
        except KeyError:
            root = cls.default_root()
        instance = cls(root)
        if not osp.isdir(root):
            if create:
                instance.init()
            else:
                NotADirectoryError(root)
        return instance


def read_config(dql_root: str) -> Optional["TOMLDocument"]:
    project_path = osp.join(dql_root, "config")
    if osp.isfile(project_path):
        with open(project_path, encoding="utf-8") as f:
            text = f.read()
        return parse(text)
    return None


def get_remote_config(
    config: Optional["TOMLDocument"], remote: str = ""
) -> Mapping[str, str]:
    if config is None:
        return {"type": "local"}
    if not remote:
        try:
            remote = config["core"]["default-remote"]  # type: ignore[index,assignment] # noqa: E501
        except KeyError:
            return {"type": "local"}
    try:
        remote_conf: Mapping[str, str] = config["remote"][remote]  # type: ignore[assignment,index] # noqa: E501
    except KeyError:
        raise Exception(f"missing config section for default remote: remote.{remote}")
    except Exception as exc:
        raise Exception("invalid config") from exc

    if not isinstance(remote_conf, Mapping):
        raise Exception(f"config section remote.{remote} must be a mapping")

    remote_type = remote_conf.get("type")
    if remote_type not in ("local", "http"):
        raise Exception(
            f'config section remote.{remote} must have "type" with one of: '
            '"local", "http"'
        )

    if remote_type == "http":
        for key in ["url", "username", "token"]:
            try:
                remote_conf[key]
            except KeyError:
                raise Exception(
                    f"config section remote.{remote} of type {remote_type} "
                    f"must contain key {key}"
                )
    elif remote_type != "local":
        raise Exception(
            f"config section remote.{remote} has invalid remote type {remote_type}"
        )
    return remote_conf


def human_time_to_int(time: str) -> Optional[int]:
    if not time:
        return None

    suffix = time[-1]
    try:
        num = int(time if suffix.isdigit() else time[:-1])
    except ValueError:
        return None
    return num * {
        "h": 60 * 60,
        "d": 60 * 60 * 24,
        "w": 60 * 60 * 24 * 7,
        "m": 31 * 24 * 60 * 60,
        "y": 60 * 60 * 24 * 365,
    }.get(suffix.lower(), 1)


def time_to_str(dt):
    if isinstance(dt, str):
        dt = isoparse(dt)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def time_to_local(dt: Union[datetime, str]) -> datetime:
    # TODO check usage
    if isinstance(dt, str):
        dt = isoparse(dt)
    try:
        return dt.astimezone(tz.tzlocal())
    except (OverflowError, OSError, ValueError):
        return dt


def time_to_local_str(dt: Union[datetime, str]) -> str:
    return time_to_str(time_to_local(dt))


def is_expired(expires: Optional[Union[datetime, str]]):
    if expires:
        return time_to_local(expires) < time_to_local(datetime.now())

    return False


SIZE_SUFFIXES = ["", "K", "M", "G", "T", "P", "E", "Z", "Y", "R", "Q"]


def sizeof_fmt(num, suffix="", si=False):
    power = 1000.0 if si else 1024.0
    for unit in SIZE_SUFFIXES[:-1]:
        if abs(num) < power:
            if not unit:
                return f"{num:4.0f}{suffix}"
            return f"{num:3.1f}{unit}{suffix}"
        num /= power
    return f"{num:.1f}Q{suffix}"


def suffix_to_number(num_str: str) -> int:
    try:
        if len(num_str) > 1:
            suffix = num_str[-1].upper()
            if suffix in SIZE_SUFFIXES:
                suffix_idx = SIZE_SUFFIXES.index(suffix)
                return int(num_str[:-1]) * (1024**suffix_idx)
        return int(num_str)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid number/suffix for: {num_str}")


def force_create_dir(name):
    if not os.path.exists(name):
        os.mkdir(name)
    elif not os.path.isdir(name):
        os.remove(name)
        os.mkdir(name)


def dql_paths_join(source_path: str, file_paths: Iterable[str]) -> Iterable[str]:
    source_parts = source_path.rstrip("/").split("/")
    if set(source_parts[-1]).intersection(GLOB_CHARS):
        # Remove last element if it is a glob match (such as *)
        source_parts.pop()
    source_stripped = "/".join(source_parts)
    return (f"{source_stripped}/{path.lstrip('/')}" for path in file_paths)


# From: https://docs.python.org/3/library/shutil.html#rmtree-example
def remove_readonly(func, path, _):
    "Clear the readonly bit and reattempt the removal"
    os.chmod(path, stat.S_IWRITE)
    func(path)


def sql_escape_like(search: str, escape: str = "\\") -> str:
    return (
        search.replace(escape, escape * 2)
        .replace("%", f"{escape}%")
        .replace("_", f"{escape}_")
    )


class FileSlice(io.RawIOBase):
    """A thin wrapper around an existing file object that
    provides a part of its data as an individual file
    object.
    """

    def __init__(self, fileobj, offset, size, name):
        self.fileobj = fileobj
        self.offset = offset
        self.size = size
        self.position = 0
        self.name = name

    def readable(self):
        return True

    def writable(self):
        return False

    def seekable(self):
        return self.fileobj.seekable()

    def tell(self):
        """Return the current file position."""
        return self.position

    def seek(self, position, whence=io.SEEK_SET):
        """Seek to a position in the file."""
        if whence == io.SEEK_SET:
            self.position = min(max(position, 0), self.size)
        elif whence == io.SEEK_CUR:
            if position < 0:
                self.position = max(self.position + position, 0)
            else:
                self.position = min(self.position + position, self.size)
        elif whence == io.SEEK_END:
            self.position = max(min(self.size + position, self.size), 0)
        else:
            raise ValueError("Invalid argument")
        return self.position

    def readinto(self, b):
        max_size = self.size - self.position
        if max_size <= 0:
            return 0
        self.fileobj.seek(self.offset + self.position)
        if len(b) > max_size:
            b = memoryview(b)[:max_size]
        res = self.fileobj.readinto(b)
        if res != len(b):
            raise RuntimeError("unexpected end of data")
        self.position += res
        return res


def get_envs_by_prefix(prefix: str) -> Dict[str, str]:
    """
    Function that searches env variables by some name prefix and returns
    the ones found, but with prefix being excluded from it's names
    """
    variables: Dict[str, str] = {}
    for env_name, env_value in os.environ.items():
        if env_name.startswith(prefix):
            variables[env_name[len(prefix) :]] = env_value

    return variables

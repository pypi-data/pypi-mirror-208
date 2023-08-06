from datetime import datetime, timedelta, timezone
from struct import unpack
from typing import (
    Any,
    Dict,
    Generic,
    Iterable,
    Iterator,
    List,
    Optional,
    Tuple,
    TypeVar,
)

T = TypeVar("T")
LsData = Optional[List[Dict[str, Any]]]


class Response(Generic[T]):
    def __init__(self, data: T, ok: bool, message: str) -> None:
        self.data = data
        self.ok = ok
        self.message = message


class StudioClient:
    def __init__(
        self, url: str, username: str, token: str, timeout: float = 3600.0
    ) -> None:
        self._check_dependencies()
        self.url = url.rstrip("/")
        self.username = username
        self.token = token
        self.timeout = timeout

    def _check_dependencies(self) -> None:
        try:
            # pylint: disable=unused-import
            import msgpack  # noqa: F401
            import requests  # noqa: F401
        except ImportError as exc:
            raise Exception(
                f"Missing dependency: {exc.name}\n"
                "To install run:\n"
                "\tpip install 'dql-alpha[remote]'"
            )

    def _send_request(self, route: str, data: Dict[str, Any]) -> Response[Any]:
        import msgpack
        import requests

        response = requests.post(
            f"{self.url}/{route}",
            json={**data, "team_name": self.username},
            headers={
                "Content-Type": "application/json",
                "Authorization": f"token {self.token}",
            },
            timeout=self.timeout,
        )
        ok = response.ok
        content = msgpack.unpackb(response.content, ext_hook=self._unpacker_hook)
        response_data = content.get("data")
        if ok and response_data is None:
            message = "Indexing in progress"
        else:
            message = content.get("message", "")
        return Response(response_data, ok, message)

    @staticmethod
    def _unpacker_hook(code, data):
        import msgpack

        if code == 42:  # for parsing datetime objects
            has_timezone = False
            timezone_offset = None
            if len(data) == 8:
                # we send only timestamp without timezone if data is 8 bytes
                values = unpack("!d", data)
            else:
                has_timezone = True
                values = unpack("!dl", data)

            timestamp = values[0]
            if has_timezone:
                timezone_offset = values[1]
                return datetime.fromtimestamp(
                    timestamp, timezone(timedelta(seconds=timezone_offset))
                )
            else:
                return datetime.fromtimestamp(timestamp)

        return msgpack.ExtType(code, data)

    def ls(self, paths: Iterable[str]) -> Iterator[Tuple[str, Response[LsData]]]:
        # TODO: change LsData (response.data value) to be list of lists
        # to handle cases where a path will be expanded (i.e. globs)
        response: Response[LsData]
        for path in paths:
            response = self._send_request("ls", {"source": path})
            yield path, response

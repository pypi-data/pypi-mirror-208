from __future__ import annotations

from typing import Iterable
from typing import Optional

from drakaina._types import ASGIReceive
from drakaina._types import ASGIScope
from drakaina._types import ASGISend
from drakaina._types import WSGIApplication
from drakaina._types import WSGIEnvironment
from drakaina._types import WSGIResponse
from drakaina._types import WSGIStartResponse
from drakaina.middleware.base import BaseMiddleware
from drakaina.utils import iterable_str_arg

__all__ = ("CORSMiddleware",)

DEFAULT_HEADERS = (
    "Accept, Accept-Encoding, Accept-Language, Authorization, "
    "Content-Language, Content-Type, DNT, Origin, User-Agent, X-Requested-With"
)
ALL_METHODS = "DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT"
DEFAULT_METHODS = "GET, POST, OPTIONS"


class CORSMiddleware(BaseMiddleware):
    """Middleware for providing CORS headers and handling preflight requests.

    See: https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS

    :param allow_origin:
        The "Access-Control-Allow-Origin" header.
    :type allow_origin: Union[str, Iterable[str]]
    :param allow_methods:
        The "Access-Control-Allow-Methods" header.
        Default: "GET, POST, OPTIONS".
    :type allow_methods: Union[str, Iterable[str]]
    :param allow_headers:
        The "Access-Control-Allow-Headers" header.
        Default: "Accept, Accept-Encoding, Authorization,
        Content-Type, DNT, Origin, User-Agent, X-Requested-With".
    :type allow_headers: Union[str, Iterable[str]]
    :param allow_credentials:
        The "Access-Control-Allow-Credentials" header. Default: None.
    :type allow_credentials: bool
    :param expose_headers:
        The "Access-Control-Expose-Headers" header. Default: None.
    :type expose_headers: Union[str, Iterable[str]]
    :param max_age:
        The "Access-Control-Max-Age" header. Default: 3600 sec. (1 hour).
    :type max_age: Union[int, str]

    """

    __slots__ = (
        "_cors_headers",
        "_preflight_cors_headers",
        "_allow_origin",
        "_allow_credentials",
        "_allow_headers",
    )

    def __init__(
        self,
        app: WSGIApplication,
        allow_origin: str | Iterable[str],
        allow_methods: Optional[str | Iterable[str]] = None,
        allow_headers: Optional[str | Iterable[str]] = None,
        allow_credentials: Optional[bool] = None,
        expose_headers: Optional[str | Iterable[str]] = None,
        max_age: int = 3600,
        **kwargs,
    ):
        super().__init__(app, **kwargs)

        self._allow_origin = ", ".join(iterable_str_arg(allow_origin))

        if allow_methods:
            if "*" in allow_methods:
                _allow_methods = ALL_METHODS
            else:
                _allow_methods = ", ".join(iterable_str_arg(allow_methods))
        else:
            _allow_methods = DEFAULT_METHODS

        if allow_headers:
            self._allow_headers = ", ".join(
                sorted(
                    set(iterable_str_arg(DEFAULT_HEADERS))
                    | set(iterable_str_arg(allow_headers)),
                ),
            )
        else:
            self._allow_headers = DEFAULT_HEADERS

        if expose_headers:
            _expose_headers = ", ".join(iterable_str_arg(expose_headers))
        else:
            _expose_headers = None

        self._allow_credentials = allow_credentials

        # Prepare CORS response headers
        self._cors_headers = []
        if self._allow_credentials:
            self._cors_headers.append(
                ("Access-Control-Allow-Credentials", "true"),
            )
        if _expose_headers:
            self._cors_headers.append(
                ("Access-Control-Expose-Headers", _expose_headers),
            )

        # Prepare pre-flight CORS response headers
        self._preflight_cors_headers = [
            ("Access-Control-Allow-Methods", _allow_methods),
            ("Access-Control-Max-Age", str(max_age)),
            ("Content-Length", "0"),
        ]
        if "*" not in self._allow_origin or self._allow_credentials:
            self._preflight_cors_headers.append(("Vary", "Origin"))

        if self._allow_credentials:
            self._preflight_cors_headers.append(
                ("Access-Control-Allow-Credentials", "true"),
            )

    def __wsgi_call__(
        self,
        environ: WSGIEnvironment,
        start_response: WSGIStartResponse,
    ) -> WSGIResponse:
        if environ.get("HTTP_ORIGIN"):
            if environ.get("REQUEST_METHOD") == "OPTIONS":
                return self.options(environ, start_response)
            return self.app(
                environ,
                self._start_response_with_cors(environ, start_response),
            )
        else:
            return self.app(environ, start_response)

    async def __asgi_call__(
        self,
        scope: ASGIScope,
        receive: ASGIReceive,
        send: ASGISend,
    ):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
        ...

    def options(
        self,
        environ: WSGIEnvironment,
        start_response: WSGIStartResponse,
    ) -> WSGIResponse:
        """Response for OPTIONS request"""
        request_origin = environ["HTTP_ORIGIN"]
        request_headers = environ.get("HTTP_ACCESS_CONTROL_REQUEST_HEADERS")

        response_headers = self._preflight_cors_headers[:]

        if "*" in self._allow_origin or request_origin in self._allow_origin:
            if "*" not in self._allow_origin or self._allow_credentials:
                response_headers.append(
                    ("Access-Control-Allow-Origin", request_origin),
                )
            else:
                response_headers.append(("Access-Control-Allow-Origin", "*"))

        if "*" in self._allow_headers and request_headers is not None:
            response_headers.append(
                ("Access-Control-Allow-Headers", request_headers),
            )
        if "*" not in self._allow_headers:
            response_headers.append(
                ("Access-Control-Allow-Headers", self._allow_headers),
            )

        start_response("200 OK", response_headers)
        yield b""

    def _start_response_with_cors(
        self,
        environ: WSGIEnvironment,
        start_response: WSGIStartResponse,
    ) -> WSGIStartResponse:
        """Wraps the start_response method, and includes the CORS header
        for the specified origin.
        """
        request_origin = environ["HTTP_ORIGIN"]

        cors_headers = self._cors_headers[:]

        if "*" in self._allow_origin:
            if "HTTP_COOKIE" in environ:
                cors_headers.append(
                    ("Access-Control-Allow-Origin", request_origin),
                )
                cors_headers.append(("Vary", "Origin"))
            else:
                cors_headers.append(("Access-Control-Allow-Origin", "*"))
        elif (
            "*" not in self._allow_origin
            and request_origin in self._allow_origin
        ):
            cors_headers.append(("Access-Control-Allow-Origin", request_origin))
            cors_headers.append(("Vary", "Origin"))

        def response_with_cors(status, headers, exc_info=None):
            headers.extend(cors_headers)
            return start_response(status, headers, exc_info)

        return response_with_cors

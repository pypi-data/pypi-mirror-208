from __future__ import annotations

from logging import Logger

from drakaina._types import ASGIApplication
from drakaina._types import ASGIReceive
from drakaina._types import ASGIScope
from drakaina._types import ASGISend
from drakaina._types import WSGIApplication
from drakaina._types import WSGIEnvironment
from drakaina._types import WSGIResponse
from drakaina._types import WSGIStartResponse
from drakaina.middleware.base import BaseMiddleware
from drakaina.rpc_protocols import BaseRPCProtocol


class ExceptionMiddleware(BaseMiddleware):
    """The middleware for handling unhandled exceptions in the application
    according to the RPC protocol.

    """

    __slots__ = ("handler", "_logger")

    def __init__(
        self,
        app: ASGIApplication | WSGIApplication,
        handler: BaseRPCProtocol,
        logger: Logger | None = None,
        is_async: bool = False,
    ):
        super().__init__(app=app, is_async=is_async)

        self.handler = handler
        self._logger = logger

    def __wsgi_call__(
        self,
        environ: WSGIEnvironment,
        start_response: WSGIStartResponse,
    ) -> WSGIResponse:
        try:
            return self.app(environ, start_response)
        except Exception as error:
            if self._logger is not None:
                self._logger.exception(error)
            response_body = self.handler.get_raw_error(error)
            response_headers = [
                ("Content-Type", self.handler.content_type),
                ("Content-Length", str(len(response_body))),
            ]
            start_response("200 OK", response_headers)
            return (response_body,)

    async def __asgi_call__(
        self,
        scope: ASGIScope,
        receive: ASGIReceive,
        send: ASGISend,
    ):
        try:
            await self.app(scope, receive, send)
        except Exception as error:
            if self._logger is not None:
                self._logger.exception(error)

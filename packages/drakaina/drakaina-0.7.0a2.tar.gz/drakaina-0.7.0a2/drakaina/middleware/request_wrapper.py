from drakaina._types import ASGIReceive
from drakaina._types import ASGIScope
from drakaina._types import ASGISend
from drakaina._types import ProxyRequest
from drakaina._types import WSGIEnvironment
from drakaina._types import WSGIResponse
from drakaina._types import WSGIStartResponse
from drakaina.middleware.base import BaseMiddleware


class RequestWrapperMiddleware(BaseMiddleware):
    """The middleware for wrapping the request object.

    Provides access to the mapping environment object through
    the attribute access interface. This is needed for some
    backward compatibility in cases where the request is
    an object with attributes, such as `request.user`.

    """

    def __wsgi_call__(
        self,
        environ: WSGIEnvironment,
        start_response: WSGIStartResponse,
    ) -> WSGIResponse:
        return self.app(ProxyRequest(environ), start_response)

    async def __asgi_call__(
        self,
        scope: ASGIScope,
        receive: ASGIReceive,
        send: ASGISend,
    ):
        await self.app(ProxyRequest(scope), receive, send)

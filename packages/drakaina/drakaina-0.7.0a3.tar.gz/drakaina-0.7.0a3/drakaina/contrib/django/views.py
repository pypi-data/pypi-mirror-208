from __future__ import annotations

from functools import partial
from typing import Callable
from typing import Iterable
from typing import Optional

from django.http import HttpRequest
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseNotAllowed
from django.utils.module_loading import autodiscover_modules
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from drakaina.exceptions import BadRequestError
from drakaina.rpc_protocols import BaseRPCProtocol
from drakaina.rpc_protocols import JsonRPCv2


class RPCView(View):
    """Django class based view implements JSON-RPC"""

    http_method_names = ["post", "options"]
    handler: BaseRPCProtocol
    content_type: str

    @classmethod
    def as_view(
        cls,
        autodiscover: str | Iterable[str] = "rpc_methods",
        handler: Optional[BaseRPCProtocol] = None,
        allowed_methods: Optional[Iterable[str]] = None,
        **initkwargs,
    ) -> Callable:
        """

        :param autodiscover: The name(s) submodule(s) in a django applications
                             in which the RPC methods are defined.
        :type autodiscover: str
        :param handler: RPC protocol implementation.
        :type handler: BaseRPCProtocol
        :param allowed_methods: Allowed http methods. Default: POST, OPTIONS.
        :type allowed_methods:
        :param initkwargs:
        :return: RPCView instance.

        """
        cls.handler = handler if handler is not None else JsonRPCv2()
        cls.content_type = cls.handler.content_type
        if allowed_methods is not None:
            cls.http_method_names = allowed_methods
        view = super().as_view(**initkwargs)
        view.cls = cls

        # Scan specified sub-modules
        autodiscover_modules(autodiscover)

        return csrf_exempt(view)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        response_headers = {}
        if request.content_type != self.content_type:
            response = partial(HttpResponse, status=415)
            content = self.handler.get_raw_error(BadRequestError())
        elif len(request.body) > int(request.headers["Content-Length"]):
            response = HttpResponseBadRequest
            content = self.handler.get_raw_error(BadRequestError())
        else:
            content = self.handler.handle_raw_request(
                request.body,
                request=request,
            )
            if hasattr(request, "response"):
                _response = request.response
                if isinstance(_response, dict) and "headers" in _response:
                    for header in _response["headers"]:
                        response_headers[header[0]] = header[1]
            response = partial(HttpResponse, headers=response_headers)

        return response(content=content, content_type=self.content_type)

    def http_method_not_allowed(
        self,
        request: HttpRequest,
        *args,
        **kwargs,
    ) -> HttpResponse:
        return HttpResponseNotAllowed(
            permitted_methods=(m.upper() for m in self.http_method_names),
            content=self.handler.get_raw_error(BadRequestError()),
            content_type=self.content_type,
        )

    def options(self, request, *args, **kwargs):
        return HttpResponse(
            headers={
                "Allow": ", ".join((m.upper() for m in self.http_method_names)),
            },
        )

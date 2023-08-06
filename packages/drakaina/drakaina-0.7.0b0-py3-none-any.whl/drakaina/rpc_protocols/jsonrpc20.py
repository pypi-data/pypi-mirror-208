from __future__ import annotations

from typing import Any
from typing import ClassVar

from drakaina._types import JSONRPCRequest
from drakaina._types import JSONRPCRequestObject
from drakaina._types import JSONRPCResponse
from drakaina._types import JSONRPCResponseObject
from drakaina._types import OpenAPI
from drakaina._types import OpenRPC
from drakaina.exceptions import AuthenticationFailedError
from drakaina.exceptions import BadRequestError
from drakaina.exceptions import DeserializationError
from drakaina.exceptions import ForbiddenError
from drakaina.exceptions import InternalServerError
from drakaina.exceptions import InvalidParametersError
from drakaina.exceptions import InvalidPermissionsError
from drakaina.exceptions import InvalidTokenError
from drakaina.exceptions import NotFoundError
from drakaina.exceptions import RPCError
from drakaina.exceptions import SerializationError
from drakaina.registries import RPCRegistry
from drakaina.rpc_protocols.base import BaseRPCProtocol
from drakaina.serializers import BaseSerializer
from drakaina.serializers import JsonSerializer


class JsonRPCError(RPCError):
    """JSON-RPC Common error

    Reserved for implementation-defined server-errors.
    Codes -32000 to -32099.

    """

    code: int = -32000
    default_message: str = "Server error"
    id: int | str = None
    data: Any = None

    def __init__(
        self,
        *args,
        message: str = None,
        id: int | str = None,
        data: Any | None = None,
    ):
        super().__init__(*args)

        self.id = id
        if message:
            self.message = message

        if self.message and data:
            self.data = {"text": self.message.strip(), "details": data}
        elif self.message:
            self.data = self.message.strip()
        elif data:
            self.data = data

    def __str__(self) -> str:
        return f"{self.__class__.__name__} ({self.code} {self.default_message})"

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} ({self.code} {self.default_message})>"
        )

    def as_dict(self) -> JSONRPCResponseObject:
        error = dict(
            jsonrpc="2.0",
            error={"code": self.code, "message": self.default_message},
            id=self.id,
        )

        if self.data:
            error["error"]["data"] = self.data

        return error


class InvalidRequestError(JsonRPCError):
    """Invalid Request

    The JSON sent is not a valid Request object.

    """

    code = -32600
    default_message = "Invalid Request"


class MethodNotFoundError(JsonRPCError):
    """Method not found

    The method does not exist / is not available.

    """

    code = -32601
    default_message = "Method not found"


class InvalidParamsError(JsonRPCError):
    """Invalid params

    Invalid method parameter(s).

    """

    code = -32602
    default_message = "Invalid params"


class InternalError(JsonRPCError):
    """Internal error

    Internal JSON-RPC error.

    """

    code = -32603
    default_message = "Internal error"


class ParseError(JsonRPCError):
    """Parse error

    Invalid JSON was received by the server.
    An error occurred on the server while parsing the JSON text.

    """

    code = -32700
    default_message = "Parse error"


# Implementation of Drakaina errors


class AuthenticationFailedJRPCError(JsonRPCError):
    """Authentication failed"""

    code = -32010
    default_message = "Authentication failed"


class InvalidTokenJRPCError(AuthenticationFailedJRPCError):
    """Invalid token error"""

    code = -32011
    default_message = "Invalid token"


class ForbiddenJRPCError(AuthenticationFailedJRPCError):
    """Forbidden error"""

    code = -32012
    default_message = "Forbidden"


class InvalidPermissionsJRPCError(ForbiddenJRPCError):
    """Invalid permissions error"""

    code = -32013
    default_message = "Invalid permissions"


class JsonRPCv2(BaseRPCProtocol):
    """JSON-RPC 2.0 implementation.

    :param registry:
        Registry of remote procedures.
        Default: `drakaina.registries.rpc_registry` (generic module instance)
    :param serializer:
        Serializer object. Default: `JsonSerializer` (stdlib.json)
    :param schema_serializer:
        The serializer object to serialize the schema.
        Default: `JsonSerializer` (stdlib.json)
    :param openrpc:
        An object (TypedDict) of OpenRPC containing general information,
        information about the server(s). It must not contain a method schema.
    :param openapi:
        An object (TypedDict) of OpenAPI containing general information,
        information about the server(s). It must not contain a paths schema.

    """

    __slots__ = ("allow_service_discovery", "schema_url")

    base_error_class: ClassVar = JsonRPCError
    """Base class for JSON-RPC 2.0 protocol implementation."""

    default_error_class: ClassVar = InternalError
    """Default JSON-RPC 2.0 error class to represent internal exceptions."""

    _errors_map: ClassVar = {
        Exception: JsonRPCError,
        RPCError: JsonRPCError,
        BadRequestError: InvalidRequestError,
        NotFoundError: MethodNotFoundError,
        InvalidParametersError: InvalidParamsError,
        InternalServerError: InternalError,
        SerializationError: InternalError,
        DeserializationError: ParseError,
        AuthenticationFailedError: AuthenticationFailedJRPCError,
        InvalidTokenError: InvalidTokenJRPCError,
        ForbiddenError: ForbiddenJRPCError,
        InvalidPermissionsError: InvalidPermissionsJRPCError,
    }

    def __init__(
        self,
        registry: RPCRegistry | None = None,
        serializer: BaseSerializer | None = None,
        schema_serializer: BaseSerializer | None = None,
        openrpc: OpenRPC | None = None,
        openapi: OpenAPI | None = None,
        allow_service_discovery: bool | None = None,
        schema_url: str | None = None,
    ):
        if serializer is None:
            serializer = JsonSerializer()

        super().__init__(
            registry=registry,
            serializer=serializer,
            schema_serializer=schema_serializer,
            openrpc=openrpc,
            openapi=openapi,
        )
        self.allow_service_discovery = allow_service_discovery
        self.schema_url = schema_url

        if allow_service_discovery:
            assert self.schema_url, "You must specify schema url."
            self.registry.register_rpc_extension(
                extension_procedure=self.rpc_discover,
                extension_name="rpc.discover",
            )

    def handle(
        self,
        rpc_request: JSONRPCRequest,
        request: Any | None = None,
    ) -> JSONRPCResponse | None:
        """Handles a procedure call or batch of procedure call

        :param rpc_request:
            RPC request in protocol format.
        :type rpc_request: JSONRPCRequest
        :param request:
            Optional parameter that can be passed as an
            argument to the procedure.
        :type request: Any
        :return:
            Returns the result in protocol format.
        :rtype: JSONRPCResponse

        """
        # Check bad request
        if not (isinstance(rpc_request, (dict, list)) and len(rpc_request) > 0):
            return InvalidRequestError().as_dict()

        # Handle batch request
        if isinstance(rpc_request, list):
            batch_result = []
            for request_object in rpc_request:
                result = self.execute(request_object, request=request)
                if result is not None:
                    batch_result.append(result)
            if len(batch_result) == 0:
                return None
            return batch_result

        # Handle single request
        return self.execute(rpc_request, request=request)

    def execute(
        self,
        procedure_call: JSONRPCRequestObject,
        request: Any | None = None,
    ) -> JSONRPCResponseObject | None:
        """Execute a remote procedure call.

        :param procedure_call:
            RPC request object in protocol format.
        :type procedure_call: JSONRPCRequestObject
        :param request:
            Optional parameter that can be passed as an
            argument to the procedure. By default, None will be passed.
        :type request: Any
        :return:
            Returns a result object in protocol format.
        :rtype: JSONRPCResponseObject

        """
        if not isinstance(procedure_call, dict):
            return InvalidRequestError().as_dict()
        method: str = procedure_call.get("method")
        params: list | dict | None = procedure_call.get("params")
        request_id: int | str | None = procedure_call.get("id")

        # Validate protocol
        if (
            procedure_call.get("jsonrpc") != "2.0"
            or not isinstance(method, str)
            or not (params is None or isinstance(params, (list, dict)))
            or not (request_id is None or isinstance(request_id, (int, str)))
        ):
            return InvalidRequestError(id=request_id).as_dict()

        # Getting procedure
        procedure = self.registry[method]
        if procedure is None:
            if request_id is None:
                return None
            return MethodNotFoundError(id=request_id).as_dict()

        # Prepare parameters
        args, kwargs = (), {}
        if params is not None:
            if isinstance(params, list):
                args = (request, *params)
            elif isinstance(params, dict):
                kwargs = dict(request=request, **params)
        else:
            kwargs = dict(request=request)

        # Execute RPC method
        try:
            result = procedure(*args, **kwargs)
        except RPCError as err:
            error = self.handle_error(err)
            error.id = request_id
            return error.as_dict()
        except Exception as err:
            return InternalError(message=str(err), id=request_id).as_dict()

        if request_id is None:
            return None

        return dict(jsonrpc="2.0", result=result, id=request_id)

    def rpc_discover(self) -> dict[str, Any]:
        """Returns an OpenRPC schema as a description of this service.

        :return:

        """
        if self.schema_url is not None:
            schema = {"$ref": self.schema_url}
        else:
            schema = self.openrpc_schema()

        return {"name": "OpenRPC Schema", "schema": schema}

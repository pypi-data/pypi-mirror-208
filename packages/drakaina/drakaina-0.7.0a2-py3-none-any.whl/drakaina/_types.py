from __future__ import annotations

from collections import OrderedDict
from collections.abc import Awaitable
from collections.abc import Callable
from collections.abc import Mapping
from collections.abc import MutableMapping
from collections.abc import MutableSequence
from collections.abc import Sequence
from sys import version_info
from typing import Any
from typing import Iterable
from typing import Tuple
from typing import Type
from typing import Union

if version_info < (3, 8):
    from typing_extensions import Literal
    from typing_extensions import Protocol
    from typing_extensions import TypedDict
else:
    from typing import Literal
    from typing import Protocol
    from typing import TypedDict

if version_info < (3, 10):
    from typing_extensions import TypeAlias
else:
    from typing import TypeAlias

if version_info < (3, 11):
    from typing_extensions import NotRequired
else:
    from typing import NotRequired


"""
JSON-RPC types definitions
"""

JSONSimpleTypes: TypeAlias = Union[str, int, float, bool, None]
JSONTypes: TypeAlias = Union[
    JSONSimpleTypes,
    Mapping[str, JSONSimpleTypes],
    Sequence[JSONSimpleTypes],
]


class JSONRPCRequestObject(TypedDict):
    jsonrpc: Literal["2.0"]
    method: str
    params: NotRequired[list[JSONTypes] | dict[str, JSONTypes]]
    id: NotRequired[str | int | None]


class JSONRPCErrorObject(TypedDict):
    code: int
    message: str
    data: NotRequired[JSONTypes]


class JSONRPCResponseObject(TypedDict):
    jsonrpc: Literal["2.0"]
    result: NotRequired[JSONTypes]
    error: NotRequired[JSONRPCErrorObject]
    id: str | int | None


JSONRPCBatchRequestObject: TypeAlias = Sequence[JSONRPCRequestObject]
JSONRPCRequest: TypeAlias = Union[
    JSONRPCRequestObject,
    JSONRPCBatchRequestObject,
]
JSONRPCBatchResponseObject: TypeAlias = Sequence[JSONRPCResponseObject]
JSONRPCResponse: TypeAlias = Union[
    JSONRPCResponseObject,
    JSONRPCBatchResponseObject,
]


"""
Schema types
"""


schema_mapping = {
    "None": "null",
    None: "null",
    "bool": "boolean",
    bool: "boolean",
    "int": "integer",
    int: "integer",
    "float": "number",
    float: "number",
    "str": "string",
    str: "string",
    "list": "array",
    list: "array",
    "dict": "object",
    dict: "object",
}


class Schema(dict):
    """JSON schema.

    type: str
    description: str
    """

    schema_mapping = schema_mapping


Reference: TypeAlias = TypedDict(
    "Reference",
    {
        "$ref": str,  # noqa
        "summary": NotRequired[str],
        "description": NotRequired[str],
    },
)


class ParameterSchema(TypedDict):
    name: NotRequired[str]
    description: NotRequired[str]
    type: NotRequired[str]
    default: NotRequired[Any]
    required: NotRequired[bool]
    """Default: False"""
    deprecated: NotRequired[bool]
    """Default: False"""


class MethodSchema(TypedDict):
    name: NotRequired[str]
    short_description: NotRequired[str]
    description: NotRequired[str]
    parameters: NotRequired[OrderedDict[str, ParameterSchema]]
    result: NotRequired[ParameterSchema]
    deprecated: NotRequired[bool]
    errors: NotRequired[dict[str, str]]


"""
Schema types - OpenRPC
https://spec.open-rpc.org/
"""

SUPPORTED_OPENRPC_VERSION = "1.2.1"


class OpenRPC(TypedDict):
    openrpc: Literal["1.2.1"]
    info: ORPCInfo
    methods: list[ORPCMethod | Reference]
    servers: NotRequired[list[ORPCServer]]
    components: NotRequired[ORPCComponents]
    externalDocs: NotRequired[ORPCExtDoc]


class ORPCInfo(TypedDict):
    title: str
    version: str
    description: NotRequired[str]
    termsOfService: NotRequired[str]
    contact: NotRequired[ORPCContact]
    license: NotRequired[ORPCLicense]


class ORPCContact(TypedDict):
    name: NotRequired[str]
    url: NotRequired[str]
    email: NotRequired[str]


class ORPCLicense(TypedDict):
    name: str
    url: NotRequired[str]


class ORPCServer(TypedDict):
    name: str
    url: str
    """Runtime Expression"""
    summary: NotRequired[str]
    description: NotRequired[str]
    variables: NotRequired[Mapping[str, ORPCServerVar]]


class ORPCServerVar(TypedDict):
    default: str
    enum: NotRequired[list[str]]
    description: NotRequired[str]


class ORPCMethod(TypedDict):
    name: str
    params: list[ORPCContentDescriptor | Reference]
    result: NotRequired[ORPCContentDescriptor | Reference]
    tags: NotRequired[list[ORPCTag | Reference]]
    summary: NotRequired[str]
    description: NotRequired[str]
    externalDocs: NotRequired[ORPCExtDoc]
    deprecated: NotRequired[bool]
    """Default: False"""
    servers: NotRequired[list[ORPCServer]]
    errors: NotRequired[list[JSONRPCErrorObject | Reference]]
    links: NotRequired[list[ORPCLink | Reference]]
    paramStructure: NotRequired[Literal["by-name", "by-position", "either"]]
    examples: NotRequired[list[ORPCExamplePairing]]


class ORPCContentDescriptor(TypedDict):
    name: str
    schema: Schema
    summary: NotRequired[str]
    description: NotRequired[str]
    required: NotRequired[bool]
    """Default: False"""
    deprecated: NotRequired[bool]
    """Default: False"""


class ORPCExamplePairing(TypedDict):
    name: NotRequired[str]
    summary: NotRequired[str]
    description: NotRequired[str]
    params: NotRequired[list[ORPCExample | Reference]]
    result: NotRequired[ORPCExample | Reference]


class ORPCExample(TypedDict):
    name: NotRequired[str]
    summary: NotRequired[str]
    description: NotRequired[str]
    value: NotRequired[Any]
    externalValue: NotRequired[str]


class ORPCLink(TypedDict):
    name: str
    summary: NotRequired[str]
    description: NotRequired[str]
    method: NotRequired[str]
    params: NotRequired[Mapping[str, Any | str]]
    """Mapping[str, Any | 'Runtime Expression']"""
    server: NotRequired[ORPCServer]


class ORPCComponents(TypedDict):
    contentDescriptors: NotRequired[Mapping[str, ORPCContentDescriptor]]
    schemas: NotRequired[Mapping[str, Schema]]
    examples: NotRequired[Mapping[str, ORPCExample]]
    links: NotRequired[Mapping[str, ORPCLink]]
    errors: NotRequired[Mapping[str, JSONRPCErrorObject]]
    examplePairingObjects: NotRequired[Mapping[str, ORPCExamplePairing]]
    tags: NotRequired[Mapping[str, ORPCTag]]


class ORPCTag(TypedDict):
    name: str
    summary: NotRequired[str]
    description: NotRequired[str]
    externalDocs: NotRequired[ORPCExtDoc]


class ORPCExtDoc(TypedDict):
    url: str
    description: NotRequired[str]


"""
Schema types - OpenAPI
https://github.com/OAI/OpenAPI-Specification
"""

SUPPORTED_OPENAPI_VERSION = "3.1.0"


class OpenAPI(TypedDict):
    openapi: Literal["3.1.0"]
    info: dict


"""
WSGI types definitions
PEP 3333 – Python Web Server Gateway Interface
https://peps.python.org/pep-3333/
"""

WSGIEnvironmentKeys: TypeAlias = Literal[
    # for CGI
    # https://datatracker.ietf.org/doc/html/draft-coar-cgi-v11-03
    "AUTH_TYPE",
    "CONTENT_LENGTH",
    "CONTENT_TYPE",
    "GATEWAY_INTERFACE",
    "PATH_INFO",
    "PATH_TRANSLATED",
    "QUERY_STRING",
    "REMOTE_ADDR",
    "REMOTE_HOST",
    "REMOTE_IDENT",
    "REMOTE_USER",
    "REQUEST_METHOD",
    "SCRIPT_NAME",
    "SERVER_NAME",
    "SERVER_PORT",
    "SERVER_PROTOCOL",
    "SERVER_SOFTWARE",
    # for WSGI
    "wsgi.errors",
    "wsgi.input",
    "wsgi.multiprocess",
    "wsgi.multithread",
    "wsgi.run_once",
    "wsgi.url_scheme",
    "wsgi.version",
]
# for framework needs
WSGIDrakainaKeys: TypeAlias = Literal[
    "drakaina.app",
    "drakaina.is_authenticated",
]
WSGIEnvironment: TypeAlias = MutableMapping[str, Any]
WSGIExceptionInfo: TypeAlias = Tuple[Type[BaseException], BaseException, Any]


class WSGIStartResponse(Protocol):
    def __call__(
        self,
        status: str,
        headers: MutableSequence[tuple[str, str]],
        exc_info: WSGIExceptionInfo | None = ...,
    ) -> Callable[[bytes], Any]:
        ...


WSGIResponse: TypeAlias = Iterable[bytes]
WSGIApplication: TypeAlias = Callable[
    [WSGIEnvironment, WSGIStartResponse],
    WSGIResponse,
]


class WSGIInputStream(Protocol):
    def read(self, size: int | None = None) -> bytes:
        ...

    def readline(self) -> bytes:
        ...

    def readlines(self, hint: Any | None) -> Iterable[bytes]:
        ...

    def __iter__(self) -> bytes:
        ...


class WSGIErrorsStream(Protocol):
    def flush(self) -> None:
        ...

    def write(self, s: str) -> None:
        ...

    def writelines(self, seq: Sequence[str]) -> None:
        ...


"""
ASGI types definitions
https://asgi.readthedocs.io/en/latest/
"""

ASGIScope: TypeAlias = MutableMapping[str, Any]
ASGIMessage: TypeAlias = MutableMapping[str, Any]

ASGIReceive: TypeAlias = Callable[[], Awaitable[ASGIMessage]]
ASGISend: TypeAlias = Callable[[ASGIMessage], Awaitable[None]]

ASGIApplication: TypeAlias = Callable[
    [ASGIScope, ASGIReceive, ASGISend],
    Awaitable[None],
]


"""
Helpful types
"""


class Comparator(Protocol):
    def __call__(
        self,
        required: Iterable[str],
        provided: str | Iterable[str],
    ) -> bool:
        ...


class ProxyRequest(MutableMapping):
    """A wrapper class for environment mapping.

    :param environment:

    """

    __slots__ = ("__environment",)

    def __init__(self, environment: ASGIScope | WSGIEnvironment):
        self.__environment = environment

    def __getitem__(self, item):
        return self.__environment[item]

    def __setitem__(self, key, value):
        self.__environment[key] = value

    def __delitem__(self, key):
        del self.__environment[key]

    def __iter__(self):
        return iter(self.__environment.keys())

    def __contains__(self, item):
        return item in self.__environment.keys()

    def __len__(self):
        return len(self.__environment)

    def keys(self):
        return self.__environment.keys()

    def values(self):
        return self.__environment.values()

    def items(self):
        return self.__environment.items()

    def get(self, key, default=None):
        return self.__environment.get(key, default)

    def clear(self):
        self.__environment.clear()

    def setdefault(self, key, default=None):
        self.__environment.setdefault(key, default)

    def pop(self, key, default=None):
        return self.__environment.pop(key, default)

    def popitem(self):
        return self.__environment.popitem()

    def copy(self):
        return self.__class__(self.__environment.copy())

    def update(self, *args, **kwargs):
        return self.__environment.update(*args, **kwargs)

    def __getattr__(self, item):
        if item in ("__environment", "_ProxyRequest__environment"):
            super().__getattribute__(item)
        return self.__environment[item]

    def __setattr__(self, key, value):
        if key in ("__environment", "_ProxyRequest__environment"):
            super().__setattr__(key, value)
        else:
            self.__environment[key] = value

    def __delattr__(self, item):
        del self.__environment[item]


AnyRequest: TypeAlias = Union[
    ASGIScope,
    WSGIEnvironment,
    ProxyRequest,
]

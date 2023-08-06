from __future__ import annotations

from asyncio import iscoroutinefunction
from functools import update_wrapper
from typing import Any
from typing import Callable
from typing import Iterable
from typing import MutableMapping
from typing import Optional
from typing import TypeVar

from drakaina._types import AnyRequest
from drakaina._types import Comparator
from drakaina.exceptions import AuthenticationFailedError
from drakaina.exceptions import ForbiddenError
from drakaina.registries import RPC_REGISTRY
from drakaina.registries import RPCRegistry
from drakaina.utils import iterable_str_arg

__all__ = (
    "RPCRegistry",
    "rpc_registry",
    "remote_procedure",
    "check_permissions",
    "login_required",
    "match_all",
    "match_any",
    "ENV_APP",
    "ENV_IS_AUTHENTICATED",
    "ENV_USER",
    "ENV_USER_ID",
    "ENV_AUTH_PAYLOAD",
    "ENV_AUTH_SCOPES",
)

# General registry
rpc_registry = RPCRegistry()

# Environ (Request) context
ENV_APP = "drakaina.app"
ENV_IS_AUTHENTICATED = "auth.is_authenticated"
ENV_USER = "user"
ENV_USER_ID = "user_id"
ENV_AUTH_PAYLOAD = "auth.payload"
ENV_AUTH_SCOPES = "auth.scopes"

T = TypeVar("T", bound=Callable)


def remote_procedure(
    name: Optional[str] = None,
    registry: Optional[RPCRegistry] = None,
    provide_request: Optional[bool] = None,
    metadata: Optional[dict[str, Any]] = None,
    **meta_options,
) -> Callable:
    """Decorator allow wrap function and define it as remote procedure.

    :param name:
        Procedure name. Default as function name.
    :type name: str
    :param registry:
        Procedure registry custom object
    :type registry: RPCRegistry
    :param provide_request:
        Provide a request object or context data (from the transport layer).
        If `True`, then the request object or context can be supplied to
        the procedure as a `request` argument.
    :type provide_request: bool
    :param metadata:
        Metadata that can be processed by middleware.
    :type metadata: dict[str, Any]
    :param meta_options:
        Metadata that can be processed by middleware.

    """

    def __decorator(
        procedure: T,
        _registry: RPCRegistry = None,
        _name: str = None,
        _provide_request: bool = None,
        _metadata: dict | None = None,
    ) -> T:
        """Returns a registered procedure"""

        if iscoroutinefunction(procedure):

            async def wrapper(*args, **kwargs):
                if not _provide_request:
                    if len(args) == 0:
                        kwargs.pop("request")
                    else:
                        scope, *args = args
                return await procedure(*args, **kwargs)

        else:

            def wrapper(*args, **kwargs):
                if not _provide_request:
                    if len(args) == 0:
                        kwargs.pop("request")
                    else:
                        environ, *args = args
                return procedure(*args, **kwargs)

        # Need to update the wrapper before registering in the registry
        decorated_procedure = update_wrapper(wrapper, procedure)

        if _registry is None:
            _registry = rpc_registry
        if _name is None:
            _name = procedure.__name__
        _registry.register_procedure(
            decorated_procedure,
            name=_name,
            provide_request=_provide_request,
            metadata=_metadata,
        )

        return decorated_procedure

    if callable(name):
        return __decorator(
            procedure=name,
            _registry=registry,
            _name=None,
            _provide_request=provide_request,
            _metadata={**(metadata or {}), **meta_options},
        )
    elif not isinstance(name, (str, type(None))):
        raise TypeError(
            "Expected first argument to be an str, a callable, or None",
        )

    def decorator(procedure):
        assert callable(procedure)
        return __decorator(
            procedure=procedure,
            _registry=registry,
            _name=name,
            _provide_request=provide_request,
            _metadata={**(metadata or {}), **meta_options},
        )

    return decorator


def login_required(*_args) -> Callable:
    """Requires login decorator.

    Gives access to the procedure only to authenticated users.

    """

    def __decorator(procedure: T) -> T:
        """Returns a registered procedure"""
        registry: RPCRegistry = getattr(procedure, RPC_REGISTRY, None)
        if registry is None:
            raise TypeError(
                "Incorrect usage of decorator. Please use "
                "the `drakaina.remote_procedure` decorator first.",
            )

        if iscoroutinefunction(procedure):

            async def wrapper(*args, **kwargs):
                request = _get_request(*args, **kwargs)
                if not _is_authenticated(request):
                    raise ForbiddenError("Authentication required")

                return await procedure(*args, **kwargs)

        else:

            def wrapper(*args, **kwargs):
                request = _get_request(*args, **kwargs)
                if not _is_authenticated(request):
                    raise ForbiddenError("Authentication required")

                return procedure(*args, **kwargs)

        wrapper = update_wrapper(wrapper, procedure)
        registry.replace(procedure, wrapper)
        return wrapper

    if len(_args) > 0:
        if callable(_args[0]):
            return __decorator(_args[0])
        else:
            raise TypeError("Expected first argument to be a callable")

    def decorator(procedure):
        assert callable(procedure)
        return __decorator(procedure)

    return decorator


def match_any(required: Iterable[str], provided: str | Iterable[str]) -> bool:
    return any((scope in provided for scope in required))


def match_all(required: Iterable[str], provided: str | Iterable[str]) -> bool:
    return set(required).issubset(set(provided))


def check_permissions(
    scopes: str | Iterable[str],
    comparator: Comparator = match_all,
) -> Callable:
    """Permission decorator.

    Gives access to the procedure only to authorized users.

    """
    if not (
        isinstance(scopes, str)
        or (
            isinstance(scopes, Iterable)
            and all((isinstance(scope, str) for scope in scopes))
        )
    ):
        raise TypeError(
            "The `scopes` argument must be a string or Iterable[string]",
        )
    if not callable(comparator):
        raise TypeError(
            "The `comparator` argument must be a function that implements "
            "the Comparator interface",
        )

    procedure_scopes = iterable_str_arg(scopes)

    def __decorator(procedure: T) -> T:
        registry: RPCRegistry = getattr(procedure, RPC_REGISTRY, None)
        if registry is None:
            raise TypeError(
                "Incorrect usage of decorator. Please use "
                "the `drakaina.remote_procedure` decorator first.",
            )

        if iscoroutinefunction(procedure):

            async def wrapper(*args, **kwargs):
                request = _get_request(*args, **kwargs)  # noqa

                if not _is_authenticated(request):
                    raise ForbiddenError("Authentication required")

                user_scopes = _get_scopes(request)
                if not isinstance(user_scopes, Iterable):
                    raise AuthenticationFailedError(
                        "Invalid permissions format",
                    )

                if not comparator(procedure_scopes, user_scopes):
                    raise ForbiddenError("Forbidden")

                return await procedure(*args, **kwargs)

        else:

            def wrapper(*args, **kwargs):
                request = _get_request(*args, **kwargs)  # noqa

                if not _is_authenticated(request):
                    raise ForbiddenError("Authentication required")

                user_scopes = _get_scopes(request)
                if not isinstance(user_scopes, Iterable):
                    raise AuthenticationFailedError(
                        "Invalid permissions format",
                    )

                if not comparator(procedure_scopes, user_scopes):
                    raise ForbiddenError("Forbidden")

                return procedure(*args, **kwargs)

        wrapper = update_wrapper(wrapper, procedure)
        registry.replace(procedure, wrapper)
        return wrapper

    return __decorator


def _get_request(*args, **kwargs) -> Optional[AnyRequest]:
    if len(args) == 0:
        return kwargs.get("request")
    else:
        return args[0]


def _is_authenticated(request: AnyRequest) -> bool:
    if isinstance(request, (dict, MutableMapping)):
        return request.get(ENV_IS_AUTHENTICATED, False)
    else:
        return getattr(request, ENV_IS_AUTHENTICATED, False)


def _get_scopes(request: AnyRequest) -> Optional[Iterable[str]]:
    if isinstance(request, (dict, MutableMapping)):
        scopes = request.get(ENV_AUTH_SCOPES, None)
    else:
        scopes = getattr(request, ENV_AUTH_SCOPES, None)
    if scopes is not None:
        return iterable_str_arg(scopes)

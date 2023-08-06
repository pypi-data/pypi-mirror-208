from __future__ import annotations

from typing import Any
from typing import Optional
from typing import Protocol

from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.http import HttpResponse
from django.utils.module_loading import import_string

from drakaina import ENV_AUTH_PAYLOAD
from drakaina import ENV_AUTH_SCOPES
from drakaina import ENV_IS_AUTHENTICATED
from drakaina import ENV_USER_ID
from drakaina.contrib import django as default_settings
from drakaina.contrib.django.views import RPCView
from drakaina.contrib.jwt.errors import InvalidJWTTokenError
from drakaina.contrib.jwt.utils import decode_jwt_token
from drakaina.exceptions import AuthenticationFailedError
from drakaina.exceptions import ForbiddenError

__all__ = ("JWTAuthenticationMiddleware",)

UserModel = get_user_model()
ARG_PREFIX = "DRAKAINA_"


class DjangoRPCView(Protocol):
    cls: RPCView

    def __call__(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        ...


def get_settings_arg(settings_attribute: str) -> Any:
    return getattr(
        settings,
        ARG_PREFIX + settings_attribute,
        getattr(default_settings, settings_attribute, None),
    )


class JWTAuthenticationMiddleware:
    """The middleware supporting JWT tokens.

    This middleware uses with `RPCView`.
    For configure this middleware define in settings module

    """

    csrf_exempt = True

    def __init__(self, view: DjangoRPCView):
        assert hasattr(
            view.cls,
            "handler",
        ), "The view must contain the BaseRPCProtocol implementation instance."

        self._rpc_view = view
        self._rpc_handler = view.cls.handler

        self.credentials_required = get_settings_arg("CREDENTIALS_REQUIRED")
        self.prefix = get_settings_arg("JWT_PREFIX")
        self.cookie_key = get_settings_arg("JWT_COOKIE_KEY")
        self.use_cookies = get_settings_arg("JWT_USE_COOKIES")
        self.algorithms = get_settings_arg("JWT_ALGORITHMS")
        secret_key = get_settings_arg("JWT_SECRET_KEY")
        public_key = get_settings_arg("JWT_PUBLIC_KEY")
        self.__verify_key = secret_key or public_key
        self.decode_options = get_settings_arg("JWT_DECODE_OPTIONS")
        self.verify_values = get_settings_arg("JWT_VERIFY_VALUES")
        self.leeway = get_settings_arg("JWT_LEEWAY")
        self.user_id_field = get_settings_arg("JWT_USER_ID_FIELD")

        self.get_token = self._get_token
        token_getter = get_settings_arg("JWT_TOKEN_GETTER")
        if token_getter:
            self.get_token = import_string(token_getter)

        self.get_user = self._get_user
        user_getter = get_settings_arg("JWT_USER_GETTER")
        if user_getter:
            self.get_user = import_string(user_getter)

        self.get_scopes = None
        scopes_getter = get_settings_arg("JWT_SCOPES_GETTER")
        if scopes_getter:
            self.get_scopes = import_string(scopes_getter)

        self.token_is_revoked = None
        revoke_checker = get_settings_arg("JWT_REVOKE_CHECKER")
        if revoke_checker:
            self.token_is_revoked = import_string(revoke_checker)

    def __call__(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        try:
            token = self.get_token(request)
        except Exception as error:
            return self._error_response(error)

        if not token and self.credentials_required:
            return self._error_response(
                AuthenticationFailedError("Credential required"),
            )

        if token is not None:
            payload = decode_jwt_token(
                token,
                algorithms=self.algorithms,
                verify_key=self.__verify_key,
                verify=True,
                decode_options=self.decode_options,
                verify_values=self.verify_values,
                leeway=self.leeway,
            )

            if callable(self.token_is_revoked):
                if self.token_is_revoked(request, payload):
                    return self._error_response(
                        ForbiddenError("Token is revoked"),
                    )

            setattr(request, ENV_USER_ID, payload[self.user_id_field])
            setattr(request, ENV_IS_AUTHENTICATED, True)
            setattr(request, ENV_AUTH_PAYLOAD, payload)

            if callable(self.get_user):
                request.user = self.get_user(request, payload)
            if callable(self.get_scopes):
                setattr(
                    request,
                    ENV_AUTH_SCOPES,
                    self.get_scopes(request, payload),
                )

        return self._rpc_view(request, *args, **kwargs)

    def _get_token(self, request: HttpRequest) -> Optional[str]:
        if self.use_cookies:
            return request.COOKIES.get(self.cookie_key)
        else:
            auth_header = request.headers.get("Authorization")
            if auth_header is None:
                return None

            try:
                parts = auth_header.strip().split(" ")
            except ValueError:
                raise AuthenticationFailedError(
                    "Invalid `Authorization` header",
                )

            if len(parts) == 0 or parts[0] not in self.prefix:
                return None

            if len(parts) != 2:
                raise InvalidJWTTokenError(
                    "The `Authorization` header must contain two values "
                    "separated by a space",
                )

            return parts[1]

    def _get_user(
        self,
        request: HttpRequest,
        payload: dict[str, Any],
    ) -> Optional[UserModel]:
        user_id = payload.get(self.user_id_field)
        if user_id is None:
            return getattr(request, "user", None)
        return UserModel.objects.get(pk=user_id)

    def _error_response(self, error: Exception) -> HttpResponse:
        return HttpResponse(
            content=self._rpc_handler.get_raw_error(error),
            content_type=self._rpc_handler.content_type,
        )

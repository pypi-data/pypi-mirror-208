from drakaina.contrib.django.middleware import JWTAuthenticationMiddleware
from drakaina.contrib.django.views import RPCView
from drakaina.contrib.jwt import SUPPORTED_ALGORITHMS

__all__ = (
    "JWTAuthenticationMiddleware",
    "RPCView",
    "CREDENTIALS_REQUIRED",
    "JWT_ALGORITHMS",
    "JWT_SECRET_KEY",
    "JWT_PUBLIC_KEY",
    "JWT_PREFIX",
    "JWT_USE_COOKIES",
    "JWT_COOKIE_KEY",
    "JWT_DECODE_OPTIONS",
    "JWT_VERIFY_VALUES",
    "JWT_LEEWAY",
    "JWT_USER_ID_FIELD",
    "JWT_TOKEN_GETTER",
    "JWT_USER_GETTER",
    "JWT_SCOPES_GETTER",
    "JWT_REVOKE_CHECKER",
)


# Settings default values
# ❗ : In settings.py your django project use `DRAKAINA_` prefix

CREDENTIALS_REQUIRED = True
JWT_ALGORITHMS = SUPPORTED_ALGORITHMS
JWT_SECRET_KEY = None
JWT_PUBLIC_KEY = None
JWT_PREFIX = "Bearer"
JWT_USE_COOKIES = False
JWT_COOKIE_KEY = "jwt"
JWT_DECODE_OPTIONS = {
    "require": [],
    "verify_iss": False,
    "verify_aud": False,
    "verify_exp": True,
    "verify_nbf": False,
    "verify_iat": True,
    "verify_jti": False,
}
JWT_VERIFY_VALUES = {}
JWT_LEEWAY = 0
JWT_USER_ID_FIELD = "user_id"
JWT_TOKEN_GETTER = None
JWT_USER_GETTER = None
JWT_SCOPES_GETTER = None
JWT_REVOKE_CHECKER = None

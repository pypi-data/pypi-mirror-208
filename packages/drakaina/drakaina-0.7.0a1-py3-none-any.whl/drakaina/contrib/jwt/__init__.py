"""Submodule with implementations support of JSON Web Tokens

Standard: https://www.rfc-editor.org/rfc/rfc7519
"""

__all__ = (
    "RESERVED_FIELDS",
    "SUPPORTED_ALGORITHMS",
)

RESERVED_FIELDS = ("iss", "sub", "aud", "exp", "nbf", "iat", "jti")  # RFC7519
RESERVED_FIELDS = RESERVED_FIELDS + ("jtt", "scp")  # Drakaina
SUPPORTED_ALGORITHMS = ("HS256", "HS384", "HS512", "RS256", "RS384", "RS512")

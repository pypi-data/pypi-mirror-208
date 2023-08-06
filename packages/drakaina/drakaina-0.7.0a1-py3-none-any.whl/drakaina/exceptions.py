"""Base exceptions module"""


class RPCError(Exception):
    """Base error class for RPC protocols"""

    message: str = None

    def __init__(self, *args):
        super().__init__(*args)
        if len(args) > 0:
            self.message = str(args[0])

    def __str__(self) -> str:
        return f"{self.__class__.__name__} ({self.message})"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} ({self.message})>"

    def as_dict(self) -> dict[str, str]:
        return {
            "error": self.__class__.__name__,
            "message": self.message or "",
        }


class SerializationError(RPCError):
    """Serialization error"""


class DeserializationError(RPCError):
    """Deserialization error"""


class BadRequestError(RPCError):
    """Bad request error"""


class NotFoundError(RPCError):
    """Not found error"""


class InvalidParametersError(RPCError):
    """Invalid parameters error"""


class AuthenticationFailedError(RPCError):
    """Authentication failed"""


class InvalidTokenError(AuthenticationFailedError):
    """Invalid token error"""


class ForbiddenError(AuthenticationFailedError):
    """Forbidden error"""


class InvalidPermissionsError(ForbiddenError):
    """Invalid permissions error"""


class InternalServerError(RPCError):
    """Server error"""

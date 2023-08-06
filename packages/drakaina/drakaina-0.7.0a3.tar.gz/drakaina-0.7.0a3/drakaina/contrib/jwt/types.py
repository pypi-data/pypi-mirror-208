from __future__ import annotations

from typing import Any
from typing import Iterable
from typing import Optional
from typing import Protocol

from drakaina._types import ASGIScope
from drakaina._types import WSGIEnvironment


class TokenGetter(Protocol):
    def __call__(
        self,
        request: ASGIScope | WSGIEnvironment,
    ) -> Optional[str]:
        ...


class ScopesGetter(Protocol):
    def __call__(
        self,
        request: ASGIScope | WSGIEnvironment,
        payload: dict[str, Any],
    ) -> Optional[str, Iterable[str]]:
        ...


class RevokeChecker(Protocol):
    def __call__(
        self,
        request: ASGIScope | WSGIEnvironment,
        payload: dict[str, Any],
    ) -> bool:
        ...


class UserGetter(Protocol):
    def __call__(
        self,
        request: ASGIScope | WSGIEnvironment,
        payload: dict[str, Any],
    ) -> Optional[Any]:
        ...

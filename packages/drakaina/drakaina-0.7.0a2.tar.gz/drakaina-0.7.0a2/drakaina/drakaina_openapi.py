from __future__ import annotations

import sys
from collections.abc import Callable
from inspect import Parameter
from inspect import signature
from inspect import Signature
from typing import Any
from typing import cast
from typing import ForwardRef

# from pydantic.typing
if sys.version_info < (3, 9):

    def evaluate_forwardref(
        type_: ForwardRef, globalns: Any, localns: Any
    ) -> Any:
        return type_._evaluate(globalns, localns)

else:

    def evaluate_forwardref(
        type_: ForwardRef, globalns: Any, localns: Any
    ) -> Any:
        # Even though it is the right signature for python 3.9,
        #  mypy complains with `error: Too many arguments for
        #  "_evaluate" of "ForwardRef"` hence the cast...
        return cast(Any, type_)._evaluate(globalns, localns, set())


# from fastapi.dependencies.utils
def get_typed_annotation(param: Parameter, globalns: dict[str, Any]) -> Any:
    annotation = param.annotation
    if isinstance(annotation, str):
        annotation = ForwardRef(annotation)
        annotation = evaluate_forwardref(annotation, globalns, globalns)
    return annotation


# from fastapi.dependencies.utils
def get_typed_signature(call: Callable[..., Any]) -> Signature:
    signature_ = signature(call)
    globalns = getattr(call, "__globals__", {})
    typed_params = [
        Parameter(
            name=param.name,
            kind=param.kind,
            default=param.default,
            annotation=get_typed_annotation(param, globalns),
        )
        for param in signature_.parameters.values()
    ]
    typed_signature = Signature(typed_params)
    return typed_signature

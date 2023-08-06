"""
https://github.com/lidatong/dataclasses-json/
https://github.com/Fatal1ty/mashumaro

https://github.com/horejsek/python-fastjsonschema
https://github.com/s-knibbs/dataclasses-jsonschema
https://github.com/marshmallow-code/apispec
https://github.com/strongbugman/apiman

starlette.starlette.schemas.BaseSchemaGenerator
"""
from inspect import Parameter
from typing import Any
from typing import Dict
from typing import ForwardRef


def get_typed_annotation(param: Parameter, globalns: Dict[str, Any]) -> Any:
    annotation = param.annotation
    if isinstance(annotation, str):
        annotation = ForwardRef(annotation)
        # annotation = evaluate_forwardref(annotation, globalns, globalns)
    return annotation


# TODO: move to openapi middleware
# _signature = signature(procedure)
# global_ns = getattr(procedure, "__globals__", {})
# typed_params = [
#     Parameter(
#         name=param.name,
#         kind=param.kind,
#         default=param.default,
#         annotation=get_typed_annotation(param, global_ns),
#     )
#     for param in _signature.parameters.values()
# ]
# typed_signature = Signature(typed_params)

import asyncio
import json
from uuid import uuid4

from aiohttp import ClientSession

from validictory import validate, ValidationError, SchemaError
from .exc import (
    ParseError,
    InvalidRequest,
    InvalidParams,
    InternalError,
    InvalidResponse,
)


# Example with client side exceptions

REQ_JSONRPC20 = {
    "type": "object",
    "properties": {
        "jsonrpc": {"pattern": r"2\.0"},
        "method": {"type": "string"},
        "params": {"type": "any"},
        "id": {"type": "any"},
    },
}
RSP_JSONRPC20 = {
    "type": "object",
    "properties": {
        "jsonrpc": {"pattern": r"2\.0"},
        "result": {"type": "any"},
        "id": {"type": "any"},
    },
}
ERR_JSONRPC20 = {
    "type": "object",
    "properties": {
        "jsonrpc": {"pattern": r"2\.0"},
        "error": {
            "type": "object",
            "properties": {
                "code": {"type": "number"},
                "message": {"type": "string"},
            },
        },
        "id": {"type": "any"},
    },
}


class Response(object):

    __slots__ = ["id", "error", "result"]

    def __init__(self, id, result=None, error=None, **kw):
        self.id = id
        self.result = result
        self.error = error

    def __repr__(self):
        return "Response(id={rid}, result={res}, error={err}".format(
            rid=self.id, res=self.result, err=self.error
        )


class Client(object):
    def __init__(self, url, dumper=None, loop=None):
        self.url = url
        self.dumper = dumper
        if not loop:
            loop = asyncio.get_event_loop()
        if not self.dumper:
            self.dumper = json.dumps

        self.client = ClientSession(
            loop=loop, headers={"content-type": "application/json"}
        )

    def __del__(self):
        self.client.close()

    def __encode(self, method, params=None, id=None):
        try:
            data = self.dumper(
                {"jsonrpc": "2.0", "id": id, "method": method, "params": params}
            )
        except Exception as e:
            raise Exception("Can not encode: {}".format(e))

        return data

    async def call(self, method, params=None, id=None, schem=None):
        if not id:
            id = uuid4().hex
        try:
            resp = await self.client.post(
                self.url, data=self.__encode(method, params, id)
            )
        except Exception as err:
            raise Exception(err)

        if 200 != resp.status:
            raise InvalidResponse(
                "Error, server retunrned: {status}".format(status=resp.status)
            )

        try:
            data = await resp.json()
        except Exception as err:
            raise InvalidResponse(err)

        try:
            validate(data, ERR_JSONRPC20)
            return Response(**data)
        except ValidationError:
            # Passing data to validate response.
            # Good if does not valid to ERR_JSONRPC20 object.
            pass
        except Exception as err:
            raise InvalidResponse(err)

        try:
            validate(data, RSP_JSONRPC20)
            if id != data["id"]:
                raise InvalidResponse(
                    "Rsponse id {local} not equal {remote}".format(
                        local=id, remote=data["id"]
                    )
                )
        except Exception as err:
            raise InvalidResponse(err)

        if schem:
            try:
                validate(data["result"], schem)
            except ValidationError as err:
                raise InvalidResponse(err)
            except Exception as err:
                raise InternalError(err)

        return Response(**data)

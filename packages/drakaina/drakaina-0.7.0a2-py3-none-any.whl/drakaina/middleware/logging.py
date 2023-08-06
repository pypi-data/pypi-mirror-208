import logging

from drakaina.middleware.base import BaseMiddleware


class LoggingMiddleware(BaseMiddleware):
    logger: object

    async def logging_middleware(self, request, handler):
        raw_request = request.dump()

        self.logger.info(
            'RpcRequest id="%s" method="%s" params="%s"',
            raw_request.get("id", ""),
            raw_request["method"],
            raw_request.get("params", ""),
            extra={"request": raw_request},
        )

        response = await handler(request)

        raw_response = request.dump()

        self.logger.info(
            'RpcResponse id="%s" method="%s" params="%s" result="%s" error="%s"',
            raw_request.get("id", ""),
            raw_request["method"],
            raw_request.get("params", ""),
            raw_response.get("result", ""),
            raw_response.get("error", ""),
            extra={"request": raw_response, "response": raw_response},
        )

        return response

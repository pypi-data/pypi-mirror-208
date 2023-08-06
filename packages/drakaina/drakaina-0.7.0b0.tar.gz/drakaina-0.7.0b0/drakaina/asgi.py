class ASGIHandler:
    """"""

    def __init__(self, route: str):
        self.route = route

        # if prefix:
        #     assert prefix.startswith("/"), "A path prefix must start with '/'"
        #     assert not prefix.endswith(
        #         "/"
        #     ), "A path prefix must not end with '/',
        #     as the routes will start with '/'"

    """http scope:
    {
        'type': 'http.request',
        'scheme': 'http',
        'root_path': '',
        'server': ('127.0.0.1', 8000),
        'http_version': '1.1',
        'method': 'GET',
        'path': '/',
        'headers': [
            [b'host', b'127.0.0.1:8000'],
            [b'user-agent', b'curl/7.51.0'],
            [b'accept', b'*/*']
        ]
    }
    """

    async def __call__(self, scope: dict, receive, send):
        import sys

        if scope["type"] == "http":
            await send(
                {
                    "type": "http.response.start",
                    "status": 200,
                    "headers": [[b"content-type", b"text/plain"]],
                }
            )
            version = f"{sys.version_info.major}.{sys.version_info.minor}"
            message = (
                f"Hello world! From Uvicorn with Gunicorn. "
                f"Using Python {version}".encode("utf-8")
            )
            await send({"type": "http.response.body", "body": message})
        elif scope["type"] == "websocket":
            await send({"type": "websocket.send"})

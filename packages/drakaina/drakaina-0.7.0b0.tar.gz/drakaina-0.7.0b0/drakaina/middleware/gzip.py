
import gzip

from drakaina.middleware.base import BaseMiddleware


def gzip_str_to_file(raw_text, dest_file):
    with gzip.GzipFile(filename="", mode="w", fileobj=dest_file) as gz:
        gz.write(raw_text)


def gunzip_file(source_file):
    with gzip.GzipFile(filename="", mode="r", fileobj=source_file) as gz:
        return gz.read()


class GZIPMiddleware(BaseMiddleware):
    """
    todo
    todo: BREACH attack
    """

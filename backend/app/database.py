from collections.abc import Iterator
from contextlib import contextmanager

import psycopg

from app.config import Settings


@contextmanager
def database_connection(settings: Settings) -> Iterator[psycopg.Connection]:
    connection = psycopg.connect(settings.database_url, connect_timeout=3)
    try:
        yield connection
    finally:
        connection.close()


def check_database(settings: Settings) -> None:
    with database_connection(settings) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()

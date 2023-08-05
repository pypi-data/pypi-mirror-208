import os
import json
from contextlib import asynccontextmanager

from asyncpg.pool import Pool
from asyncpg import create_pool, connect, Connection

from .database_errors import DatabaseError


async def get(user: str = os.environ["PG_USER"], password: str = os.environ["PG_PASSWORD"],
              database: str = os.environ["PG_DATABASE"], host: str = os.environ["PG_HOST"],
              port: int = os.environ["PG_PORT"]) -> Connection:
    """Retrieve a database connection.
    :param user: Database user.
    :param password: Database password.
    :param database: Database name.
    :param host: Database host.
    :param port: Database port number.
    :return: (asyncpg) Connection.
    """

    connection: Connection = await connect(user=user, password=password, database=database, host=host, port=port)
    await __init(connection)
    return connection


async def get_pool(user: str = os.environ["PG_USER"], password: str = os.environ["PG_PASSWORD"],
                   database: str = os.environ["PG_DATABASE"], host: str = os.environ["PG_HOST"],
                   port: int = os.environ["PG_PORT"], min_size: int = int(os.environ["PG_POOL_MIN_SIZE"]),
                   max_size: int = int(os.environ["PG_POOL_MAX_SIZE"]),
                   max_inactive_connection_lifetime: int = int(
                       os.environ["PG_POOL_MAX_INACTIVE_CONNECTION_LIFETIME_SECONDS"])) -> Pool:
    """Retrieve a database connection pool.
    :param user: Database user.
    :param password: Database password.
    :param database: Database name.
    :param host: Database host.
    :param port: Database port number.
    :param min_size: Number of connection the pool will be initialized with.
    :param max_size: Max number of connections.
    :param max_inactive_connection_lifetime: Number of seconds after which inactive connections will be closed.
    :return: (asyncpg) Pool.
    """

    return await create_pool(user=user, password=password, database=database, host=host, port=port,
                             min_size=min_size, max_size=max_size,
                             max_inactive_connection_lifetime=max_inactive_connection_lifetime,
                             init=__init)


@asynccontextmanager
async def transactional(pool: Pool = None, connection: Connection = None):
    """Create a database transaction. If connection is provided then a transaction is created immediately, if not then
    a transaction established using a connection acquired from provided connection pool.
    :param pool: (asyncpg) Connection pool.
    :param connection: (asyncpg) Connection.
    :raise DatabaseError: If nor connection neither connection pool are specified.
    :return: Transactional connection.
    """

    if connection:
        async with connection.transaction():
            yield connection
    elif pool:
        async with pool.acquire() as connection, connection.transaction():
            yield connection
    else:
        raise DatabaseError("nor connection neither connection pool are specified")


async def __init(conn: Connection):
    await conn.set_type_codec("uuid", encoder=str, decoder=str, schema="pg_catalog")
    await conn.set_type_codec("numeric", encoder=str, decoder=float, schema="pg_catalog")
    await conn.set_type_codec("jsonb", encoder=json.dumps, decoder=json.loads, schema="pg_catalog")

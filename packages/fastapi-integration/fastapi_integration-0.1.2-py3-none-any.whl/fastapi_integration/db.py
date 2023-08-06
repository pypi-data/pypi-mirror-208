from collections.abc import AsyncGenerator
import logging
from contextlib import asynccontextmanager
import asyncio
import time

import redis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from fastapi_integration.config import FastApiConfig


class RedisEngine:
    """
    Represents the Redis engine for caching operations.

    Attributes:
        connection: The Redis connection.

    Args:
        setting: The FastApiConfig object for configuration.

    Methods:
        ping: Pings the Redis server to test the connection.
        connection: Retrieves the Redis connection.
    """
    def __init__(self, setting: FastApiConfig):
        """
        Initializes an instance of RedisEngine.

        Args:
            setting: The FastApiConfig object for configuration.
        """
        self.redis_pool = redis.ConnectionPool(
            host=setting.redis_url.host,
            port=setting.redis_url.port,
            db=int(setting.redis_url.path[1:]),
            username=setting.redis_url.user,
            password=setting.redis_url.password,
            max_connections=setting.redis_max_connections,
        )

    def ping(self, recursive=20):
        """
        Pings the Redis server to test the connection.
        """
        is_connected = False
        while not is_connected:
            try:
                logging.info("Connecting to Redis")
                redis_conn = redis.Redis(connection_pool=self.redis_pool)
                redis_conn.set('test', 'test', ex=1)
                is_connected = True
            except Exception as error:
                if recursive > 0:
                    logging.error(
                        f"Cannot connect to Redis: {error}, Retrying in 3s"
                    )
                    time.sleep(3)
                    return self.ping()
                else:
                    raise error
        logging.info("Connection established")

    def connection(self) -> redis.Redis:
        """
        Retrieves the Redis connection.

        Returns:
            The Redis connection.
        """
        return redis.Redis(connection_pool=self.redis_pool)


class SqlEngine:
    def __init__(self, setting: FastApiConfig, **kwargs):
        """
        Initializes an instance of SqlEngine.

        Args:
            setting: The FastApiConfig object for configuration.
            **kwargs: Additional keyword arguments.
        """
        self.setting = setting
        self.engine = create_async_engine(
            setting.get_sql_database,
            future=True,
            echo=False,
            **kwargs
        )
        self.async_session_factory = sessionmaker(
            self.engine, autoflush=False, expire_on_commit=False,
            class_=AsyncSession
        )

    async def create_database(self, base, recursive=20):
        """
        Creates the database specified in the configuration.

        Args:
            base: The SQLAlchemy declarative_base object.

        """
        is_connected = False
        while not is_connected:
            try:
                logging.info("Connecting to  PostgreSQL")
                async with self.engine.begin() as conn:
                    await conn.run_sync(base.metadata.create_all)

                async with AsyncSession(self.engine) as session:
                    async with session.begin():
                        logging.info("Connection established")
                is_connected = True
            except Exception as error:
                if recursive > 0:
                    logging.error(
                        f"Cannot connect to PGSql: {error}, Retrying in 3s"
                    )
                    await asyncio.sleep(3)
                    return await self.create_database(base, recursive-1)
                else:
                    raise error

    async def drop_database(self, base):
        """
        Drops the database specified in the configuration.

        Args:
            base: The SQLAlchemy declarative_base object.
        """
        logging.info("Dropping Database")
        async with self.engine.begin() as conn:
            await conn.run_sync(base.metadata.drop_all)
            logging.info("Database Dropped")

    async def connection(self) -> AsyncGenerator:
        """
        Retrieves an asynchronous generator for database connections.

        Returns:
            An asynchronous generator for database connections.
        """
        async with self.async_session_factory() as session:
            logging.info("ASYNC Pool: %s", self.engine.pool.status())
            yield session

    @asynccontextmanager
    async def connection_context_manager(self) -> AsyncSession:
        """
        Retrieves an asynchronous session context manager.

        Returns:
            An asynchronous session context manager.
        """
        async with self.async_session_factory() as session:
            logging.info("ASYNC Pool: %s", self.engine.pool.status())
            yield session

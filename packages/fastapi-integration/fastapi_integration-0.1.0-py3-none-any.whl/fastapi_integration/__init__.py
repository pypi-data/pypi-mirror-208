from typing import Callable, List, Tuple, Union
from functools import cached_property
from passlib.context import CryptContext


from fastapi import FastAPI, HTTPException, routing
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


from fastapi_integration.config import FastApiConfig
from fastapi_integration.db import SqlEngine, RedisEngine
from fastapi_integration.auth import BaseRouter
from fastapi_integration.exceptions import (
    NoConfigurationFound,
    DependencyException
)
from fastapi_integration.dependencies import SQL, Redis
from fastapi_integration.features import AdminPanel


class FastAPIExtended(FastAPI):
    """
    This class extends the functionality of FastAPI.

    Attributes:
        routers: A list of tuples containing API routers and their prefixes.

    Properties:
        config: Retrieves the FastApiConfig object.
    """
    routers: List[Tuple[routing.APIRouter, str]] = []

    @property
    def config(self) -> FastApiConfig:
        """
        Retrieves the FastApiConfig object.
        """
        return self.get_setting()

    def __init__(
            self,
            *args,
            base,
            db_engine: SqlEngine = None,
            redis_engine: RedisEngine = None,
            routers: list = None,
            features: List[
                Union[BaseRouter, AdminPanel]
            ] = None,
            **kwargs
    ):
        """
        Initializes an instance of FastAPIExtended.

        Args:
            base: The base path of the API.
            db_engine: The SQL engine for database operations.
            redis_engine: The Redis engine for caching operations.
            routers: A list of additional API routers.
            features: A list of features to be added to the FastAPI app.
        """
        self.pwd_context = CryptContext(
            schemes=["bcrypt"], deprecated="auto"
        )
        self.base = base
        self.features = features or []
        self.routers = routers or []
        super().__init__(
            *args,
            **{**kwargs, **self.config.fastapi_kwargs}
        )
        if self.config.database_url and db_engine:
            self.db_engine = db_engine
        if self.config.redis_url and redis_engine:
            self.redis_engine = redis_engine
            self.redis_engine.ping()
        self.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.allowed_hosts,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self.add_event_handler(
            "startup", self.create_start_app_handler()
        )

        self.add_event_handler(
            "shutdown", self.create_stop_app_handler()
        )
        self.add_exception_handler(
            HTTPException, self.http_error_handler
        )

    @cached_property
    def get_setting(self) -> FastApiConfig:
        result = next(
            (
                obj for obj in self.features
                if FastApiConfig.__class__ in obj.__class__.__mro__
            ),
            None
        )
        if result is None:
            raise NoConfigurationFound
        return result.create()

    async def features_handler(self) -> None:
        for feature in self.features:
            if (
                hasattr(feature, "create")
            ) and (
                feature.create.__annotations__.get('return')
            ):
                router_type = feature.create.__annotations__['return']
                if router_type == routing.APIRouter:
                    self.include_router(
                        feature.create(
                            db_engine=self.db_engine,
                            config=self.config,
                            pwd_context=self.pwd_context
                        ),
                        prefix=feature.prefix
                    )

            if (
                feature.__class__ == AdminPanel
            ) or (
                hasattr(feature, "__mro__") and AdminPanel in feature.__mro__
            ):
                feature.create(
                    app=self,
                    engine=self.db_engine.engine
                )

    def create_start_app_handler(self) -> Callable:
        """
        Creates a startup event handler for the FastAPI application.

        Returns:
            The startup event handler as a callable.
        """
        async def start_app() -> None:
            self.dependency_lookup()
            for router in self.routers:
                self.include_router(router)
            await self.features_handler()
            if self.config.database_url:
                await self.create_sql_database()
        return start_app

    async def create_sql_database(self) -> None:
        """
        Creates the SQL database specified in the configuration.
        """
        await self.db_engine.create_database(self.base)

    def create_stop_app_handler(self) -> Callable:
        """
        Creates a shutdown event handler for the FastAPI application.

        Returns:
            The shutdown event handler as a callable.
        """
        async def stop_app() -> None:
            if self.config.database_url:
                async with self.db_engine.engine.connect() as conn:
                    await conn.close()
                    await self.db_engine.engine.dispose()
        return stop_app

    @staticmethod
    async def http_error_handler(
        _: Request,
        exc: HTTPException
    ) -> JSONResponse:
        """
        Handles the HTTP errors.

        Args:
            _: The request object.
            exc: The exception representing the HTTP error.

        Returns:
            The JSON response for the error.
        """
        return JSONResponse(
            {"errors": [exc.detail]}, status_code=exc.status_code
        )

    def dependency_lookup(self) -> None:
        """
        Performs dependency lookup for the FastAPI application.
        """
        for feature in self.features:
            if not self.config.database_url and SQL in feature.__mro__:
                raise DependencyException("No Database URL specified")
            if not self.config.redis_url and Redis in feature.__mro__:
                raise DependencyException("No Redis URL specified")

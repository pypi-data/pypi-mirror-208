import logging
from typing import List, Tuple, Optional

from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseSettings
from pydantic.networks import PostgresDsn, RedisDsn
from dotenv import load_dotenv


class FastApiConfig(BaseSettings):
    """
    Configuration settings for the FastAPI application.

    Attributes:
        debug: Whether the application is in debug mode.
        docs_url: The URL for the API documentation.
        openapi_prefix: The prefix for OpenAPI endpoints.
        openapi_url: The URL for the OpenAPI JSON file.
        redoc_url: The URL for the ReDoc documentation.
        title: The title of the API.
        version: The version of the API.
        algorithm: The algorithm used for JWT token encoding.
        access_token_expire_minutes: The expiration minutes for access tokens.
        oauth2_scheme: The OAuth2 password bearer scheme.
        default_pagination: The default pagination size.
        max_pagination: The maximum pagination size.
        database_url: The URL for the Postgres database.
        redis_url: The URL for the Redis database.
        redis_max_connections: The maximum number of connections to the Redis.
        secret_key: The secret key for the application.
        api_prefix: The prefix for API endpoints.
        jwt_token_prefix: The prefix for JWT tokens.
        allowed_hosts: The list of allowed hosts.
        logging_level: The logging level for the application.
        loggers: The loggers to configure.
    """
    def __init__(self, *args, **kwargs):
        load_dotenv()
        super().__init__(*args, **kwargs)

    debug: bool
    docs_url: str = "/docs"
    openapi_prefix: str = ""
    openapi_url: str = "/openapi.json"
    redoc_url: str = "/redoc"
    title: str
    version: str = "0.0.0"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 180
    oauth2_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(
        tokenUrl="api/auth/token"
    )
    default_pagination: int = 20
    max_pagination: int = 100

    database_url: Optional[PostgresDsn]
    redis_url: Optional[RedisDsn]
    redis_max_connections: int = 100

    secret_key: str
    api_prefix: str = "/api"
    jwt_token_prefix: str = "Token"
    allowed_hosts: List[str] = ["*"]
    logging_level: int = logging.INFO
    loggers: Tuple[str, str] = ("uvicorn.asgi", "uvicorn.access")

    class Config:
        validate_assignment = True

    @property
    def fastapi_kwargs(self) -> dict:
        """
        Retrieves the keyword arguments for initializing FastAPI.

        Returns:
            A dictionary of FastAPI keyword arguments.
        """
        return {
            "debug": self.debug,
            "docs_url": self.docs_url,
            "openapi_prefix": self.openapi_prefix,
            "openapi_url": self.openapi_url,
            "redoc_url": self.redoc_url,
            "title": self.title,
            "version": self.version,
        }

    @property
    def get_sql_database(self) -> str:
        """
        Retrieves the SQL database URL.

        Returns:
            The URL for the Postgres database.
        """
        return self.database_url

    @classmethod
    def create(cls) -> "FastApiConfig":
        """
        Creates an instance of FastApiConfig, as a feature.

        Returns:
            An instance of FastApiConfig.
        """
        return cls

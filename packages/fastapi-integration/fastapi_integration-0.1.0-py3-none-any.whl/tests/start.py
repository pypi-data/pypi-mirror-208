import resolve_path
import uvicorn
import logging

from pydantic import PostgresDsn, RedisDsn

from fastapi_integration import FastAPIExtended, FastApiConfig
from fastapi_integration.models import AbstractBaseUser


class MyConfig(FastApiConfig):
    debug = True
    database_url: PostgresDsn = "postgresql+asyncpg://postgres:12345@127.0.0.1:5432/test"   # Postgres Database URL
    secret_key = "2129df71b280f0768a80efcb7bf5"        # A Random Secret Key
    redis_url: RedisDsn = "redis://127.0.0.1:6382/0"   # Redis Database URL
    title = "Test"                                     # Website Title


class User(AbstractBaseUser):
    """Add Your Desired Fields Here."""


class MyApp(FastAPIExtended):
    settings = MyConfig


app = MyApp(Users=User)


if __name__ == "__main__":
    resolve_path
    logging.basicConfig(level=logging.INFO)
    uvicorn.run(
        "start:app", host="localhost", port=8000, reload=True, workers=1
    )

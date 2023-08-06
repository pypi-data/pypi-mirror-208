import logging

import uvicorn
from fastapi import APIRouter
from sqlalchemy.orm import declarative_base

from fastapi_integration.features import (
    JwtAuthentication,
    UserRegistration,
    AdminPanel
)
from fastapi_integration.models import AbstractBaseUser
from fastapi_integration import FastAPIExtended, FastApiConfig
from fastapi_integration.db import SqlEngine

from examples import admin as test_admin


base = declarative_base()


class MyConfig(FastApiConfig):
    debug: bool = True
    secret_key: str = "..."
    title: str = "..."


engine = SqlEngine(MyConfig())


class Users(AbstractBaseUser, base):
    __tablename__ = "users"


test_router = APIRouter()


@test_router.get("/")
def hello_world():
    return {"message": "Hello, world!"}


app = FastAPIExtended(
    base=base,
    db_engine=engine,
    features=[
        MyConfig,
        JwtAuthentication("/auth", Users, tags=["user"]),
        UserRegistration("/users", Users, tags=["user"]),
        AdminPanel(
            test_admin
        )
    ],
    routers=[
        test_router
    ]
)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    uvicorn.run(
        "main:app", host="0.0.0.0", port=7979, reload=True, workers=1
    )

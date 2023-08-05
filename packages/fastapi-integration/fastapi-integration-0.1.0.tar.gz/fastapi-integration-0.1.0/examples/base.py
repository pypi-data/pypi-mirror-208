from sqlalchemy.orm import declarative_base

from fastapi_integration.models import AbstractBaseUser
from fastapi_integration import FastApiConfig

base = declarative_base()


class MyConfig(FastApiConfig):
    debug = True
    secret_key = "2129df71b280f0768a80efcb7bf5"
    title = "Test"


class Users(AbstractBaseUser, base):
    __tablename__ = "users"

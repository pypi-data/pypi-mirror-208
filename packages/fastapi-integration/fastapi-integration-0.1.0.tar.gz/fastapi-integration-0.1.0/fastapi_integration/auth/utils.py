from datetime import datetime, timedelta
from typing import Any, Callable


from fastapi import Depends
from pydantic import BaseModel
import jwt
from sqlalchemy.ext.asyncio import AsyncSession


from fastapi_integration.db import SqlEngine
from fastapi_integration.config import FastApiConfig
from fastapi_integration.models import AbstractBaseUser
from fastapi_integration.exceptions import (
    is_not_superuser_exception,
    credentials_exception
)


class TokenData(BaseModel):
    user_id: int


def manager_get_current_user(
        db_engine: SqlEngine,
        config: FastApiConfig,
        user_model: AbstractBaseUser
) -> Callable:
    """
    Manager function to get the current user.

    Args:
        db_engine: The SQL engine for database connections.
        config: The FastAPI configuration.
        user_model: The user model associated with the current user.

    Returns:
        Callable: The get_current_user function.
    """
    async def get_current_user(
        db_session: AsyncSession = Depends(db_engine.connection),
        token: str = Depends(config.oauth2_scheme),
    ) -> AbstractBaseUser:
        try:
            payload = jwt.decode(
                token, config.secret_key, algorithms=[config.algorithm]
            )
            user_id = payload.get("sub")

            if user_id is None:
                raise credentials_exception

            token_data = TokenData(user_id=user_id)
        except jwt.exceptions.PyJWTError:
            raise credentials_exception

        user = await user_model.objects.get(
            db_session=db_session, id=token_data.user_id
        )
        if user is None:
            raise credentials_exception
        return user

    return get_current_user


def manager_get_admin_user(
    db_engine: SqlEngine, config: FastApiConfig, user_model: AbstractBaseUser
) -> Callable:
    """
    Manager function to get the admin user.

    Args:
        db_engine: The SQL engine for database connections.
        config: The FastAPI configuration.
        user_model: The user model associated with the admin user.

    Returns:
        Callable: The get_admin_user function.
    """
    async def get_admin_user(
        db_session: AsyncSession = Depends(db_engine.connection),
        token: str = Depends(config.oauth2_scheme),
    ) -> Any:
        user = await manager_get_current_user(
            db_engine, config, user_model
        )(db_session, token)
        if not user.is_admin:
            raise is_not_superuser_exception
        return user
    return get_admin_user


def manager_create_access_token(
        config: FastApiConfig
) -> Callable:
    """
    Manager function to create an access token.

    Args:
        config: The FastAPI configuration.

    Returns:
        Callable: The create_access_token function.
    """
    def create_access_token(*, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(
            minutes=config.access_token_expire_minutes
        )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, config.secret_key, algorithm=config.algorithm
        )
        return encoded_jwt
    return create_access_token

from passlib.context import CryptContext


from fastapi import (
    Depends,
    HTTPException,
    APIRouter,
    status
)
from fastapi.security import OAuth2PasswordRequestForm
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from fastapi_integration.auth.utils import (
    manager_create_access_token,
    manager_get_current_user,
)
from fastapi_integration.auth.schemas import AuthModel, UserOut, UserIn
from fastapi_integration.db import SqlEngine
from fastapi_integration.config import FastApiConfig
from fastapi_integration.models import AbstractBaseUser


def create_auth_router(
        db_engine: SqlEngine,
        config: FastApiConfig,
        user_model: AbstractBaseUser,
        pwd_context: CryptContext,
        **kwargs
) -> APIRouter:
    """
    Create an API router for authentication.

    Args:
        db_engine: The SQL engine for database connections.
        config: The FastAPI configuration.
        user_model: The user model associated with authentication.
        pwd_context: The password hashing context.
        **kwargs: Additional keyword arguments.

    Returns:
        APIRouter: The created authentication API router.
    """
    auth_router = APIRouter(**kwargs)

    @auth_router.post("/token", response_model=AuthModel)
    async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db_session: AsyncSession = Depends(db_engine.connection),
    ):
        user = await user_model.objects.get(
            db_session=db_session, email=form_data.username
        )
        if not (
            user and pwd_context.verify(form_data.password, user.password)
        ):
            raise HTTPException(
                status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Incorrect email or password",
            )

        create_access_token = manager_create_access_token(
            config=config
        )
        access_token = create_access_token(data={"sub": user.id})
        return {"access_token": access_token, "token_type": "bearer"}

    return auth_router


def create_user_register_router(
        db_engine: SqlEngine,
        config: FastApiConfig,
        user_model: AbstractBaseUser,
        pwd_context: CryptContext,
        **kwargs
) -> APIRouter:
    """
    Create an API router for user registration.

    Args:
        db_engine: The SQL engine for database connections.
        config: The FastAPI configuration.
        user_model: The user model associated with user registration.
        pwd_context: The password hashing context.
        **kwargs: Additional keyword arguments.

    Returns:
        APIRouter: The created user registration API router.
    """
    register_router = APIRouter(**kwargs)

    get_current_user = manager_get_current_user(
        db_engine, config, user_model
    )

    @register_router.post("/register", response_model=UserOut)
    async def register(
        form_data: UserIn,
        db_session: AsyncSession = Depends(db_engine.connection),
    ):
        """
        Ask for forgiveness than for permission
        Don't be too specific in registration unique constraint to run from BF
        """
        try:
            data = form_data.dict().copy()
            data.update(
                password=pwd_context.encrypt(form_data.dict().get("password"))
            )
            return await user_model.objects.create(
                db_session=db_session,
                **data
            )
        except IntegrityError as error:
            if 'unique constraint' in str(error):
                raise HTTPException(
                    status_code=status.HTTP_417_EXPECTATION_FAILED,
                    detail="Username or Email already exists."
                )

    @register_router.get("/me", response_model=UserOut)
    async def read_users_me(
        current_user: user_model = Depends(get_current_user)
    ):
        return current_user

    return register_router

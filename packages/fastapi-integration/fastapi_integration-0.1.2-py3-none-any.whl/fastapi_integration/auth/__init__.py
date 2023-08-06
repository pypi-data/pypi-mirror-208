from fastapi import APIRouter

from fastapi_integration.dependencies import SQLAlchemy
from fastapi_integration.auth.routers import (
    create_auth_router,
    create_user_register_router
)


class BaseRouter:
    def __init__(self, prefix: str, model=None, **kwargs):
        """
        Base router class for creating API routers.

        Args:
            prefix (str): The prefix for the router's path.
            model: The model associated with the router (optional).
            **kwargs: Additional keyword arguments.
        """
        self.model = model
        self.prefix = prefix
        self.kwargs = kwargs

    def create(self) -> None:
        """
        Create the API router.

        Returns:
            None
        """
        return None


class JwtAuthentication(SQLAlchemy, BaseRouter):
    def create(self, **kwargs) -> APIRouter:
        """
        Create the JWT authentication router.

        Args:
            **kwargs: Additional keyword arguments.

        Returns:
            APIRouter: The created API router.
        """
        return create_auth_router(
            user_model=self.model,
            **kwargs,
            **self.kwargs
        )


class UserRegistration(SQLAlchemy, BaseRouter):
    def create(self, **kwargs) -> APIRouter:
        """
        Create the user registration router.

        Args:
            **kwargs: Additional keyword arguments.

        Returns:
            APIRouter: The created API router.
        """
        return create_user_register_router(
            user_model=self.model,
            **kwargs,
            **self.kwargs
        )

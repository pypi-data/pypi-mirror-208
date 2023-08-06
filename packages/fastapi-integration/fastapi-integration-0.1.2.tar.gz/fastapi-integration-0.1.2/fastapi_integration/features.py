from fastapi_integration.auth import JwtAuthentication, UserRegistration
from fastapi_integration.config import FastApiConfig
from fastapi_integration.models import AbstractBaseUser, AbstractOAuth2User
from fastapi_integration.admin import AdminPanel


def get_all_features() -> list:
    """
    Retrieves a list of all features.

    Returns:
        A list of all features available in the application.
    """
    return [
        JwtAuthentication,
        UserRegistration,
        FastApiConfig,
        AbstractBaseUser,
        AbstractOAuth2User,
        AdminPanel
    ]

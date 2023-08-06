from fastapi import HTTPException, status


class IntegrationBaseException(Exception):
    "Base Exception for fastapi-integration"


class HTTPErrorIntegration(IntegrationBaseException, HTTPException):
    "HTTP Errors for integration based level"


class ValidationException(IntegrationBaseException):
    "Validation errors for application level"


class NoConfigurationFound(IntegrationBaseException):
    "No configuration found, Please configure your FastAPI App"


class DependencyException(IntegrationBaseException):
    "Lack of dependencies required for added features"


credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


is_not_superuser_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate administration access",
        headers={"WWW-Authenticate": "Bearer"},
    )

from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Boolean

from fastapi_integration.orm.models import AbstractModel
from fastapi_integration.dependencies import SQLAlchemy


class AbstractBaseUser(SQLAlchemy, AbstractModel):
    """
    Represents the abstract base user model.

    This class uses the SQLAlchemy dependency and the AbstractModel class.

    Attributes:
        id: The primary key of the user.
        email: The email of the user.
        username: The username of the user.
        password: The password of the user.
        created_at: The timestamp of when the user was created.
        updated_at: The timestamp of when the user was last updated.
        is_active: Indicates whether the user is active.
        is_admin: Indicates whether the user is an administrator.
        last_login: The timestamp of the user's last login.
    """
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(50), unique=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=True)
    password = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True, default=None)


class AbstractOAuth2User(SQLAlchemy, AbstractModel):
    """
    Represents the abstract OAuth2 user model.

    This class extends the SQLAlchemy dependency and the AbstractModel class.

    Attributes:
        id: The primary key of the OAuth2 user.
        oauth_name: The name of the OAuth provider.
        access_token: The access token for the OAuth user.
        expires_at: The timestamp of when the access token expires.
        refresh_token: The refresh token for the OAuth user.
        account_id: The account ID associated with the OAuth user.
        account_email: The email associated with the OAuth user.
    """
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    oauth_name = Column(String(100), unique=True, index=True)
    access_token = Column(String(200), unique=True, index=True)
    expires_at = Column(DateTime, nullable=True, default=None)
    refresh_token = Column(String(200), unique=True, index=True)
    account_id = Column(String(30), unique=True, index=True)
    account_email = Column(String(200), unique=True, index=True)

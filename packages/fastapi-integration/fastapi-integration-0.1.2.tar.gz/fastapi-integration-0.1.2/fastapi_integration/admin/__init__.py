from fastapi import FastAPI
from fastapi_integration.db import SqlEngine
from sqladmin import Admin

from fastapi_integration.dependencies import SQLAlchemy
from fastapi_integration.admin.generator import AdminLoader


class AdminPanel(SQLAlchemy, AdminLoader):
    """
    Represents an admin panel integrated with FastAPI.

    This class inherits from SQLAlchemy and AdminLoader, providing
    functionality to manage and display an admin panel for managing
    database models.

    Args:
        SQLAlchemy: SQLAlchemy dependency checker.
        AdminLoader: Providing admin panel generation and configuration.

    """
    def create(self, app: FastAPI, engine: SqlEngine) -> None:
        """
        Create and configure the admin panel for a FastAPI application.

        Args:
            app: The FastAPI application instance.
            engine: The SqlEngine instanceto use for database connections.
        """
        admin = Admin(app, engine, **self.kwargs)
        for obj in self._admin_views:
            admin.add_view(obj)

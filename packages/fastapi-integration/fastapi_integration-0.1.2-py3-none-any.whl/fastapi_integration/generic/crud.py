from typing import Union, Optional, Tuple, List
from urllib.parse import urlencode

from pydantic import BaseModel, HttpUrl, Field
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession


from fastapi_integration.dependencies import SQLAlchemy
from fastapi_integration.config import FastApiConfig
from fastapi_integration.orm.models import AbstractModel
from fastapi_integration.exceptions import ValidationException


class PaginationQuery(BaseModel):
    """
    Represents the pagination query parameters.

    Attributes:
        page (int): The current page number.
        per_page (int): The number of results per page.

    Note:
        `page` must be greater than or equal to 1.
        `per_page` must be between 1 and 100 (inclusive).
    """
    page: int = Field(1, ge=1)
    per_page: int = Field(20, le=100)


def get_pagination_class(config: FastApiConfig) -> PaginationQuery:
    """
    Get the PaginationQuery class with default per_page values from the
    provided configuration.

    Args:
        config: The FastAPI configuration.

    Returns:
        PaginationQuery: The updated PaginationQuery class.
    """
    PaginationQuery.per_page: int = Field(
            config.default_pagination, le=config.max_pagination
    )
    return PaginationQuery


class PaginatedObjects(BaseModel):
    """
    Represents a paginated response.

    Attributes:
        results (List[dict]): The list of results.
        page (Union[None, int]): The current page number.
        count (Union[None, int]): The total count of results.
        next_page (Union[None, HttpUrl]): The URL of the next page.
        previous_page (Union[None, HttpUrl]): The URL of the previous page.
    """
    results: List[dict]
    page: Union[None, int]
    count: Union[None, int]
    next_page: Union[None, HttpUrl]
    previous_page: Union[None, HttpUrl]


class BaseCRUD(SQLAlchemy):
    """
    Base CRUD class for handling database operations.

    Attributes:
        verbose_name: The verbose name of the model.
        order_by_fields: The fields used forordering the results.
    """
    verbose_name: str
    order_by_fields: Union[None, Tuple, str]

    def __init__(
            self, model: AbstractModel,
            in_schema: BaseModel,
            update_schema: BaseModel,
            name: str
    ):
        self.model = model
        self.in_schema = in_schema
        self.update_schema = update_schema
        self.verbose_name = name

    @property
    def _order_by_fields(self):
        cached_order_by_fields = getattr(self, "order_by_fields", None)
        if cached_order_by_fields in ["__all__", ("__all__")]:
            return self.model.__table__.columns.keys()
        return cached_order_by_fields

    @_order_by_fields.setter
    def _order_by_fields(self, value):
        if (
            isinstance(value, (str, tuple))
        ) and self.init_order_by(value):
            self._order_by_fields = value
        raise ValidationException(
            "order_by_fields is not a valid string/tuple"
        )

    def init_order_by(self, order_by):
        fields = [field.strip("-") for field in order_by.split(",")]
        invalid_fields = set(fields) - set(self.model.__table__.columns.keys())
        if invalid_fields:
            raise ValidationException(
                f"order_by contains invalid fields:{', '.join(invalid_fields)}"
            )
        return True

    def is_order_by_valid(self, order_by):
        fields = [field.strip("-") for field in order_by.split(",")]
        return all(field in self._order_by_fields for field in fields)


class ConstructorMixin:
    """
    Mixin class for CRUD constructors.

    Methods:
        pre_save_check: Perform pre-save checks.
        pre_update_check: Perform pre-update checks.
        pre_delete_check: Perform pre-delete checks.
    """
    async def pre_save_check(self, db_session: AsyncSession, data: dict):
        pass

    async def pre_update_check(self, db_session: AsyncSession, data: dict):
        pass

    async def pre_delete_check(self, db_session: AsyncSession):
        pass


class CRUD(BaseCRUD, ConstructorMixin):
    """
    CRUD class for performing Create, Read, Update, and Delete operations.

    Methods:
        create: Create a new instance.
        delete: Delete instances.
        read_all: Read all instances.
        paginated_read_all: Read instances with pagination.
        read_single: Read a single instance.
        update: Update an instance.
    """
    async def create(self, db_session: AsyncSession, data: dict):
        await self.pre_save_check(db_session, data)
        instance = await self.model.objects.create(
            db_session=db_session, **data
        )
        return instance

    async def delete(
            self, db_session: AsyncSession, joins: set = None, **kwargs):
        await self.pre_delete_check(db_session)
        deleted_rows = await self.model.objects.delete(
            db_session=db_session, joins=joins, **kwargs
        )
        return deleted_rows

    async def read_all(
            self,  db_session: AsyncSession,
            joins: set or None,
            order_by: Optional[str] = None,
            skip: int = None,
            per_page: int = None,
            get_count: bool = False,
            **kwargs
    ):
        if order_by and order_by != "?":
            if not self.is_order_by_valid(order_by):
                text = f"{self.verbose_name} with the specified field for"
                text += "order_by is not found, please use one of"
                text += f"these fields : {self._order_by_fields}"
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=text
                )
            order_by = tuple(order_by.split(","))
        query = self.model.objects.filter(
            joins=joins,
            order_by=order_by,
            skip=skip,
            limit=per_page,
            **kwargs
        )
        count = await query.count(db_session) if get_count else None
        result = await query.execute(db_session=db_session)

        if get_count:
            return result, count
        return query

    async def paginated_read_all(
            self,
            db_session: AsyncSession,
            joins: set = None,
            order_by: Optional[str] = None,
            base_url=None,
            query_params: dict = None,
            **kwargs
    ):
        query_params = query_params or {}
        per_page = query_params.get('per_page')
        page_num = query_params.get('page')

        if order_by:
            query_params.update(order_by=order_by)

        results, count = await self.read_all(
            db_session, order_by=order_by, skip=(page_num - 1) * per_page,
            per_page=per_page, joins=joins or set(), get_count=True, **kwargs
        )
        next_page = None
        previous_page = None

        if (page_num * per_page) < count:
            next_query_params = urlencode(
                {**query_params, "page": page_num + 1}
            )
            next_page = f"{base_url}?{next_query_params}"

        if (page_num - 1) > 0 and 0 < (
            (page_num-1) * per_page
        ) < count+per_page:
            prev_query_params = urlencode(
                {**query_params, "page": page_num - 1}
            )
            previous_page = f"{base_url}?{prev_query_params}"

        return dict(
            results=results, page=page_num, count=count,
            previous_page=previous_page, next_page=next_page
        )

    async def read_single(
        self,
        db_session: AsyncSession,
        joins: set = None,
        **kwargs
    ):
        result = await self.model.objects.get(
            db_session=db_session, joins=joins or set(), **kwargs
        )
        if not result:
            text = f"{self.verbose_name} with specified filter is not found"
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=text
            )
        return result

    async def update(
            self, db_session: AsyncSession, data: dict, joins: set, **kwargs
    ):
        await self.pre_update_check(db_session, data)
        updated_instance = await self.model.objects.update(
            db_session=db_session, data=data, joins=joins or set(), **kwargs
        )
        if updated_instance is None:
            text = f"{self.verbose_name} with specified filter is not found"
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=text
            )
        return updated_instance

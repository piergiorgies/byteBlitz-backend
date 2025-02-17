from pydantic import Field
from typing import Optional
from app.schemas.base import BaseRequest
from fastapi import Query

class PaginationParams(BaseRequest):
    """
    Pagination Params DTO

    Attributes
        page (int): The page number
        size (int): The page size

    """
    limit: int = Field(10, description="The maximum number of record to return")
    offset: int = Field(0, description="The number of record to skip")
    search_filter: Optional[str] = Field(None, description="Search filter string")


def get_pagination_params(
    limit: int = Query(15, ge=1),
    offset: int = Query(0, ge=0),
    search: str = Query(None),
) -> PaginationParams:
    return PaginationParams(limit=limit, offset=offset, search_filter=search)


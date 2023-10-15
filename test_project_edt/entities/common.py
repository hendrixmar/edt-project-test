from enum import Enum
from typing import Annotated

from fastapi import Query, HTTPException
from pydantic import BaseModel, BeforeValidator

from test_project_edt.db.models.restaurant import Restaurant


def validate_order_by_argument(orderby_argument: str):
    if orderby_argument not in Restaurant.__annotations__:
        raise HTTPException(
            status_code=422,
            detail=f"the argument {orderby_argument} is not valid"
        )

    return orderby_argument


class AscOrDesc(Enum):
    DESC: str = "DESC"
    ASC: str = "ASC"

class PaginationParams(BaseModel):
    limit: int = Query(default=100, ge=1, le=1000)
    offset: int = Query(default=0, ge=0)
    order_by: Annotated[
        str,
        BeforeValidator(validate_order_by_argument)
    ] = Query(default="id")
    asc_or_desc: AscOrDesc = Query(default=AscOrDesc.DESC)

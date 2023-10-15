from fastapi import Depends
from psycopg_pool import AsyncConnectionPool
from starlette.requests import Request

from test_project_edt.repository.pyscopg_restaurant_repository import \
    PsycopgRestaurantRepository
from test_project_edt.repository.resturant_repository_protocol import \
    RestaurantRepository
from test_project_edt.web.lifetime import retrieve_db_pool


async def get_db_pool(request: Request) -> AsyncConnectionPool:
    """
    Return database connections pool.

    :param request: current request.
    :returns: database connections pool.
    """
    return request.app.state.db_pool


def inject_repository(connection_pool: AsyncConnectionPool = Depends(
    retrieve_db_pool)) -> RestaurantRepository:
    return PsycopgRestaurantRepository(connection_pool)

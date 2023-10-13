import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from psycopg_pool import AsyncConnectionPool
from starlette import status


@pytest.mark.anyio
async def test_health(client: AsyncClient, fastapi_app: FastAPI) -> None:
    """
    Checks the health endpoint.

    :param client: client for the app.
    :param fastapi_app: current FastAPI application.
    """
    url = fastapi_app.url_path_for("health_check")
    response = await client.get(url)
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.anyio
async def test_healths(client: AsyncClient,
                       fastapi_app: FastAPI,
                       dbpool: AsyncConnectionPool) -> None:
    """
    Checks the health endpoint.

    :param client: client for the app.
    :param fastapi_app: current FastAPI application.
    """
    async with dbpool.connection() as conn_check:
        res = await conn_check.execute(
            """SELECT *
                FROM restaurants
                """

        )
        row = await res.fetchall()
        print(row, "here")

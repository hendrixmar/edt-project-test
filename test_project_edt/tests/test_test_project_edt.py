from typing import Dict

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
@pytest.mark.parametrize(
    "order_by",
    [
        "id",
        "rating",
        "name",
        "site",
        "email",
        "phone",
        "street",
        "city",
        "state",
        "lat",
        "lng",
    ],
)
@pytest.mark.parametrize("asc_or_desc", ["ASC", "DESC"])
async def test_restaurant_retrievals(
    client: AsyncClient, fastapi_app: FastAPI, order_by: str, asc_or_desc: str
) -> None:
    """
    Checks the health endpoint.

    :param client: client for the app.
    :param fastapi_app: current FastAPI application.
    """
    url = fastapi_app.url_path_for("get_all_restaurants")
    response = await client.get(
        url,
        params={
            "limit": 100,
            "offset": 0,
            "order_by": order_by,
            "asc_or_desc": asc_or_desc,
        },
    )
    elements = response.json()
    comparison = [*elements]
    assert len(response.json()) == 100
    assert response.status_code == status.HTTP_200_OK

    comparison.sort(key=lambda x: x[order_by], reverse=asc_or_desc == "DESC")
    assert elements == comparison


@pytest.mark.anyio
async def test_restaurant_creation(client: AsyncClient, fastapi_app: FastAPI) -> None:
    """
    Create a restaurant record, check that exist calling the endpoint with the
    identifier, and finally it delete the resource and review if still exist
    """

    # Retrieve the restaurant created
    url = fastapi_app.url_path_for("add_restaurant")
    response_create_restaurant = await client.post(
        url,
        json={
            "name": "hendrik Martina",
            "site": "http://gloria.gob.mx",
            "email": "Abril.Yez@yahoo.com",
            "phone": "9512389703",
            "street": "41601 Lucia Manzana",
            "city": "Vallechester",
            "state": "Quintana Roo",
            "lat": 19.4373485952783,
            "lng": -99.1278959822006,
            "rating": "4",
        },
    )
    assert response_create_restaurant.status_code == status.HTTP_201_CREATED
    new_restaurant: Dict = response_create_restaurant.json()
    restaurant_id = new_restaurant.get("id")

    # Retrieve the restaurant created
    url = fastapi_app.url_path_for("get_restaurants_by_id", restaurant_id=restaurant_id)
    response_get_restaurant = await client.get(url)
    assert response_get_restaurant.status_code == status.HTTP_200_OK
    assert response_get_restaurant.json() == new_restaurant


@pytest.mark.anyio
async def test_restaurant_deletion(client: AsyncClient, fastapi_app: FastAPI) -> None:
    """
    Create a restaurant record, check that exist calling the endpoint with the
    identifier, and finally it delete the resource and review if still exist
    """

    # Retrieve the restaurant created
    url = fastapi_app.url_path_for("add_restaurant")
    response_create_restaurant = await client.post(
        url,
        json={
            "name": "hendrik Martina",
            "site": "http://gloria.gob.mx",
            "email": "Abril.Yez@yahoo.com",
            "phone": "9512389703",
            "street": "41601 Lucia Manzana",
            "city": "Vallechester",
            "state": "Quintana Roo",
            "lat": 19.4373485952783,
            "lng": -99.1278959822006,
            "rating": "4",
        },
    )
    assert response_create_restaurant.status_code == status.HTTP_201_CREATED
    new_restaurant: Dict = response_create_restaurant.json()
    restaurant_id = new_restaurant.get("id")

    # Delete the restaurant
    url = fastapi_app.url_path_for("delete_restaurant", restaurant_id=restaurant_id)
    response_delete_restaurant = await client.delete(url)
    assert response_delete_restaurant.status_code == status.HTTP_204_NO_CONTENT
    assert response_delete_restaurant.content == b""

    url = fastapi_app.url_path_for("get_restaurants_by_id", restaurant_id=restaurant_id)
    response_get_restaurant = await client.get(url)
    assert response_get_restaurant.status_code == status.HTTP_404_NOT_FOUND
    assert response_get_restaurant.json() == {
        "detail": f"Restaurant {restaurant_id} not found"
    }


@pytest.mark.anyio
async def test_restaurant_update(client: AsyncClient, fastapi_app: FastAPI) -> None:
    """
    Create a restaurant record, check that exist calling the endpoint with the
    identifier, and finally it delete the resource and review if still exist
    """
    restaurant_data = {
            "name": "hendrik Martina",
            "site": "https://gloria.gob.mx",
            "email": "Abril.Yez@yahoo.com",
            "phone": "9512389703",
            "street": "41601 Lucia Manzana",
            "city": "Vallechester",
            "state": "Quintana Roo",
            "lat": 19.4373485952783,
            "lng": -99.1278959822006,
            "rating": 4,
        }
    # Retrieve the restaurant created
    url = fastapi_app.url_path_for("add_restaurant")
    response_create_restaurant = await client.post(
        url,
        json=restaurant_data,
    )
    assert response_create_restaurant.status_code == status.HTTP_201_CREATED
    new_restaurant: Dict = response_create_restaurant.json()
    restaurant_id = new_restaurant.get("id")
    restaurant_data['name'] = "Elvis PResley"
    restaurant_data['city'] = "Oaxaca"


    # update the restaurant information
    url = fastapi_app.url_path_for("update_restaurant", restaurant_id=restaurant_id)
    response_update_restaurant = await client.patch(url, json=restaurant_data)

    assert response_update_restaurant.status_code == status.HTTP_204_NO_CONTENT
    assert response_update_restaurant.content == b""


    url = fastapi_app.url_path_for("get_restaurants_by_id", restaurant_id=restaurant_id)
    response_get_restaurant = await client.get(url)
    assert response_get_restaurant.status_code == status.HTTP_200_OK
    assert response_get_restaurant.json() == {'id': restaurant_id, **restaurant_data}


@pytest.mark.anyio
async def test_healths(
    client: AsyncClient, fastapi_app: FastAPI, dbpool: AsyncConnectionPool
) -> None:
    """
    Checks the health endpoint.

    :param client: client for the app.
    :param fastapi_app: current FastAPI application.
    """
    async with dbpool.connection() as conn_check:
        res = await conn_check.execute(
            """SELECT * FROM restaurants"""
        )
        await res.fetchall()

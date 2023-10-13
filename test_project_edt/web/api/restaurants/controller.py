from typing import List

from fastapi import APIRouter, Depends, status


from test_project_edt.db.models.restaurant import Restaurant
from test_project_edt.db.models.statistics import Statistics
from test_project_edt.repository.pyscopg_restaurant_repository import \
    PsycopgRestaurantRepository
from test_project_edt.repository.resturant_repository_protocol import \
    RestaurantRepository
from test_project_edt.entities.http_entities import (ClientError,
                                                     ClientErrorType)
from test_project_edt.entities.restaurant import (CreateRestaurantValidator,
                                                  UpdateRestaurantValidator)

router = APIRouter()


@router.get("/restaurants")
async def get_all_restaurants(
    repository: RestaurantRepository = Depends(lambda: PsycopgRestaurantRepository())
) -> List[Restaurant]:

    return await repository.get_all()

@router.get("/restaurants/statistics")
async def get_restaurants_statistics(
    latitude: float,
    longitude:float,
    radius: float,
    repository: RestaurantRepository = Depends(lambda: PsycopgRestaurantRepository())
) -> Statistics:

    return await repository.get_statistics(latitude, longitude, radius)

@router.get("/restaurants/{restaurant_id}")
async def get_all_restaurants(
    restaurant_id: str,
    repository: RestaurantRepository = Depends(lambda: PsycopgRestaurantRepository())
) -> Restaurant:

    result = await repository.get(restaurant_id)
    if not result:
        raise ClientError(client_error_type=ClientErrorType.NOT_FOUND,
                          message=f'Restaurant of id {restaurant_id} does not exist')
    return result


@router.post("/restaurants",
             status_code=status.HTTP_201_CREATED)
async def add_restaurant(
    restaurant_information: CreateRestaurantValidator,
    repository: RestaurantRepository = Depends(lambda: PsycopgRestaurantRepository())
) -> Restaurant:

    return await repository.add(Restaurant(**restaurant_information.model_dump()))


@router.patch("/restaurants/{restaurant_id}",
              status_code=status.HTTP_204_NO_CONTENT)
async def update_restaurant(
    restaurant_id: str,
    restaurant_information: UpdateRestaurantValidator,
    repository: RestaurantRepository = Depends(lambda: PsycopgRestaurantRepository())
):

    print(Restaurant(**restaurant_information.model_dump(exclude_none=True, exclude={'id'})))
    await repository.update(restaurant_id,
                            Restaurant(**restaurant_information.model_dump()))


@router.delete("/restaurants/{restaurant_id}",
              status_code=status.HTTP_204_NO_CONTENT)
async def delete_restaurant(
    restaurant_id: str,
    repository: RestaurantRepository = Depends(lambda: PsycopgRestaurantRepository())
):


    await repository.delete(restaurant_id)

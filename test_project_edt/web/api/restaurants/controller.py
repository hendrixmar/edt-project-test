from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from test_project_edt.db.dependencies import inject_repository
from test_project_edt.db.models.restaurant import Restaurant
from test_project_edt.db.models.statistics import Statistics
from test_project_edt.entities.common import PaginationParams
from test_project_edt.entities.restaurant import (
    CreateRestaurantValidator,
    UpdateRestaurantValidator,
)
from test_project_edt.repository.resturant_repository_protocol import (
    RestaurantRepository,
)

router = APIRouter()


@router.get("/restaurants")
async def get_all_restaurants(
    repository: RestaurantRepository = Depends(inject_repository),
    params: PaginationParams = Depends(),
) -> List[Restaurant]:
    """Retrieve a list of restaurants with optional pagination parameters."""

    return await repository.get_all(params)


@router.get("/restaurants/statistics")
async def get_restaurants_statistics(
    latitude: float,
    longitude: float,
    radius: float,
    repository: RestaurantRepository = Depends(inject_repository),
) -> Statistics:
    """Return statistics about how many restaurant exist in certain area, the average
    of the rating and the standard deviation of the rating."""
    return await repository.get_statistics(latitude, longitude, radius)


@router.get("/restaurants/{restaurant_id}")
async def get_restaurants_by_id(
    restaurant_id: str,
    repository: RestaurantRepository = Depends(inject_repository),
) -> Restaurant:
    """Retrieve a restaurant by its unique identifier."""
    result = await repository.get(restaurant_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Restaurant {restaurant_id} not found",
        )

    return result


@router.post("/restaurants", status_code=status.HTTP_201_CREATED)
async def add_restaurant(
    restaurant_information: CreateRestaurantValidator,
    repository: RestaurantRepository = Depends(inject_repository),
) -> Restaurant:
    """Create a new restaurant with the provided information."""
    return await repository.add(Restaurant(**restaurant_information.model_dump()))


@router.patch("/restaurants/{restaurant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_restaurant(
    restaurant_id: str,
    restaurant_information: UpdateRestaurantValidator,
    repository: RestaurantRepository = Depends(inject_repository),
):
    """Update an existing restaurant's information based on its unique identifier."""
    await repository.update(
        restaurant_id, Restaurant(**restaurant_information.model_dump())
    )


@router.delete("/restaurants/{restaurant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_restaurant(
    restaurant_id: str,
    repository: RestaurantRepository = Depends(inject_repository),
):
    """Delete a restaurant based on its unique identifier."""
    await repository.delete(restaurant_id)

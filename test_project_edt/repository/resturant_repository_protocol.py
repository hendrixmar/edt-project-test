from typing import Protocol, runtime_checkable, List

from test_project_edt.db.models.restaurant import Restaurant


@runtime_checkable
class RestaurantRepository(Protocol):

    async def get_all(self) -> List[Restaurant]:
        ...

    async def get(self, restaurant_id: str) -> Restaurant:
        ...

    async def delete(self, restaurant_id: str) -> Restaurant:
        ...

    async def add(self, restaurant_data: Restaurant) -> Restaurant:
        ...

    async def update(self,
                     restaurant_id: str,
                     restaurant_data: Restaurant) -> Restaurant:
        ...

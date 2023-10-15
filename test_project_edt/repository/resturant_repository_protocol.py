from typing import List, NoReturn, Protocol, runtime_checkable

from test_project_edt.db.models.restaurant import Restaurant
from test_project_edt.db.models.statistics import Statistics
from test_project_edt.entities.common import PaginationParams


@runtime_checkable
class RestaurantRepository(Protocol):

    async def get_all(self, pagination_param: PaginationParams) -> List[Restaurant]:
        ...

    async def get(self, restaurant_id: str) -> Restaurant | None:
        ...

    async def delete(self, restaurant_id: str) -> NoReturn:
        ...

    async def add(self, restaurant_data: Restaurant) -> Restaurant:
        ...

    async def update(self,
                     restaurant_id: str,
                     restaurant_data: Restaurant) -> Restaurant | None:
        ...


    async def get_statistics(self,
                             latitude: float,
                             longitude: float,
                             radius: float,) -> Statistics:
        ...

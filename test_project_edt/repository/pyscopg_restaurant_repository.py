from typing import Dict, List, NoReturn

from psycopg import AsyncConnection, AsyncCursor, AsyncServerCursor
from psycopg_pool import AsyncConnectionPool
from pydantic import TypeAdapter

from test_project_edt.db.models.restaurant import Restaurant
from test_project_edt.db.models.statistics import Statistics
from test_project_edt.entities.common import PaginationParams


class PsycopgRestaurantRepository:
    """Restaurant repository using Postgresql with psycopg."""

    def __init__(self, connection: AsyncConnectionPool):
        self._connection = connection.connection

    async def get_all(self, pagination_params: PaginationParams) -> List[Restaurant]:
        """Retrieve all the restaurant using pagination parameters."""

        params_dict = pagination_params.model_dump(mode="json")
        conn: AsyncConnection[Restaurant]
        conn_check: AsyncCursor | AsyncServerCursor
        async with self._connection() as conn:
            async with conn.cursor() as conn_check:
                res = await conn_check.execute(
                    f"""SELECT * FROM restaurants
                        ORDER BY {params_dict['order_by']} {params_dict['asc_or_desc']}
                        LIMIT %(limit)s
                        OFFSET %(offset)s;
                    """,
                    params=params_dict,
                )
                rows = await res.fetchall()
                return [Restaurant(**row) for row in rows]

    async def get(self, restaurant_id: str) -> Restaurant | None:
        """Retrieve a restaurant by their unique identifier."""

        conn: AsyncConnection
        conn_check: AsyncCursor | AsyncServerCursor

        async with self._connection() as conn:
            async with conn.cursor() as conn_check:
                res = await conn_check.execute(
                    "SELECT * FROM restaurants where id = %(id)s",
                    params={"id": restaurant_id},
                )
                row: Dict[str, str | int | float] | None = await res.fetchone()
                if not row:
                    return None
                return Restaurant(**row)

    async def delete(self, restaurant_id: str) -> NoReturn:

        """
        Delete a restaurant record using their unique identifier.
        """
        async with self._connection() as conn:
            async with conn.cursor() as conn_check:
                await conn_check.execute(
                    "DELETE FROM restaurants where id = %(id)s;",
                    params={"id": restaurant_id},
                )

    async def add(self, restaurant_data: Restaurant) -> Restaurant:
        async with self._connection() as conn:
            async with conn.cursor() as conn_check:
                await conn_check.execute(
                    """
                        INSERT INTO Restaurants (
                        id, rating, name,
                        site, email, phone,
                        street, city, state, lat, lng
                        ) VALUES
                        (%(id)s, %(rating)s, %(name)s,
                        %(site)s, %(email)s, %(phone)s,
                        %(street)s, %(city)s, %(state)s, %(lat)s, %(lng)s);
                    """,
                    params=TypeAdapter(Restaurant).dump_python(restaurant_data),
                )

                return restaurant_data

    async def update(
        self,
        restaurant_id: str,
        restaurant_data: Restaurant
    ) -> Restaurant | None:

        if not await self.get(restaurant_id):
            return None

        async with self._connection() as conn:
            async with conn.cursor() as conn_check:
                temp_data: Dict[str, str | int | float] = TypeAdapter(
                    Restaurant
                ).dump_python(restaurant_data, exclude_none=True, exclude={"id"})
                set_arguments: str = f",".join(
                    f"{key} = %({key})s" for key, _ in temp_data.items()
                )

                await conn_check.execute(
                    f"""
                        UPDATE Restaurants
                            SET {set_arguments}
                        WHERE id = %(id)s;
                    """,
                    params={"id": restaurant_id, **temp_data},
                )

                return restaurant_data

    async def get_statistics(
        self, latitude: float, longitude: float, radius: float
    ) -> Statistics:
        async with self._connection() as conn:
            async with conn.cursor() as conn_check:
                res = await conn_check.execute(
                    """
                       SELECT count(*), avg(rating), stddev(rating)
                        FROM restaurants
                        WHERE ST_DWithin(
                            ST_SetSRID(ST_MakePoint(lng, lat),4326)::GEOGRAPHY,
                            ST_SetSRID(
                                ST_MakePoint(%(longitude)s, %(latitude)s),
                                4326)::GEOGRAPHY,
                            %(radius)s);
                    """,
                    params={"latitude": latitude, "longitude": longitude, "radius": radius},
                )
                row: Dict[str, float] | None = await res.fetchone()
                return Statistics(**row)

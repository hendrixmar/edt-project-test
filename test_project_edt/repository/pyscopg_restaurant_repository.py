from typing import List, NoReturn, Dict

from psycopg_pool import AsyncConnectionPool
from pydantic import TypeAdapter

from test_project_edt.db.models.restaurant import Restaurant

from test_project_edt.db.models.statistics import Statistics


class PsycopgRestaurantRepository:
    def __init__(self, connection: AsyncConnectionPool):
        self.__connection = connection

    async def get_all(self) -> List[Restaurant]:
        async with (self.__connection() as conn,
                    conn.cursor() as conn_check):
            res = await conn_check.execute(
                """SELECT *
                    FROM restaurants
                    """

            )
            rows = await res.fetchall()
            return [Restaurant(**row) for row in rows]

    async def get(self, restaurant_id: int) -> Restaurant | None:
        async with (self.__connection() as conn,
                    conn.cursor() as conn_check):
            res = await conn_check.execute(
                """SELECT *
                    FROM restaurants
                    where id = %(id)s
                    """,
                params={
                    "id": restaurant_id,
                }
            )
            row = await res.fetchone()
            if not row:
                return None
            return Restaurant(**row)

    async def delete(self, restaurant_id: int) -> NoReturn:
        async with (self.__connection() as conn,
                    conn.cursor() as conn_check):
            await conn_check.execute(
                """
                   DELETE
                    FROM restaurants
                    where id = %(id)s;
                """,
                params={
                    "id": restaurant_id,
                }

            )

    async def add(self, restaurant_data: Restaurant) -> Restaurant:
        async with (self.__connection() as conn,
                    conn.cursor() as conn_check):
            await conn_check.execute(
                """
                    INSERT INTO Restaurants (id, rating, name, site, email, phone, street, city, state, lat, lng) VALUES
                    (%(id)s, %(rating)s, %(name)s, %(site)s, %(email)s, %(phone)s, %(street)s, %(city)s, %(state)s, %(lat)s, %(lng)s);
                """,
                params=TypeAdapter(Restaurant).dump_python(restaurant_data)

            )

            return restaurant_data

    async def update(self,
                     restaurant_id: str,
                     restaurant_data: Restaurant) -> Restaurant | None:

        restaurant_exist = await self.get(restaurant_id)
        if not restaurant_exist:
            return None

        async with (self.__connection() as conn,
                    conn.cursor() as conn_check):
            temp_data: Dict = TypeAdapter(Restaurant).dump_python(restaurant_data,
                                                                  exclude_none=True,
                                                                  exclude={'id'})
            set_arguments: str = f",".join(
                f"{k} = %({k})s" for k, v in temp_data.items()
            )
            print(f"""
                    UPDATE Restaurants
                        SET {set_arguments}
                    WHERE id = %(id)s;
                """)
            await conn_check.execute(
                f"""
                    UPDATE Restaurants
                        SET {set_arguments}
                    WHERE id = %(id)s;
                """,
                params={
                    "id": restaurant_id,
                    **temp_data
                }

            )

            return restaurant_data

    async def get_statistics(self,
                             latitude: float,
                             longitude: float,
                             radius: float) -> Statistics:
        async with (self.__connection() as conn,
                    conn.cursor() as conn_check):
            res = await conn_check.execute(
                """
                   SELECT count(*), avg(rating), stddev(rating)
                    FROM restaurants
                    WHERE ST_DWithin(
                        ST_SetSRID(ST_MakePoint(lng, lat),4326)::GEOGRAPHY, -- geometry column of cities table
                        ST_SetSRID(ST_MakePoint(%(longitude)s, %(latitude)s),4326)::GEOGRAPHY, -- target point coordinates in (longitude, latitude) format
                        %(radius)s);
                """,
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "radius": radius
                }

            )
            row = await res.fetchone()
            return Statistics(**row)

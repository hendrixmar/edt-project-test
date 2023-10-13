import uuid

from pydantic import Field, HttpUrl
from pydantic.dataclasses import dataclass

@dataclass
class Restaurant:
    name: str | None = None
    site: str | None = None
    email: str | None = None
    phone: str | None = None
    street: str | None = None
    city: str | None = None
    state: str | None = None
    lat: float | None = None
    lng: float | None = None
    rating: int | None = Field(default=None, gte=0, lte=4)
    id: str = str(uuid.uuid4())
    rating: int = Field(gte=0, lte=4)

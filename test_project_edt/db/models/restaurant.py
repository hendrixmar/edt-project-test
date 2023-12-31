import uuid

from pydantic import Field
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
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))

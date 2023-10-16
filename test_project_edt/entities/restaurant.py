from pydantic import BaseModel, Field


class CreateRestaurantValidator(BaseModel):
    name: str
    site: str
    email: str
    phone: str
    street: str
    city: str
    state: str
    lat: float
    lng: float
    rating: int = Field(gte=0, lte=4)


class UpdateRestaurantValidator(BaseModel):
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

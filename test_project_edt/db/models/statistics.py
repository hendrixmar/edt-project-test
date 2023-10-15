from typing import Annotated

from pydantic import BeforeValidator, Field
from pydantic.dataclasses import dataclass


@dataclass
class Statistics:
    count: int = Field(gte=0)
    avg: Annotated[float, BeforeValidator(lambda v: v or 0)] = Field(gte=0)
    std: Annotated[float, BeforeValidator(lambda v: v or 0)] = Field(gte=0, alias="stddev")

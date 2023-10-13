from pydantic import Field, HttpUrl
from pydantic.dataclasses import dataclass

@dataclass
class Statistics:
    count: int = Field(gte=0)
    avg: float = Field(gte=0)
    std: float = Field(gte=0, alias="stddev")

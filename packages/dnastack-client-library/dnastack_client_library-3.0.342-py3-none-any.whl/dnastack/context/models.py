from typing import Dict, List
from uuid import uuid4

from pydantic import BaseModel, Field

from dnastack import ServiceEndpoint as Endpoint


class Context(BaseModel):
    model_version: float = 1.0

    # For debugging
    guid:  str = Field(default_factory=lambda: str(uuid4()))

    # This is the short-type-to-service-id map.
    defaults: Dict[str, str] = Field(default_factory=lambda: dict())

    endpoints: List[Endpoint] = Field(default_factory=lambda: list())

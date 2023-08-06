import re
from datetime import datetime
from time import time
from typing import Optional, List, Any, Dict

from pydantic import BaseModel, Field


class Tag(BaseModel):
    id: str
    label: str


class Collection(BaseModel):
    """
    A model representing a collection

    .. note:: This is not a full representation of the object.
    """

    id: Optional[str]
    name: str
    slugName: str
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    description: Optional[str]
    itemsQuery: str
    tags: Optional[List[Tag]] = Field(default_factory=list)
    createdAt: datetime
    updatedAt: Optional[datetime]
    dbSchemaName: Optional[str]
    itemsChangedAt: Optional[datetime]
    latestItemUpdatedTime: Optional[datetime]
    # accessTypeLabels: Optional[Dict[str, str]] = Field(default_factory=dict)  # FIXME Uncomment this and ensure that CLI command filters this field out.
    # itemCounts: Optional[Dict[str, int]] = Field(default_factory=dict)  # FIXME Uncomment this and ensure that CLI command filters this field out.

    @classmethod
    def make(cls,
             name: str,
             items_query: str,
             slug_name: Optional[str] = None,
             description: Optional[str] = None):
        if not slug_name:
            slug_name = re.sub(r'[^a-z0-9-]', '-', name.lower()) + str(int(time()))
            slug_name = re.sub(r'-+', '-', slug_name)
        return cls(name=name, itemsQuery=items_query, slugName=slug_name, description=description)
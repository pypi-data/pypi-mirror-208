from typing import List

from pydantic import BaseModel

from bpkio_api.models.common import BaseResource, NamedModel


class SubCategory(BaseModel):
    key: str
    value: str


class CategoryIn(NamedModel):
    subcategories: List[SubCategory] = []


class Category(BaseResource, CategoryIn):
    pass

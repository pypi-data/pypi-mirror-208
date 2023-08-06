"""Define base and common pydantic models"""

from typing import Optional
from pydantic import BaseModel, Extra


class Base(BaseModel):
    """Base model reference"""
    class Config:
        """Setup common config"""
        extra = Extra.allow


class ResponseModel(Base):
    code: str  # '200'
    message: str  # 'Operation success',
    status: str  # 'success',
    version: str  # '2'


class Link(Base):
    first: Optional[str]  # http://hostname/api/nodes?page=1
    last: Optional[str]  # http://hostname/api/nodes?page=1
    prev: Optional[str]  # number | null
    next: Optional[str]  # number | null


class Meta(BaseModel):
    """
    Similar to other Meta models
    """
    current_page: Optional[int]  # 1,
    from_: Optional[int]  # 1,
    last_page: Optional[int]  # 1,
    path: Optional[str]  # http://hostname/api/nodes,
    per_page: Optional[int]  # 15,
    to: Optional[int]  # 2,
    total: Optional[int]  # 2,
    all_count: Optional[int]  # number,
    filter_count: Optional[int]  # number

    class Config:
        fields = {"from_": "from"}

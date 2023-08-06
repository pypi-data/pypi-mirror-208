from enum import Enum, unique
from typing import List

from pydantic import BaseModel, Field

from .base_models import Link, ResponseModel, Meta


@unique
class DireccionRequest(str, Enum):
    """Allowed values for Dir in Requests"""
    n_s = "N-S"
    e_w = "E-W"
    ne_sw = "NE-SW"
    nw_se = "NW-SE"


@unique
class VehicleType(str, Enum):
    pedestrian = "pedestrian"
    vehicle = "vehicle"
    bicycle = "bicycle"


class CounterObject(BaseModel):
    time: str   # "2020-11-08 00:00"
    location_uid: str = Field(..., alias='locationUid')
    dir: str
    count: int
    vehicle_type: VehicleType
    pole_id: str
    node_id: str


class TrafficMobilityResponse(ResponseModel):
    data: List[CounterObject]
    meta: Meta
    links: Link

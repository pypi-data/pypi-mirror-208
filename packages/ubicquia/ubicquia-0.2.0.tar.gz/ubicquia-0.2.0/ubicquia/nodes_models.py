from typing import List, Optional  # , Union

from pydantic import BaseModel, Field
from .base_models import Link, ResponseModel, Base, Meta


class GenericStatus(Base):
    color: Optional[str]
    status: Optional[str]
    type: Optional[str]
    value: Optional[str]  # value: int
    units: Optional[str]
    font_color: Optional[str]


class ParentNodes(Base):
    parent_name_L1: Optional[str]
    parent_id_L1: Optional[float]
    parent_level_L1: Optional[float]
    parent_name_L2: Optional[float]
    parent_id_L2: Optional[float]
    parent_level_L2: Optional[float]


class Node(BaseModel):
    id: int
    latitude: Optional[str]
    createdate: Optional[str]  # yyyy-mm-dd hh:mm:ss
    node: Optional[str]
    longitude: Optional[str]
    HDOP: Optional[int]
    overrideGPS: Optional[int]
    deleted: bool
    active: bool
    isActive: bool
    nodetype: Optional[str]
    dev_eui: Optional[str]  # value
    newnode: Optional[int]
    groupId: Optional[int]
    poleId: Optional[int]
    poleTypeId: Optional[int]
    fixtureId: Optional[int]
    fixtureTypeId: Optional[int]
    imagePath: Optional[str]
    CState: Optional[int]
    C1State: Optional[int]
    VState: Optional[int]
    V1State: Optional[int]
    nodeTypeId: Optional[int]
    twinPole: bool
    poleColor: Optional[str]
    poleHeight: Optional[str]
    maintenanceCompany: Optional[str]
    pole_id: Optional[int]
    poleType: Optional[str]
    fixture_id: Optional[int]
    fixtureType: Optional[int]
    dualDim: int
    on_cycles: int
    off_cycles: int
    fixture_cycles: str  # On: 0 Off: 0,
    running_hours: str
    node_events_checked_at: str  # yyyy-mm-dd hh:mm:ss
    updatedAt: str  # yyyy-mm-dd hh:mm:ss
    deactivatedAt: Optional[str]
    node_level_type_id: int
    parent_id: Optional[int]
    Description: Optional[str]
    poleTypeName: Optional[str]
    poleTypeCreatedAt: Optional[str]  # yyyy-mm-dd hh:mm:ss
    poleTypeUpdatedAt: Optional[str]  # yyyy-mm-dd hh:mm:ss
    groupName: Optional[str]
    zoneId: Optional[int]
    zoneName: Optional[str]
    gpsLatitude: Optional[int]
    gpsLongitude: Optional[int]
    cns_id: int
    nodeState: Optional[str]
    versionState: str
    LState: int
    yState: Optional[str]
    RqState: Optional[int]
    LD1State: int  # dim value
    LD2State: Optional[int]
    LPState: int
    LhState: Optional[int]
    LThOffState: int
    LthOnState: int
    SState: int
    RaState: Optional[str]
    bState: int
    FFState: Optional[int]
    BBState: Optional[int]
    TTState: int
    VtSagState: int
    VTSwellState: int
    PFState: int
    LFState: int
    yDState: int
    createdDateTime: str  # yyyy-mm-dd hh:mm:ss
    updatedDateTime: str  # yyyy-mm-dd hh:mm:ss
    StrayV: bool
    stray_voltage_status: str
    fixture_wattage: Optional[int]
    state: str
    SHState: str
    power: Optional[str]
    # custom1: Optional[str]
    # custom2: Optional[str]
    # custom3: Optional[str]
    # custom4: Optional[str]
    # custom5: Optional[str]
    # custom6: Optional[str]
    # custom7: Optional[str]
    # custom8: Optional[str]
    # custom9: Optional[str]
    # custom10: Optional[str]
    # custom11: Optional[str]
    # custom12: Optional[str]
    # custom13: Optional[str]
    # custom14: Optional[str]
    # custom15: Optional[str]
    # custom16: Optional[str]
    # custom17: Optional[str]
    # custom18: Optional[str]
    # custom19: Optional[str]
    # custom20: Optional[str]
    parent_nodes: Optional[ParentNodes]
    temperature_c: Optional[int]
    temperature_f: Optional[int]
    humidity: Optional[int]
    pressure: Optional[int]
    pm1_0: Optional[int]
    pm2_5: Optional[int]
    pm10: Optional[int]
    so2: Optional[int]
    o3: Optional[int]
    co: Optional[int]
    no2: Optional[int]
    noise_level: Optional[int]
    aqi: Optional[int]
    primary_pollutant: Optional[str]
    aq_updated_date: Optional[str]  # mm/dd/yy
    aq_updated_time: Optional[str]  # h:s:i A,
    command_status: Optional[str]
    light_status: str
    aqi_status: Optional[GenericStatus]
    sensor_initialized: bool
    powerFactorState: Optional[int]
    ambient_temperature_c: Optional[int]
    ambient_temperature_f: Optional[int]
    dsState: Optional[int]
    circuit_switch: int


class NodeListResponse(ResponseModel):
    # data: Union[List[Node], Node]
    data: List[Node]
    links: Optional[Link]
    meta: Optional[Meta]


class NodeResponse(ResponseModel):
    data: Node


class DiscoverDeviceData(BaseModel):
    lp_state: int = Field(..., alias='LPState')
    dali: str
    dali_status: str
    dev_eui: str
    id: int
    latitude: Optional[str]
    longitude: Optional[str]
    updated_date_time: str = Field(..., alias='updatedDateTime')


class DiscoverDeviceMeta(BaseModel):
    all_count: int
    filter_count: int


class DiscoverDevices(ResponseModel):
    data: List[DiscoverDeviceData] = []
    meta: DiscoverDeviceMeta
    timestamp: str

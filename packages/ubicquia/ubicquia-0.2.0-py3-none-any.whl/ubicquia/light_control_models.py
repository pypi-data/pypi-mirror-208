from typing import List, Dict
from .base_models import ResponseModel, Base


class UserModel(Base):
    type: str
    id: str


class CommandPayload(Base):
    # ids: Ids
    ids: List[Dict[str, int]]  # [{'id': 0}]
    CommandEnum: int
    commandValue: int
    ObjectType: str
    user: UserModel


class LightControlModel(Base):
    devEui: str  # string,
    command_payload: CommandPayload
    command_id: str  # number,
    command_status: str  # string,
    attempts: str  # number,
    delay: str  # number,
    id: int  # number
    attempts: int
    command_id: int
    delay: int


class LightControlResponse(ResponseModel):
    """
    Example
    {
        'data': {
            'devEui': '6ac4584a3ff23m34',
            'command_payload': {
                'ids': [{'id': 1}],
                'CommandEnum': 0,
                'commandValue': 0,
                'ObjectType': 'nodes',
                'user': {
                    'type': 'UbiVu',
                    'id': 'ab3112f-d190-4c4d-b18e-d4803c9d0111'
                }
            },
            'command_id': 0,
            'command_status': 'in progress',
            'attempts': 3,
            'delay': 10,
            'id': 6
        },
        'status': 'success',
        'message': 'Operation success',
        'code': '200',
        'version': '2'
    }
    """
    data: LightControlModel


class LightControlSetDim(Base):
    commandElement: str
    controlDescription: str
    controlName: str
    id_list: list
    response_status: bool
    value: int


class LightControlSetDimResponse(ResponseModel):
    """Example:

    {
        'code': '200',
        'data': {
            'commandElement': 'nodes',
            'controlDescription': 'This command will dim the light',
            'controlName': 'Lamp Dim',
            'id_list': [{'id': 1}],
            'response_status': True,
            'value': 5
        },
        'message': 'Operation success',
        'status': 'success',
        'version': '2'
    }
    """
    data: LightControlSetDim

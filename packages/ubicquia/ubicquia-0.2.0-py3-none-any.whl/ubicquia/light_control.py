import logging
from enum import IntEnum
from typing import List, Union
from .base import Endpoint
from . import light_control_models as models

logger = logging.getLogger(__name__)


class NodeLevelTypeId(IntEnum):
    """Complement the parameter node_level_type_id."""
    node: int = 1
    group: int = 2
    zone: int = 3


class LightControlUtils:
    @staticmethod
    def convert_id_list(id_list: list):
        """
        Convert list of int into adecuate list
        """
        container = []
        for _id in id_list:
            container.append({'id': _id})
        return container


class LightControl(Endpoint, LightControlUtils):
    def set_light_state(self,
                        id_list: List[int],
                        value: Union[bool, int],
                        node_level_type_id: int = 1) -> models.LightControlResponse:
        """Turn on/off lights.

        Turn Light On/Off by sending command to MQTT server.

        Common API error HTTP 429 when requesting some ID's:
        {
            'status': 'failed', code': 409,
            'message': 'Command already exist with same value',
            'version': '2'
        }

        Args:
            id_list: List of ID's
            value: value of node to set. (Use 0 or 1)
            node_level_type_id: Node Level Type Id (1-Node | 2-Group | 3-Zone)

        Returns:
            LightControl

        Raises:
            HTTP Errors.
        """

        if isinstance(value, int) and value not in [0, 1]:
            logger.error(f'value must be 0=OFF, 1=ON. Not {value}')
            raise ValueError(f'value must be 0=OFF, 1=ON. Not {value}')

        if isinstance(value, bool):
            value = 1 if value is True else 0

        data = {
            'id_list': self.convert_id_list(id_list),
            'value': value,
            'node_level_type_id': node_level_type_id
        }
        # print( data)
        url = self.base_url + '/nodes/setLightState'
        d = self.session.req('post', url, json=data)
        return models.LightControlResponse(**d)

    def set_light_dim(self,
                      id_list: List[int],
                      value: int,
                      node_level_type_id: Union[NodeLevelTypeId, int] = 1,
                      dim_type: str = 'LD1State') -> models.LightControlSetDimResponse:
        """Set Light dim by sending command to MQTT server.

        API response considerations:
        1. dim_type: should be LD1State or http 422 Unprocessable Entity,
        2. value: Value must be between 5 and 100 or http 404

        Args:
            id_list: List of ID's
            value: value of node to set
            node_level_type_id: Node Level Type Id (1-Node | 2-Group | 3-Zone)
            dim_type: Dim Value type

        Returns:

        Raises:
            HTTP Errors.
        """
        url = self.base_url + '/nodes/setLightDim'
        # if value < 5 or value > 100:
        #     raise ValueError('API requirement: value must in 5-100')
        data = {
            'id_list': self.convert_id_list(id_list),
            'value': value,
            'node_level_type_id': node_level_type_id,
            'dim_type': dim_type
        }
        d = self.session.req('post', url, json=data)
        return models.LightControlSetDimResponse(**d)

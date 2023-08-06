from . import nodes_models as models
from .base import Endpoint


class Nodes(Endpoint):
    def get_nodes_list(self, node_status: int = None,
                       group: str = '',
                       zone: str = '',
                       rssi: str = '',
                       schedule: int = None,
                       q: str = '', **pagination) -> models.NodeListResponse:
        """
        Args:
            node_status: 1|0|-1|-2
            group:
            zone:
            rssi: excellent|good|fair|poor
            schedule:
            q:

        Returns:

        Raises:
            ValueError:
        """
        url = self.base_url + '/getnodeslist'
        parameter = {}
        if node_status:
            if node_status not in [None, -2, -1, 1, 2]:
                raise ValueError('Invalid node_status. Use accepted values')
            parameter['node_status'] = node_status
        if group:
            parameter['group'] = group
        if zone:
            parameter['zone'] = zone
        if rssi:
            if rssi not in ['', 'excellent', 'good', 'fair', 'poor']:
                raise ValueError('Invalid rssi. Use accepted values')
            parameter['rssi'] = rssi
        if schedule:
            parameter['schedule'] = schedule
        if q:
            parameter['q'] = q
        params = {**parameter, **self.pagination(**pagination)}
        d = self.session.req('get', url, params=params)
        return models.NodeListResponse(**d)

    def get_node_by_id(self,
                       id: int,
                       node_type: str = 'light',
                       air_quality: str = '',
                       periods: str = '',
                       **pagination) -> models.NodeResponse:
        """
        Args:
            id: node id
            node_type: use light|aqi
            air_quality: only for node_type='aqi',
                air-quality like pm_2_5, pm_10, pm1_0, o3, so2, no2, co,
                noise_level, temperature, humidity, pressure, aqi.
            periods: only for node_type='aqi',
                periods like today, yesterday, week, month, year.

        Returns:
            List of Nodes.

        Raises:
            ValueError: for invalid parameter values
        """
        url = self.base_url + f'/nodes/{id}'

        parameter = {'type': node_type}
        if node_type not in ['light', 'aqi']:
            raise ValueError('Invalid node_type')
        if air_quality:
            parameter['air-quality'] = air_quality
        if periods:
            parameter['periods'] = periods
        params = {**parameter, **self.pagination(**pagination)}
        d = self.session.req('get', url, params=params)
        return models.NodeResponse(**d)

    def current_node_state(self, is_active: int = 1
                           ) -> models.NodeListResponse:
        """Returns a list of node state.

        Args:
            is_active: for active nodes. Values accepted 1 | 0

        Returns:
            List of Nodes.

        Raises:
            HTTP Errors.
        """
        url = self.base_url + '/currentnodestate'

        if is_active not in [0, 1]:
            raise ValueError('Invalid value')
        params = {'isActive': is_active}
        d = self.session.req('get', url, params=params)
        return models.NodeListResponse(**d)

    def discover_devices(self) -> models.DiscoverDevices:
        """Discover all ubicells for a customer.

        This endpoint method is not offically documented. Example of part of the
        data:

         .. code:: python

            {"data": [
                {
                    "LPState": -2,
                    "dali": "No",
                    "dali_status": "",
                    "dev_eui": "...",
                    "id": 1,
                    "latitude": "...",
                    "longitude": "...",
                    "updatedDateTime": "2022-11-25 13:18:10"
                }],
            ...}

        Returns:
            Devices and their states.

        Raises:
            HTTP Errors.
        """
        url = self.base_url_v2 + '/map/nodes/light'
        d = self.session.req('post', url)
        return models.DiscoverDevices(**d)

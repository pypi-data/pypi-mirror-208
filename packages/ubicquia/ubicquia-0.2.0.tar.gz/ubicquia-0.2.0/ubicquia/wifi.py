"""Wifi operations about UbiWifi"""

from typing import List, Union

from pydantic import BaseModel
from . import wifi_captive_portal as captive_portal
from .base import Endpoint


class NetworkDataModel(BaseModel):
    """
    Attributes:
        is_hotspot: Must be True or error:
            {'status': 'failed', 'code': 422,
            'message': 'Please select minimum 1 HotSpot', 'version': '2'}
    """
    wifi_venue_network_id: int  # ? I think it referets to SSID ID
    network_id: int  # ? I think it referets to SSID ID
    max_uplink: str = ''
    max_downlink: str = ''
    is_hotspot: bool = True
    hide_ssid: bool = False
    vlan_id: int
    traffic_shaping: bool = False
    traffic_shaping_json: List[dict] = [
        {
            "user_group": "string",
            "ingressRateclass": 0,
            "egressRateclass": 0
        }
    ]


class VenueDataModel(BaseModel):
    name: str
    description: str
    channel_id: int  # wifi network channels
    portal_id: int  # Captive portal id
    networks: List[NetworkDataModel]


class Venues(Endpoint):
    """Join wifi/venues and wifi/venue

    To make a more consistent design, join /venue and /venues
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.url = self.base_url_v2 + '/wifi'
        self.url_venues = self.base_url_v2 + '/wifi/venues'
        self.url_venue = self.base_url_v2 + '/wifi/venue'

    def list(self, sort_by: str = '', sort_dir: str = 'asc', q: str = '',
             **pagination) -> dict:
        """List all Venues.
        Args:
            sort_by: Sort by field, like name.
            sort_dir: Sort direction.
            q: Query.
            pagination: Pagination extra parameters.

        Returns:
            List of Venues.

        Raises:
            HTTTPError.
        """
        params = {
            'sort_by': sort_by,
            'sort_dir': sort_dir,
            'q': q,
            **pagination
        }
        d = self.session.req('get', self.url_venues, params=params)
        return d

    def create(self, data: Union[VenueDataModel, dict]) -> dict:
        """
        Args:
            id: Venue id.
            data: Venue data.

        Returns:
            Venue data.

        Raises:
            HTTPError.
        """
        data = data.dict() if not isinstance(data, dict) else data
        d = self.session.req('post', self.url_venues, json=data)
        return d

    def update_by_id(self, id: int, data: Union[VenueDataModel, dict]) -> dict:
        """Update a Venue by id.
        Args:
            id: Venue id.
            data: Venue data.

        Returns:
            Venue data.

        Raises:
            HTTPError.
        """
        url = self.url + f'/{id}/venue'
        data = data.dict() if not isinstance(data, dict) else data
        d = self.session.req('put', url, json=data)
        return d

    def delete_by_id(self, id: int) -> dict:
        """Delete a Venue by id.
        Args:
            id: Venue id.

        Returns:


        Raises:
            HTTPError.
        """
        url = self.url_venue + f'/{id}'
        d = self.session.req('delete', url)
        return d

    def get_by_id(self, id: int) -> dict:
        """Get a Venue by id.
        Args:
            id: Venue id.

        Returns:
            Venue data.

        Raises:
            HTTPError.
        """
        url = self.url_venue + f'/{id}'
        d = self.session.req('get', url)
        return d


class Vlan(Endpoint):
    """wifi/vlans sub-endpoint

    Operations related to VLANs.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = self.base_url_v2 + '/wifi' + '/vlans'

    def list(self, sort_by: str = '', sort_dir: str = '', q: str = '',
             **pagination) -> dict:
        """List all VLANs.
        Args:
            sort_by: Sort by field.
            sort_dir: Sort direction.
            q: Query.
            pagination: Pagination extra parameters.

        Returns:
            List of VLANs.

        Raises:
            HTTTPError.
        """
        params = {
            'sort_by': sort_by,
            'sort_dir': sort_dir,
            'q': q,
            **pagination
        }
        d = self.session.req('get', self.url, params=params)
        return d


class WirelessNetwork(Endpoint):
    """wireless-network"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = self.base_url_v2 + '/wifi' + '/wireless-network'

    def list(self, sort_by: str = '', sort_dir: str = '', q: str = '',
             **pagination) -> dict:
        """Get wifi network list (SSID)

        Args:
            sort_by: Sort by field.
            sort_dir: Sort direction.
            q: Query.

        Returns:
            A list of wireless networks.
        """
        params = {
            'sort_by': sort_by,
            'sort_dir': sort_dir,
            'q': q,
            **pagination
        }
        d = self.session.req('get', self.url, params=params)
        return d


class Wifi(Endpoint):
    """Wifi operations about UbiWifi

    Expose wifi as endpoint and sub-endpoints declared in __init__ method.

    Depencencies classes:

    - captive_portal.CaptivePortal
    - vlan.Vlan
    - wireless_network.WirelessNetwork
    - Others...
    """

    def __init__(self, *args, **kwargs):
        """Adding URL.

        This endpoint uses various URLs.
        """
        super().__init__(*args, **kwargs)
        # Define URLs:
        self.url = self.base_url_v2
        # self.url_wifi = self.base_url_v2 + '/wifi'
        # self.url_portal = self.base_url_v2 + '/portal'
        # self.url_toggle_wifi = self.base_url_v2 + '/toggle-wifi'
        # self.url_channel_list = self.base_url_v2 + '/channel-list'

        # Dependencies:
        self.captive_portal = captive_portal.CaptivePortal(self.session)
        self.vlans = Vlan(self.session)
        self.wireless_network = WirelessNetwork(self.session)
        self.venues = Venues(self.session)

    def get_bandwidth_usage_list(self) -> dict:
        """ Get bandwidth usage details with:

        top SSID, Most Active AP, Device list,
        Map and chart (Return unit based on data).

        Args:

        Returns:
            data response.

        Raises:
            HTTPError:
        """
        url = self.url + '/get-bandwidth-usage/list'
        # TODO:
        # Some elements can be used as argument for thi method:
        data = {
            "filter": [
                {
                    "attribute": "",
                    "operator": "",
                    "value": ""
                }
            ],
            "q": "",
            "start_time": "string",
            "end_time": "string",
            "prev_start_time": "string",
            "prev_end_time": "string",
            "aggregation_interval": "string",
            "mac_address": "string",
            "ssid": [
                "string"
            ]
        }
        # ---
        d = self.session.req('post', url, json=data)
        return d

    def get_wifibandwidth_ssid_list(self) -> dict:
        """get list of consumption by SSID.

        Returns:
            A list of bandwidth consumption SSID.
        """
        url = self.url + '/get-wifibandwidth-ssid-list'
        data = {
            "filter": [
                {
                    "attribute": "",
                    "operator": "",
                    "value": ""
                }
            ],
            "q": ""
        }
        d = self.session.req('post', url, json=data)
        return d

    def wifi_network_channel(self, sort_by: str = '', sort_dir: str = '',
                             q: str = '',
                             **pagination) -> dict:
        """List all Wireless Channels.
        Args:
            sort_by: Sort by field.
            sort_dir: Sort direction.
            q: Query.
            pagination: Pagination extra parameters.

        Returns:
            List wifi network channels.

        Raises:
            HTTTPError.
        """
        url = self.url + '/wifi-network-channel'
        params = {
            'sort_by': sort_by,
            'sort_dir': sort_dir,
            'q': q,
            **pagination
        }
        d = self.session.req('get', url, params=params)
        return d

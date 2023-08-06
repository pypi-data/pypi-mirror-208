"""Expose client API"""

# from .alerts import Alerts
from .base import Endpoint, UbicquiaSession
from .light_control import LightControl
from .nodes import Nodes
from .public_safety import PublicSafety
from .reports import Report
from .traffic_mobility import TrafficMobility
from .wifi import Wifi


class Ubicquia:
    """API Interface"""
    def __init__(self, session: UbicquiaSession) -> None:
        # self.alerts = Alerts(base_url=BASE_URL, session=session)
        self.light_control = LightControl(session=session)
        self.nodes = Nodes(session)
        self.public_safety = PublicSafety(session)
        self.session = session
        self.traffic_mobility = TrafficMobility(session)
        self.wifi = Wifi(session)
        self.reports = Report(session)


class RawRequest(Endpoint):
    """Send requests to server that are not in SDK.

    Like REST alpha or beta endpoints, new features not in current SDK, etc.
    """

    def request(self, method: str, url, **requests_params) -> dict:
        """Create a request with custom url, method, etc.

        Args:
            method: HTTP methods. No sense case GET, POST, PUT, PATCH ...
            url: complete url scheme required.
            **requests_params: extra parameters that will be passed to requests.

        Returns:
            Server response in a dict.

        Raises:
            HTTP Errors with requests module exceptions.
        """
        return self.session.req(method, url, **requests_params)

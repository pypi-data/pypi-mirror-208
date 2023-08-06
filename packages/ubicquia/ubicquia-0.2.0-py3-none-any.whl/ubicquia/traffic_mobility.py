"""Traffic & Mobility"""

from . import traffic_mobility_models as models
from .base import Endpoint


class TrafficMobility(Endpoint):
    """Operations about Traffic & Mobility-Tags"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = self.base_url_v2 + '/traffic-mobility'

    def list(self,
             start_date_time: str,
             end_date_time: str,
             count_type: str = 'vehicle',
             response_type: str = 'all',
             direction: models.DireccionRequest = 'N-S',
             vehicle_type: str = 'all',
             aggregation_type: str = 'hourly',
             q: str = '',
             **pagination) -> models.TrafficMobilityResponse:
        """Vehicle Count List.

        Args:
            start_date_time: example '2021-05-01 00:00:00'
            end_date_time: example '2021-05-13 06:30:00'
            count_type: (type) allowed -> vehicle | pedestrian | bicycle
            response_type: official documentation does not exist.
            direction: NW, SE -> 'N-W' | 'S-E' ?
                based on dashboard data. Official documentation does not exist.
            vehicle_type: official documentation does not exist.
            aggregation_type: hourly | daily | monthly.
                 based on dashboard. Official documentation does not exist.
            q: official documentation does not exist.

        Returns:
            TrafficMobilityResponse

        Raises:
            HttpError:
        """
        if direction not in [d.value for d in models.DireccionRequest]:
            raise ValueError(f'Invalid value for direction: {direction}')
        url = self.url + f'/list/{count_type}'
        # params = {**self.pagination(**pagination)}
        data_json = {
            "responseType": response_type,
            "direction": direction,
            "vehicleType": vehicle_type,
            "aggregationType": aggregation_type,
            "startDateTime": start_date_time,
            "endDateTime": end_date_time,
            "filter": [
                {
                    "attribute": "",
                    "operator": "",
                    "value": ""
                }
            ],
            "q": q,
            **self.pagination(**pagination)
            # "page": 1,
            # "per_page": 10
        }
        d = self.session.req('post', url, json=data_json)
        # return d
        return models.TrafficMobilityResponse(**d)

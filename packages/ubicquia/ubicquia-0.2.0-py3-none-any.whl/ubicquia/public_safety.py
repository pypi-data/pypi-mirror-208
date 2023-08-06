""""Get Video Download Request"""

from ubicquia.base import Endpoint


class PublicSafety(Endpoint):
    """Related to Cameras"""

    def __init__(self, *args, **kwargs):
        """Adding URL"""
        super().__init__(*args, **kwargs)
        self.url = self.base_url_v2 + '/publicsafety'

    def video_downloads(self,
                        sort_by: str = 'id',
                        sort_dir: str = 'DESC',
                        edge_id: str = 'id',
                        q: str = '',
                        **pagination) -> dict:
        """Get Video Download Request

        Args:
            sort_by: order by
            sort_dir: direction of sort
            edge_id: offical documentation does not exist
            q: offical documentation does not exist
            **pagination: pagination parameters

        Returns:
            data response.
        Raises:
            HTTPError:
        """
        url = self.url + '/videoDownloads'
        data = {
            'sort_by': sort_by,
            'sort_dir': sort_dir,
            'edge_id': edge_id,
            "filter": [
                {
                    "attribute": "",
                    "operator": "",
                    "value": ""
                }
            ],
            'q': q,
            **self.pagination(**pagination),
        }
        d = self.session.req('post', url, json=data)
        return d

    def update_video_download_request(self, id: str,
                                      status: str = 'cancelled') -> dict:
        """Update video download

        Args:
            id: item id
            status: offical documentation does not exist

        Returns:
            data response.

        Raises:
            HTTPError:
        """
        url = self.url + f'/updateVideoDownloadRequest/{id}'
        data = {'status': status}
        d = self.session.req('put', url, json=data)
        return d

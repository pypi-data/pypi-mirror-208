from urllib.parse import urljoin

import requests


class RequestHelper(requests.Session):
    def __init__(self, base_url: str, request_id: str = None):
        super().__init__()
        self.base_url = base_url
        self.headers['request-id'] = request_id

    def request(self, method, url, *args, **kwargs):
        joined_url = urljoin(self.base_url, url)
        return super().request(method, joined_url, *args, **kwargs)

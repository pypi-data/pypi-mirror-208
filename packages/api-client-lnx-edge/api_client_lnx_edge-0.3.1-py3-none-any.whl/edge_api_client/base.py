import requests
from urllib.parse import urljoin


class BaseAPIClient(object):
    base_url = ''

    def __init__(self):
        self.session = requests.Session()

    def get_entity(self, entity_type, entity_id=None, append_url=True, **kwargs):
        endpoint = 'api/{}/{}'.format(entity_type, entity_id if entity_id else '')
        return self._get(endpoint, append_url=append_url, **kwargs)

    def _get(self, endpoint='', append_url=True, **kwargs):
        return self._request('get', endpoint, append_url=append_url, **kwargs)

    def _post(self, endpoint='', append_url=True, **kwargs):
        return self._request('post', endpoint, append_url=append_url, **kwargs)

    def _request(self, method, endpoint, params=None, data=None, append_url=True, **kwargs):
        url = self._build_url(endpoint) if append_url else self.base_url
        params = params or {}
        data = data or {}

        response = self.session.request(method, url, params=params, data=data, **kwargs)

        return response

    def _build_url(self, endpoint):
        return urljoin(self.base_url, endpoint) if endpoint else self.base_url

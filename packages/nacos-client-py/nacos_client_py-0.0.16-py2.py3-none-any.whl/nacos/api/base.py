class BaseNacosAPI:
    """Nacos API base class"""

    def __init__(self, client=None):
        self._client = client

    def _get(self, url, **kwargs):
        return self._client._do_request('GET', url, **kwargs)

    def _post(self, url, **kwargs):
        return self._client._do_request('POST', url, **kwargs)

    def _put(self, url, **kwargs):
        return self._client._do_request('PUT', url, **kwargs)

    def _delete(self, url, **kwargs):
        return self._client._do_request('DELETE', url, **kwargs)

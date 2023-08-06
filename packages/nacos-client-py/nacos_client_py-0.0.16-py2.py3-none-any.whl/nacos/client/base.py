import inspect
import time

import httpx

from nacos.api.base import BaseNacosAPI
from nacos.api.models import AccessToken
from nacos.errors import _default_response_to_exception


class BaseNacosClient:

    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls)
        api_endpoints = inspect.getmembers(self, lambda x: isinstance(x, BaseNacosAPI))
        for name, api in api_endpoints:
            api_cls = type(api)
            api = api_cls(self)
            setattr(self, name, api)
        return self

    def __init__(self,
                 server_addresses: str,
                 username: str,
                 password: str,
                 namespace_id: str = None):
        self.server_addresses = server_addresses
        self.username = username
        self.password = password
        self.namespace_id = namespace_id

        self.access_token = None
        self.access_token_timestamp = None
        self.access_token_ttl = None

        self.request = httpx.Client(
            base_url=self.server_addresses,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            event_hooks={
                "response": [_default_response_to_exception],
            },
            timeout=10
        )

        self._fetch_access_token()

    def _fetch_access_token(self):
        """ Fetches the access token """
        now = int(time.time())
        if self.access_token is None or self.access_token_timestamp + self.access_token_ttl * 0.9 < now:
            res = self.request.post('/nacos/v1/auth/login',
                                    data={'username': self.username, 'password': self.password})
            data = AccessToken.parse_raw(res.content)

            self.access_token = data.accessToken
            self.access_token_timestamp = now
            self.access_token_ttl = data.tokenTtl

        return self.access_token

    def _do_request(self, method, url, **kwargs):
        access_token = self._fetch_access_token()
        return self.request.request(method, f'{url}?accessToken={access_token}', **kwargs)

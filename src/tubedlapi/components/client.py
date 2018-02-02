# -*- coding: utf-8 -*-

import requests
from apistar import http

from tubedlapi.app import get_app


class AppClient(requests.Session):

    def __init__(self, host: str, port: int, scheme: str = 'http') -> None:

        self.headers.update({'User-Agent': 'AppClient'})
        self.scheme = scheme
        self.host = host
        self.port = port

    def __repr__(self) -> str:

        return '<AppClient{{scheme}://{host}:{port}/}>'.format(
            scheme=self.scheme,
            host=self.host,
            port=self.port,
        )

    def __str__(self) -> str:

        return self.__repr__()

    def request(self, method: str, url: str, **kwargs) -> requests.Response:

        if not url.startswith('http:') and not url.startswith('https:'):
            if not url.startswith('/'):
                raise ValueError(
                    'AppClient expected either absolute URL starting with '
                    'http: or https:, or a relative URL starting with /'
                )
            else:
                url = '{scheme}://{host}:{port}{url}'.format(
                    scheme=self.scheme,
                    host=self.host,
                    port=self.port,
                    url=url,
                )

        return super().request(method, url, **kwargs)


def make_app_client(scheme: http.Scheme, host: http.Host, port: http.Port) -> AppClient:

    return AppClient(host, port, scheme=scheme)

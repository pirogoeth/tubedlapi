# -*- coding: utf-8 -*-

from flask import Response


def cors_headers(resp: Response) -> Response:
    ''' Adds very permissive CORS headers to all responses.
    '''

    cors = 'Access-Control-Allow'

    resp.headers.add(f'{cors}-Origin', '*')
    resp.headers.add(f'{cors}-Credentials', 'true')
    resp.headers.add(f'{cors}-Headers', 'Content-Type')
    resp.headers.add(f'{cors}-Methods', 'GET, POST, PUT, OPTIONS, DELETE')

    return resp

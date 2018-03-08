# -*- coding: utf-8 -*-

import flask
from flask import request

from flasgger import LazyString, Swagger

from tubedlapi.components.settings import Settings


def init_flasgger(app: flask.Flask, settings: Settings) -> None:

    # Disable `flasgger` if settings.SWAGGER is not true
    if not settings.SWAGGER:
        return None

    app.config['SWAGGER'] = {
        'title': 'tubedlapi',
        'uiversion': 3,
    }

    template: dict = {
        # 'swaggerUiPrefix': LazyString(
        #    lambda: request.environ.get('HTTP_X_SCRIPT_NAME', ''),
        # ),
    }

    return Swagger(app, template=template)


component = {
    'cls': Swagger,
    'init': init_flasgger,
    'persist': True,
}

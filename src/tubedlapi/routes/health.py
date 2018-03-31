# -*- coding: utf-8 -*-

import logging

from flask import (
    Blueprint,
)
from flask.json import jsonify

log = logging.getLogger(__name__)
blueprint = Blueprint(
    'health',
    __name__,
    url_prefix='/health',
)


@blueprint.route('/')
def health_ok() -> str:

    return jsonify({'status': 'ok'})

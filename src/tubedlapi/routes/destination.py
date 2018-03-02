# -*- coding: utf-8 -*-

import logging
from http import HTTPStatus as status
from urllib.parse import unquote_plus

from flask import (
    Blueprint,
    Response,
    json,
    request,
)
from flask.json import jsonify

blueprint = Blueprint(
    'destination',
    __name__,
    url_prefix='/destination',
)
log = logging.getLogger(__name__)


@blueprint.route('/', methods=['GET'])
def list_destinations() -> Response:

    return jsonify([])

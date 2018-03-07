# -*- coding: utf-8 -*-

import logging
from http import HTTPStatus as status
from urllib.parse import unquote_plus

import peewee
from flask import (
    Blueprint,
    Response,
    request,
)
from flask.json import jsonify

from tubedlapi.model.destination import Destination

blueprint = Blueprint(
    'destination',
    __name__,
    url_prefix='/destinations',
)
log = logging.getLogger(__name__)


@blueprint.route('/', methods=['GET'])
def list_destinations() -> Response:
    ''' GET /destinations/

        Returns a JSON list of all destinations with secrets sanitized
        out of the `config` property.
    '''

    return jsonify([d.to_dict() for d in Destination.select()])


@blueprint.route('/', methods=['POST'])
def create_destination() -> Response:
    ''' POST /destinations/

        Create a new download destination.
        Expects a JSON payload similar to the following:

            {
                "name": "destination_name",
                "config": {
                    "url": "osfs:///var/lib/music",
                }
            }

        Returns a dictionary representing the created destination.
    '''

    payload = request.get_json()
    name = payload.get('name')
    if not name:
        return jsonify({
            'message': 'name required but not provided',
        }), status.BAD_REQUEST

    url = payload.get('url')
    if not url:
        return jsonify({
            'message': 'url required but not provided',
        }), status.BAD_REQUEST

    dest = Destination(**payload)
    try:
        dest.save()
        return jsonify({
            'message': 'success',
            'destination': dest.to_dict(),
        })
    except peewee.IntegrityError:
        return jsonify({
            'message': 'name already exists',
        }), status.CONFLICT


@blueprint.route('/<string:name>', methods=['DELETE'])
def delete_destination(name) -> Response:
    ''' DELETE /destination/:name

        Removes a download destination.

        Returns the result and the details of the removed destination.
    '''

    name = unquote_plus(name)

    try:
        res = Destination.get(name=name)
        last_state = res.to_dict()
        res.delete_instance()

        return jsonify({
            'message': 'deleted',
            'profile': last_state,
        })
    except Destination.DoesNotExist:
        return jsonify({
            'message': 'not found',
            'query': {
                'name': name,
            },
        }), status.NOT_FOUND

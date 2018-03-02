# -*- coding: utf-8 -*-

import logging
from http import HTTPStatus as status
from urllib.parse import unquote_plus

import peewee
from flask import (
    Blueprint,
    Response,
    json,
    request,
)
from flask.json import jsonify

from tubedlapi.model.profile import Profile

blueprint = Blueprint(
    'profile',
    __name__,
    url_prefix='/profiles',
)
log = logging.getLogger(__name__)


@blueprint.route('/', methods=['GET'])
def list_profiles() -> Response:

    return jsonify([p.to_dict() for p in Profile.select()])


@blueprint.route('/<string:name>', methods=['GET'])
def show_profile(name: str) -> Response:

    name = unquote_plus(name)

    try:
        return jsonify(Profile.get(name=name).to_dict())
    except Profile.DoesNotExist:
        return jsonify({
            'message': 'not found',
            'query': {
                'name': name,
            },
        }), status.NOT_FOUND


@blueprint.route('/', methods=['POST'])
def create_profile() -> Response:

    payload = request.get_json()
    options = payload.get('options', {})

    if isinstance(options, dict):
        payload.update({
            'options': bytes(json.dumps(options), 'utf-8'),
        })

    # TODO: Do not allow overwriting of profiles
    new_profile = Profile(**payload)
    try:
        new_profile.save()
        return jsonify({
            'message': 'success',
            'profile': new_profile.to_dict(),
        })
    except peewee.IntegrityError:
        return jsonify({
            'message': 'name already in use',
        }), status.CONFLICT


@blueprint.route('/<string:name>', methods=['DELETE'])
def delete_profile(name: str) -> dict:

    name = unquote_plus(name)

    try:
        res = Profile.get(name=name)
        last_state = res.to_dict()
        res.delete_instance()
        return jsonify({
            'message': 'deleted',
            'profile': last_state,
        })
    except Profile.DoesNotExist:
        return jsonify({
            'message': 'not found',
            'query': {
                'name': name,
            },
        }), status.NOT_FOUND

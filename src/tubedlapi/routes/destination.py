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
        ---
        tags:
          - Destinations
        parameters: []
        definitions:
          Destination:
            type: object
            required:
              - id
              - name
              - url
            properties:
              id:
                type: integer
                readOnly: true
              name:
                type: string
              url:
                type: string
        responses:
          200:
            description: a list of destinations
            schema:
              type: array
              items:
                $ref: "#/definitions/Destination"
            examples:
              [
                  {
                      "id": 1,
                      "name": "local",
                      "url": "osfs:///var/lib/music"
                  }
              ]
    '''

    return jsonify([d.to_dict() for d in Destination.select()])


@blueprint.route('/', methods=['POST'])
def create_destination() -> Response:
    ''' POST /destinations/

        Create a new download destination.

        Returns a dictionary representing the created destination.
        ---
        tags:
          - Destinations
        consumes:
          - application/json
        produces:
          - application/json
        parameters:
          - name: destination
            in: body
            description: Destination to create
            required: true
            schema:
              $ref: "#/definitions/Destination"
        responses:
          200:
            description: Created destination
            schema:
              properties:
                message:
                  type: string
                destination:
                  $ref: "#/definitions/Destination"
            examples:
              {
                  "message": "created",
                  "destination": {
                    "id": 1,
                    "name": "local",
                    "url": "osfs:///var/lib/music"
                  }
              }
          400:
            description: Required parameters not provided
            schema:
              properties:
                message:
                  type: string
          409:
            description: Destination could not be created
            schema:
              properties:
                message:
                  type: string
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
            'message': 'created',
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
        ---
        tags:
          - Destinations
        parameters:
          - name: name
            in: path
            required: true
            type: string
            description: Name of the destination to remove
        responses:
          200:
            description: Deleted destination
            schema:
              properties:
                message:
                  type: string
                destination:
                  $ref: "#/definitions/Destination"
            examples:
              {
                  "message": "deleted",
                  "destination": {
                    "id": 1,
                    "name": "local",
                    "url": "osfs:///var/lib/music"
                  }
              }
          404:
            description: No destination matching name
            schema:
              properties:
                message:
                  type: string
                query:
                  type: object
                  properties:
                    name:
                      type: string
            examples:
              {
                  "message": "not found",
                  "query": {
                      "name": "local"
                  }
              }

    '''

    name = unquote_plus(name)

    try:
        res = Destination.get(name=name)
        last_state = res.to_dict()
        res.delete_instance()

        return jsonify({
            'message': 'deleted',
            'destination': last_state,
        })
    except Destination.DoesNotExist:
        return jsonify({
            'message': 'not found',
            'query': {
                'name': name,
            },
        }), status.NOT_FOUND

# -*- coding: utf-8 -*-

import logging
from http import HTTPStatus as status
from urllib.parse import unquote_plus

import peewee
from flask import Blueprint, Response, json, request
from flask.json import jsonify

from tubedlapi.model.profile import Profile

blueprint = Blueprint("profile", __name__, url_prefix="/profiles")
log = logging.getLogger(__name__)


@blueprint.route("/", methods=["GET"])
def list_profiles() -> Response:
    """ List all download profiles stored in the database

        A download profile also stores the way downloaded media should
        be encoded or modified. A profile typically contains a set of options
        that should be passed to [`youtube-dl`](https://github.com/rg3/youtube-dl)
        to modify the download or post-processing step(s).

        ---
        import: "../specs/definitions.yaml"
        tags:
          - Profile
        responses:
          200:
            description: a list of profiles
            schema:
              type: array
              items:
                $ref: "#/definitions/Profile"
            examples:
              [
                  {
                      "id": 1,
                      "name": default,
                      "options": {
                          "format": "bestaudio/best",
                          "postprocessors": [
                              {
                                  "key": "FFmpegExtractAudio",
                                  "preferredcodec": "mp3",
                                  "preferredquality": "192"
                              }
                          ]
                      }
                  }
              ]
    """

    return jsonify([p.to_dict() for p in Profile.select()])


@blueprint.route("/<string:name>", methods=["GET"])
def show_profile(name: str) -> Response:
    """ Display the download profile with the given `name`

        A download profile also stores the way downloaded media should
        be encoded or modified. A profile typically contains a set of options
        that should be passed to [`youtube-dl`](https://github.com/rg3/youtube-dl)
        to modify the download or post-processing step(s).

        ---
        import: "../specs/definitions.yaml"
        tags:
          - Profile
        parameters:
          - name: name
            in: path
            required: true
            type: string
            description: Name of the profile to show
        responses:
          200:
            description: Profile
            schema:
              $ref: "#/definitions/Profile"
            examples:
              [
                  {
                      "id": 1,
                      "name": default,
                      "options": {
                          "format": "bestaudio/best",
                          "postprocessors": [
                              {
                                  "key": "FFmpegExtractAudio",
                                  "preferredcodec": "mp3",
                                  "preferredquality": "192"
                              }
                          ]
                      }
                  }
              ]
          404:
            description: Profile could not be found
            schema:
              $ref: "#/definitions/QueryNotFound"
    """

    name = unquote_plus(name)

    try:
        return jsonify(Profile.get(name=name).to_dict())
    except Profile.DoesNotExist:
        return (
            jsonify({"message": "not found", "query": {"name": name}}),
            status.NOT_FOUND,
        )


@blueprint.route("/", methods=["POST"])
def create_profile() -> Response:
    """ Create a new download profile

        ---
        import: "../specs/definitions.yaml"
        tags:
          - Profile
        parameters:
          - name: profile
            in: body
            description: Profile to create
            required: true
            schema:
                $ref: "#/definitions/Profile"
        responses:
          200:
            description: Created profile
            schema:
              $ref: "#/definitions/Profile"
            examples:
              [
                  {
                      "id": 1,
                      "name": default,
                      "options": {
                          "format": "bestaudio/best",
                          "postprocessors": [
                              {
                                  "key": "FFmpegExtractAudio",
                                  "preferredcodec": "mp3",
                                  "preferredquality": "192"
                              }
                          ]
                      }
                  }
              ]
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
    """

    payload = request.get_json()
    options = payload.get("options", {})

    if isinstance(options, dict):
        payload.update({"options": bytes(json.dumps(options), "utf-8")})

    # TODO: Do not allow overwriting of profiles
    new_profile = Profile(**payload)
    try:
        new_profile.save()

        return jsonify({"message": "success", "profile": new_profile.to_dict()})
    except peewee.IntegrityError:
        return jsonify({"message": "name already in use"}), status.CONFLICT


@blueprint.route("/<string:name>", methods=["DELETE"])
def delete_profile(name: str) -> Response:
    """ Delete a download profile

        ---
        import: "../specs/definitions.yaml"
        tags:
          - Profile
        parameters:
          - name: name
            in: path
            required: true
            type: string
            description: Name of the profile to remove
        responses:
          200:
            description: Deleted profile
            schema:
              properties:
                message:
                  type: string
                destination:
                  $ref: "#/definitions/Profile"
            examples:
              {
                  "message": "deleted",
                  "profile": {
                      "id": 1,
                      "name": "test",
                      "options": {
                          "format": "bestaudio/best"
                      }
                  }
              }
          404:
            description: No profile matching name
            schema:
              $ref: "#/definitions/QueryNotFound"
            examples:
              {
                  "message": "not found",
                  "query": {
                      "name": "local"
                  }
              }
    """

    name = unquote_plus(name)

    try:
        res = Profile.get(name=name)
        last_state = res.to_dict()
        res.delete_instance()

        return jsonify({"message": "deleted", "profile": last_state})
    except Profile.DoesNotExist:
        return (
            jsonify({"message": "not found", "query": {"name": name}}),
            status.NOT_FOUND,
        )

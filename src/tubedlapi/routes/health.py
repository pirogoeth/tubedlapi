# -*- coding: utf-8 -*-

import logging

from flask import Blueprint
from flask.json import jsonify

log = logging.getLogger(__name__)
blueprint = Blueprint("health", __name__, url_prefix="/health")


@blueprint.route("/")
def health_ok() -> str:
    """ Returns a simple status message for use as a health check in monitoring software
        ---
        tags:
          - Health
        produces:
          - application/json
        responses:
          200:
            description: Healthy endpoint
            schema:
              properties:
                status:
                  type: string
            examples:
              {
                  "status": "ok"
              }
    """

    return jsonify({"status": "ok"})

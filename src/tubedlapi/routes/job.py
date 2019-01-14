# -*- coding: utf-8 -*-

import logging
from http import HTTPStatus as status

from flask import Blueprint, json, request
from flask.json import jsonify

from tubedlapi.exec import stage
from tubedlapi.model.job import Job
from tubedlapi.model.profile import Profile

log = logging.getLogger(__name__)
blueprint = Blueprint("job", __name__, url_prefix="/jobs")


@blueprint.route("/", methods=["GET"])
def list_jobs():
    """ Lists all jobs

        ---
        import: "../specs/definitions.yaml"
        tags:
          - Job
        produces:
          - application/json
        responses:
          200:
            description: a list of jobs
            schema:
              type: array
              items:
                $ref: "#/definitions/Job"
    """

    return jsonify([j.to_dict() for j in Job.select()])


@blueprint.route("/", methods=["POST"])
def create_job():
    """ Creates a new job from a JSON payload

        ---
        import: "../specs/definitions.yaml"
        tags:
          - Job
        consumes:
          - application/json
        produces:
          - application/json
        parameters:
          - name: job
            in: body
            description: Job to create
            required: true
            schema:
              $ref: "#/definitions/JobMeta"
        responses:
          200:
            description: newly created job
            schema:
              $ref: "#/definitions/Job"
            examples:
              {
                "created_at": "Fri, 01 Jun 2018 23:58:13 GMT",
                "id": "0e5c5924-ff94-4e01-970e-3c6acf57c296",
                "meta": {
                  "destinations": [
                    "default"
                  ],
                  "profile": "video",
                  "url": "https://www.youtube.com/watch?v=oxoqm05c7yA"
                },
                "status": "queued"
              }
          400:
            description: job payload is malformed
            schema:
              type: object
              properties:
                request:
                  type: object
                  properties:
                    body:
                      type: object
                      description: request body that was sent
            examples:
              {
                "message": "body must contain `url` and `profile`",
                "request": {
                  "body": {
                    "destinations": [
                      "default"
                    ]
                  }
                }
              }
          404:
            description: destination(s) or profile do not exist
            schema:
              $ref: "#/definitions/QueryNotFound"
            examples:
              {
                "message": "profile not found",
                "query": {
                  "profile": "invalid"
                }
              }
    """

    payload = request.get_json()
    url = payload.get("url")
    profile = payload.get("profile")

    if not url or not profile:
        return (
            jsonify(
                {
                    "message": "body must contain `url` and `profile`",
                    "request": {"body": payload},
                }
            ),
            status.BAD_REQUEST,
        )

    try:
        profile = Profile.get(name=profile)
    except Profile.DoesNotExist:
        return (
            jsonify({"message": "profile not found", "query": {"profile": profile}}),
            status.NOT_FOUND,
        )

    # TODO: Do validation of `destinations` list
    # TODO: Make sure each destination is included only once (collapse mult)

    job_record = Job.create(status="queued", meta=json.dumps(payload))

    stage.job_begin_fetch(job_record, profile)

    return jsonify(job_record.to_dict())


@blueprint.route("/<uuid:job_id>")
def show_job(job_id: str):
    """ Get a job by ID

        ---
        import: "../specs/definitions.yaml"
        tags:
          - Job
        produces:
          - application/json
        parameters:
          - name: job_id
            in: path
            required: true
            type: string
            description: ID of the job to show
        responses:
          200:
            description: Job
            schema:
              $ref: "#/definitions/Job"
            examples:
              {
                "created_at": "Sun, 11 Mar 2018 23:41:07 GMT",
                "id": "dfb95f67-1f4c-4592-8c56-33af76d4ed5a",
                "meta": {
                  "destinations": [
                    "local"
                  ],
                  "extractor": {
                    "_elapsed_str": "00:00",
                    "_total_bytes_str": "4.83MiB",
                    "downloaded_bytes": 5062877,
                    "elapsed": 0.7492239475250244,
                    "filename": "dfb95f67-1f4c-4592-8c56-33af76d4ed5a.251 - audio only (DASH audio)",
                    "status": "finished",
                    "total_bytes": 5062877
                  },
                  "info": {
                    "codecs": {
                      "audio": "opus",
                      "video": "none"
                    },
                    "downloaded": {
                      "filename": "dfb95f67-1f4c-4592-8c56-33af76d4ed5a.mp3",
                      "filesize_bytes": 5062877
                    },
                    "source": {
                      "description": "... SNIP ...",
                      "duration": 269,
                      "original_url": "https://www.youtube.com/watch?v=VozMw_v1vxg",
                      "tags": [
                        "Ekcle",
                        "Sakoya",
                        "Deshoda",
                        "EP",
                        "Inspected",
                        "INSP031",
                        "Inspector",
                        "Dubplate"
                      ],
                      "thumbnails": [
                        "https://i.ytimg.com/vi/VozMw_v1vxg/maxresdefault.jpg"
                      ],
                      "title": "Sakoya"
                    },
                    "uploader": {
                      "id": "InspectorDubplate",
                      "url": "http://www.youtube.com/user/InspectorDubplate"
                    }
                  },
                  "profile": "music-meta",
                  "result": {
                    "local": {
                      "result": {
                        "success": true
                      }
                    }
                  },
                  "url": "https://www.youtube.com/watch?v=VozMw_v1vxg"
                },
                "status": "completed"
              }
          404:
            description: job with ID not found
            schema:
              $ref: "#/definitions/QueryNotFound"
            examples:
              {
                "message": "job not found",
                "query": {
                  "job": "dfb95f67-1f4c-4592-8c56-33af76d4eaae"
                }
              }
    """

    try:
        return jsonify(Job.get(id=job_id).to_dict())
    except Job.DoesNotExist:
        return (
            jsonify({"message": "job not found", "query": {"job": job_id}}),
            status.NOT_FOUND,
        )

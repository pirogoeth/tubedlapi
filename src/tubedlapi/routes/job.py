# -*- coding: utf-8 -*-

import logging
from http import HTTPStatus as status

from flask import (
    Blueprint,
    json,
    request,
)
from flask.json import jsonify

from tubedlapi.exec import stage
from tubedlapi.model.job import Job
from tubedlapi.model.profile import Profile

log = logging.getLogger(__name__)
blueprint = Blueprint(
    'job',
    __name__,
    url_prefix='/jobs',
)


@blueprint.route('/', methods=['POST'])
def create_job():
    ''' POST /job/

        Creates a new job from a JSON payload.
    '''

    payload = request.get_json()
    url = payload.get('url')
    profile = payload.get('profile')

    if not url or not profile:
        return jsonify({
            'message': 'body must contain `url` and `profile`',
            'request': {
                'body': payload,
            },
        }), status.BAD_REQUEST

    try:
        profile = Profile.get(name=profile)
    except Profile.DoesNotExist:
        return jsonify({
            'message': 'profile not found',
            'query': {
                'profile': profile,
            },
        }), status.NOT_FOUND

    # TODO: Do validation of `destinations` list
    # TODO: Make sure each destination is included only once (collapse mult)

    job_record = Job.create(
        status='queued',
        meta=json.dumps(payload),
    )

    stage.job_begin_fetch(job_record, profile)

    return jsonify(job_record.to_dict())


@blueprint.route('/<uuid:job_id>')
def show_job(job_id: str):

    return jsonify(Job.get(id=job_id).to_dict())

# -*- coding: utf-8 -*-

import asyncio
import logging
from functools import partial
from http import HTTPStatus as status
from urllib.parse import unquote_plus

from flask import (
    Blueprint,
    json,
    request,
)
from flask.json import jsonify

from tubedlapi.app import inject
from tubedlapi.exec import youtubedl
from tubedlapi.model.job import Job
from tubedlapi.model.profile import Profile
from tubedlapi.util.async import JobExecutor

log = logging.getLogger(__name__)
blueprint = Blueprint(
    'job',
    __name__,
    url_prefix='/jobs',
)


@blueprint.route('/', methods=['POST'])
@inject
def create_job(executor: JobExecutor):

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

    # TODO: Make a new job record to use with the fetcher
    job_record = Job.create(
        status='queued',
        meta=json.dumps(payload),
    )

    # Create a partial of the fetcher job instead of beginning exec
    future: asyncio.Future = executor.execute_future(
        youtubedl.fetch_url,
        job_record,
        profile,
    )
    future.add_done_callback(
        partial(
            _create_job_callback,
            job_record,
        ),
    )

    return job_record.to_json()


def _create_job_callback(job: Job, fut: asyncio.Future):

    exc = fut.exception()
    if not fut.cancelled() and exc:
        raise exc

    if fut.done():
        job.meta_update(result=fut.result())
        job.save()


@blueprint.route('/<uuid:job_id>')
def show_job(job_id: str):

    return Job.get(id=job_id).to_json()


@blueprint.route('/<uuid:job_id>', methods=['PUT'])
def update_job(job_id: str):

    # TODO: Get new stats from update payload
    job_status = None

    job = Job.get(id=id)
    if job.status != job_status:
        job.status = job_status
        job.save()

    return job.to_json()

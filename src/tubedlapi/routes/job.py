# -*- coding: utf-8 -*-

import asyncio
import functools
import logging
import typing
from http import HTTPStatus as status
from urllib.parse import unquote_plus

from apistar import Response, Route, get_current_app, http, typesystem
from apistar.backends.sqlalchemy_backend import Session
from tubedlapi.app import get_app
from tubedlapi.exec import youtubedl
from tubedlapi.model import binding
from tubedlapi.model.job import (
    Job,
    JobId,
    JobMetadata,
    JobObject,
    JobStatus,
)
from tubedlapi.model.profile import (
    Profile,
    ProfileObject,
)
from tubedlapi.util.async import JobExecutor

log = logging.getLogger(__name__)


def create_job(session: Session, executor: JobExecutor, meta: JobMetadata) -> JobObject:

    profile = None

    with binding(session):
        profile_name = meta['profile']
        result = Profile.find(name=profile_name).all()
        if len(result) >= 1:
            profile = ProfileObject.from_model(result[0])

    # Make a new job record to use with the fetcher
    job_record = Job.new()
    job_record.meta = meta.to_json()
    job_record.status = 'queued'
    session.add(job_record)
    session.flush()

    job_object = JobObject.from_model(job_record)

    # Create a partial of the fetcher job instead of beginning exec
    future: asyncio.Future = executor.execute_future(
        youtubedl.fetch_url,
        job_object,
        profile,
    )
    future.add_done_callback(_create_job_callback)

    return job_object


def _create_job_callback(fut: asyncio.Future):

    get_app().console.echo('Future done callback')

    exc = fut.exception()
    if not fut.cancelled() and exc:
        get_app().console.echo('Future raised an error, raising..')
        raise exc


def show_job(session: Session, id: JobId) -> JobObject:

    with binding(session):
        job = Job.find(id=id).first()
        return JobObject.from_model(job)


def update_job(session: Session, id: JobId, job_status: JobStatus) -> JobObject:

    with binding(session):
        job = Job.find(id=id).first()
        if job.status != job_status:
            job.status = job_status

        return JobObject.from_model(job)


routes = [
    Route('/', 'POST', create_job),
    Route('/{id}', 'GET', show_job),
    Route('/{id}', 'PUT', update_job),
]

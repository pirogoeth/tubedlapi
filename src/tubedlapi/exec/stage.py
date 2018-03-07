# -*- coding: utf-8 -*-

import logging
from concurrent.futures import Future
from functools import partial

from tubedlapi.app import inject
from tubedlapi.exec.uploader import upload_file
from tubedlapi.exec.youtubedl import fetch_url
from tubedlapi.model.job import Job
from tubedlapi.model.profile import Profile
from tubedlapi.util.async import JobExecutor

log = logging.getLogger(__name__)

STAGE_FETCHING = 'fetching'
STAGE_UPLOADING = 'uploading'


@inject
def job_begin_fetch(executor: JobExecutor, job: Job, profile: Profile) -> Future:
    ''' Kickstarts the fetcher job. Returns the future
        that will contain the result of the fetch.

        Automatically adds `job_stage_callback` as a done callback,
        which will use job metadata to determine the next steps.
    '''

    fut: Future = executor.execute_future(
        fetch_url,
        job,
        profile,
    )
    fut.add_done_callback(
        partial(
            job_stage_callback,
            job,
            STAGE_FETCHING,
        ),
    )

    return fut


@inject
def job_begin_upload(executor: JobExecutor, job: Job) -> Future:
    ''' Begins execution of a future whih spawns another future
        each destination upload. The number of futures that will be
        spawned/running is limited by the default size of the `ThreadPoolExecutor`.
    '''

    # Update the job status to notify that the file is uploading
    job.status = 'uploading'
    job.save()

    fut: Future = executor.execute_future(
        upload_file,
        job,
    )
    fut.add_done_callback(
        partial(
            job_stage_callback,
            job,
            STAGE_UPLOADING,
        ),
    )

    return fut


def job_stage_callback(job: Job, stage: str, fut: Future) -> None:
    ''' Generic job stage completion callback.
        Accepts a Job model, stage name, and the future.

        When this is called, it means the job stage has completed
        in some form or fashion. Should use `fut`'s result methods
        to figure out what happened and update accordingly.
    '''

    # First, update job metadata with the execution result.
    exc = fut.exception()
    if not fut.cancelled() and exc:
        raise exc

    if fut.done():
        job.meta_update(result=fut.result())
        job.save()

    # Dispatch the next futures chain, if applicable
    if stage == STAGE_FETCHING:
        # Check if the job has any destinations and trigger the
        # destinations executor
        if 'destinations' in job.meta_dict:
            # Spawn the uploader future
            # TODO: Add a marker in the job meta showing
            # that destination uploads are queued
            job_begin_upload(job)
    elif stage == STAGE_UPLOADING:
        job.status = 'completed'
        job.save()

        log.info(f'job {job.id} has finished job pipeline')

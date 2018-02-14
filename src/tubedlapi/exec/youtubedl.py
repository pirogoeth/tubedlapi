# -*- coding: utf-8 -*-

import functools
import logging
import typing

import youtube_dl
from flask import json

from tubedlapi.model.job import Job
from tubedlapi.model.profile import Profile

log = logging.getLogger(__name__)


class FetchLogger(object):

    def __init__(self, job: Job, profile: Profile):

        self.job = job
        self.profile = profile

    def message(self, msg):

        # TODO: Put fetch logs into a database model.
        pass

    debug = message
    error = message
    warning = message


def fetch_url(job: Job, profile: Profile):

    options = json.loads(profile.options)
    options.update({
        'outtmpl': f'{job.id}.%(format)s',
        'logger': FetchLogger(job, profile),
        'progress_hooks': [
            functools.partial(_progress_hook, job)
        ],
    })

    return _fetch(job.meta_dict['url'], options)


def _fetch(url: str, options: dict):

    with youtube_dl.YoutubeDL(options) as dl:
        return dl.download([url])


def _progress_hook(job: Job, info: dict):

    if job.status != info['status']:
        log.info(
            'Job transitioning from {old_state} to {new_state}'.format(
                old_state=job.status,
                new_state=info['status'],
            )
        )

        job.status = info['status']
        job.meta_update(info=info)
        job.save()

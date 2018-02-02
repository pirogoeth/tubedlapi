# -*- coding: utf-8 -*-

import functools
import typing

import youtube_dl

from tubedlapi.app import get_app
from tubedlapi.components.client import AppClient
from tubedlapi.model import binding_new_session
from tubedlapi.model.job import (
    JobMetadata,
    JobObject,
)
from tubedlapi.model.profile import (
    ProfileObject,
    ProfileOptions,
)


def fetch_url(job: JobObject, profile: ProfileObject):

    options = profile['options']
    options.update({
        'logger': None,
        'progress_hooks': [
            functools.partial(_progress_hook, job)
        ],
    })

    return _fetch(job['meta']['url'], options)


def _fetch(url: str, options: ProfileOptions):

    with youtube_dl.YoutubeDL(options) as dl:
        return dl.download([url])


def _progress_hook(job: JobObject, info: dict):

    client = get_app().preloaded_state[AppClient]
    get_app().console.echo('AppClient: %s' % (client))
    client.post(
        '/jobs/{id}',
        data={
            'status': info['status'],
        },
    )

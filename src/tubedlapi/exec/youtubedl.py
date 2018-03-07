# -*- coding: utf-8 -*-

import functools
import logging
from typing import Any

import youtube_dl
from flask import json
from youtube_dl.postprocessor.common import PostProcessor

from tubedlapi.model.job import Job
from tubedlapi.model.profile import Profile

log = logging.getLogger(__name__)


class FetchLogger(object):

    def __init__(self, job: Job, profile: Profile) -> None:

        self.job = job
        self.profile = profile

    def message(self, msg):

        # TODO: Put fetch logs into a database model.
        pass

    debug = message
    error = message
    warning = message


class JobPostProcessor(PostProcessor):
    ''' Youtube-DL post-processor for getting
        the final filename from the end of the
        post-processor chain.
    '''

    def __init__(self, job: Job) -> None:

        self._job = job

    def filter_info(self, info: dict) -> dict:

        return {
            'codecs': {
                'audio': info.get('acodec'),
                'video': info.get('vcodec'),
            },
            'downloaded': {
                'filename': info.get('filepath'),
                'filesize_bytes': info.get('filesize'),
            },
            'source': {
                'description': info.get('description'),
                'duration': info.get('duration'),
                'original_url': info.get('webpage_url'),
                'tags': info.get('tags'),
                'thumbnails': [t.get('url') for t in info.get('thumbnails', [])],
                'title': info.get('title'),
            },
            'uploader': {
                'id': info.get('uploader_id'),
                'url': info.get('uploader_url'),
            },
        }

    def run(self, info: dict):
        ''' Basically, a dummy implementation of run to get the final
            information dictionary from the end of the post-processor
            chain.
        '''

        log.info(
            'Job %s finished execution in post-processor chain',
            self._job.id,
        )

        info = self.filter_info(info)

        self._job.status = 'finished'
        self._job.meta_update(info=info)
        self._job.save()

        return [], self.filter_info(info)


def fetch_url(job: Job, profile: Profile) -> Any:

    options = json.loads(profile.options)
    options.update({
        'outtmpl': f'{job.id}.%(format)s',
        'logger': FetchLogger(job, profile),
        'progress_hooks': [
            functools.partial(_progress_hook, job)
        ],
    })

    job_proc = JobPostProcessor(job)

    return _fetch(job.meta_dict['url'], options, job_proc)


def _fetch(url: str, options: dict, job_proc: JobPostProcessor) -> Any:

    with youtube_dl.YoutubeDL(options) as dl:
        job_proc.set_downloader(dl)
        dl.add_post_processor(job_proc)
        return dl.download([url])


def _progress_hook(job: Job, info: dict) -> None:

    if job.status != info['status']:
        log.info(
            'Job transitioning from {old_state} to {new_state}'.format(
                old_state=job.status,
                new_state=info['status'],
            )
        )

        # status == 'finished' means download is finished -- waiting
        # for post-processor chain to complete execution.
        if info['status'] == 'finished':
            job.status = 'processing'
        else:
            job.status = info['status']

        job.meta_update(extractor=info)
        job.save()

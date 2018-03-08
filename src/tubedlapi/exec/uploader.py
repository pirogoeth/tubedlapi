# -*- coding: utf-8 -*-

import io
import logging
from concurrent import futures
from concurrent.futures import (
    wait,
    Future,
)
from typing import (
    Any,
    Dict,
    Iterator,
    List,
    Tuple,
)

from tubedlapi.app import inject
from tubedlapi.model.destination import Destination
from tubedlapi.model.job import Job
from tubedlapi.util.async import JobExecutor

log = logging.getLogger(__name__)


@inject
def upload_file(executor: JobExecutor, job: Job) -> dict:
    ''' This will actually spawn off a new future for each
        destination and wait for each to complete before
        this function will complete/return.
    '''

    local_filename = job.meta_dict.get('info', {}).get('downloaded', {}).get('filename')
    if not local_filename:
        # TODO: This is technically correct... which is also the best (read: worst)
        # kind of correct
        raise TypeError(
            'Expected a filename (str) at `job.meta.info.downloaded.filename`, got None'
        )

    log.info(
        'beginning upload for %s',
        local_filename,
    )

    dests: List[str] = []
    futs: List[Future] = []
    for dest in job.meta_dict.get('destinations', []):
        future = executor.execute_future(
            upload_to_destination,
            local_filename,
            dest,
        )

        dests.append(dest)
        futs.append(future)

    wait(futs, return_when=futures.ALL_COMPLETED)

    all_results: Dict[str, Dict] = {}
    for dest, fut in zip(dests, futs):
        result: Dict[str, Any] = {}

        exc = fut.exception()
        if not fut.cancelled() and exc:
            result.update({
                'error': str(exc),
            })

        if fut.done():
            result.update({
                'result': fut.result(),
            })

        all_results.update({
            dest: result,
        })

    return all_results


def upload_to_destination(filename: str, dest_name: str) -> dict:
    ''' Given a source filename and the name of a destination,
        load the destination record, open a connection to the
        underlying filesystem, and copy the source into the
        destination filesystem.
    '''

    log.info(
        'trying to upload file `%s` to destination %s',
        filename,
        dest_name,
    )

    # Try to find the destination model
    dest = Destination.get(name=dest_name)
    with dest.as_fs as fs:
        with io.open(filename, 'rb') as src_file:
            fs.setbinfile(filename, src_file)

    return {
        'success': True,
    }

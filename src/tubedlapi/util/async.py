# -*- coding: utf-8 -*-

import asyncio
import functools
import typing
from concurrent.futures import ThreadPoolExecutor


class JobExecutor(object):
    ''' Executor utility class supporting futures and coroutines.
        Adapted from https://gist.github.com/s0hvaperuna/48f07b8a2183fcf3f9364536f54814d5
    '''

    thread_pool: ThreadPoolExecutor = None
    loop: asyncio.AbstractEventLoop = None

    def __init__(self):

        self.thread_pool = ThreadPoolExecutor(thread_name_prefix='tubedlapi')
        self.loop = asyncio.get_event_loop()

    def execute_future(self, func: typing.Callable, *args, **kw) -> asyncio.Future:

        return self.thread_pool.submit(func, *args, **kw)

    async def execute_async(self, func: typing.Callable, *args, err: typing.Callable=None, **kw):

        func_exec = functools.partial(func, *args, **kw)

        try:
            return await self.loop.run_in_executor(self.thread_pool, func_exec)
        except Exception as e:
            if asyncio.iscoroutinefunction(err):
                asyncio.ensure_future(err, loop=self.loop)
            elif asyncio.iscoroutine(err):
                asyncio.ensure_future(err, loop=self.loop)
            elif not callable(err):
                pass
            else:
                self.loop.call_soon_threadsafe(err, e)

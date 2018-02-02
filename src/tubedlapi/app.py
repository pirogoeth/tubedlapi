# -*- coding: utf-8 -*-

import os
import pdb  # noqa

from apistar import Component, Include, Route
from apistar.backends import sqlalchemy_backend
from apistar.frameworks.asyncio import ASyncIOApp as App
from apistar.frameworks.cli import CliApp
from apistar.handlers import docs_urls, static_urls
from apistar.types import Settings

from tubedlapi.model import BaseModel
from tubedlapi.util.async import JobExecutor

__app = None


def get_app() -> App:

    global __app

    return __app


def main():

    global __app

    from tubedlapi.components.client import (
        AppClient,
        make_app_client,
    )
    from tubedlapi.routes import (
        job,
        profile,
    )

    routes = [
        Include('/docs', docs_urls),
        Include('/static', static_urls),
        Include('/profiles', profile.routes),
        Include('/jobs', job.routes),
        Route('/_debug', 'GET', pdb.set_trace),
    ]

    components = [
        Component(AppClient, init=make_app_client),
        Component(JobExecutor, init=JobExecutor),
    ]
    components.extend(sqlalchemy_backend.components)

    app = App(
        routes=routes,
        settings=Settings({
            'DATABASE': {
                'URL': 'sqlite://{}'.format(os.getenv('DB_PATH', '/app/tubedlapi.db')),
                'METADATA': BaseModel.metadata,
            },
            'DEBUG': True,
        }),
        commands=sqlalchemy_backend.commands,
        components=components,
    )
    __app = app

    app.main()

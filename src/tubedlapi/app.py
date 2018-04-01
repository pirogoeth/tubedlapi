# -*- coding: utf-8 -*-

import logging

import flask
from diecast.inject import make_injector
from diecast.registry import ComponentRegistry
from diecast.types import Injector

from tubedlapi.components import (
    crypto,
    database,
    flasgger,
    jobexec,
    sentry,
    settings as app_settings,
)
from tubedlapi.util import cors_headers

registry = ComponentRegistry()
inject: Injector = make_injector(registry)


def main() -> flask.Flask:

    from tubedlapi.routes import (
        destination,
        health,
        job,
        profile,
    )

    blueprints = [
        destination.blueprint,
        health.blueprint,
        job.blueprint,
        profile.blueprint,
    ]

    # Register initial component dependencies
    registry.add(**app_settings.component)

    # Grab the settings component for logging setup
    settings = registry[app_settings.Settings]
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format='%(levelname)-8s | %(name)12s | %(message)s',
        handlers=[
            logging.StreamHandler(),
        ],
    )

    # Initialize the remaining components
    registry.add(**crypto.component)
    registry.add(**database.component)
    registry.add(**jobexec.component)

    # Set up the application and register route blueprints
    app = flask.Flask(__name__)
    [app.register_blueprint(blueprint) for blueprint in blueprints]
    app.after_request(cors_headers)

    # Register Flask app as a component
    registry.add(
        flask.Flask,
        init=lambda: app,
        persist=True,
    )

    # Register flask extension components only after app creation!
    registry.add(**sentry.component)
    registry.add(**flasgger.component)

    return app


@inject
def run(settings: app_settings.Settings):

    app = main()
    app.run(
        debug=settings.DEBUG,
        host=settings.HOST,
        port=settings.PORT,
    )


# WSGI Entrypoint
wsgi = main()

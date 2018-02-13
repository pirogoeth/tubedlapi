# -*- coding: utf-8 -*-

import logging
from typing import Callable, Type

import flask
from diecast.inject import make_injector
from diecast.registry import get_registry, register_component

from tubedlapi.components import (
    database,
    jobexec,
    sentry,
    settings as app_settings,
)

inject: Callable[[Callable], Callable] = make_injector(get_registry())


def main():

    from tubedlapi.routes import (
        job,
        profile,
    )

    blueprints = [
        job.blueprint,
        profile.blueprint,
    ]

    # Register initial component dependencies
    register_component(**app_settings.component)
    register_component(**database.component)
    register_component(**jobexec.component)

    # Grab the settings component for logging setup
    settings = get_registry()[app_settings.Settings]['instance']
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format='%(levelname)-8s | %(name)12s | %(message)s',
        handlers=[
            logging.StreamHandler(),
        ],
    )

    # Set up the application and register route blueprints
    app = flask.Flask(__name__)
    [app.register_blueprint(blueprint) for blueprint in blueprints]

    # Register Flask app as a component
    register_component(
        flask.Flask,
        init=lambda: app,
        persist=True,
    )

    # Register the Sentry component
    register_component(**sentry.component)

    run()


@inject
def run(app: flask.Flask, settings: app_settings.Settings):

    app.run(debug=settings.DEBUG)

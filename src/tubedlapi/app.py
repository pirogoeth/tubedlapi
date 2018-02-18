# -*- coding: utf-8 -*-

import logging

import flask
from diecast.inject import make_injector
from diecast.registry import get_registry, register_component
from diecast.types import Injector

from tubedlapi.components import (
    crypto,
    database,
    jobexec,
    sentry,
    settings as app_settings,
)

inject: Injector = make_injector(get_registry())


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

    # Grab the settings component for logging setup
    settings = get_registry()[app_settings.Settings]['instance']
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format='%(levelname)-8s | %(name)12s | %(message)s',
        handlers=[
            logging.StreamHandler(),
        ],
    )

    # Initialize the remaining components
    register_component(**crypto.component)
    register_component(**database.component)
    register_component(**jobexec.component)

    # Set up the application and register route blueprints
    app = flask.Flask(__name__)
    [app.register_blueprint(blueprint) for blueprint in blueprints]

    # Register Flask app as a component
    register_component(
        flask.Flask,
        init=lambda: app,
        persist=True,
    )

    # Register the Sentry component only after app creation!
    register_component(**sentry.component)

    run()


@inject
def run(app: flask.Flask, settings: app_settings.Settings):

    app.run(debug=settings.DEBUG)

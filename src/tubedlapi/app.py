# -*- coding: utf-8 -*-

import logging

import flask
from diecast.inject import make_injector
from diecast.registry import ComponentRegistry, get_registry
from diecast.types import Injector

from tubedlapi.components import (
    crypto,
    database,
    jobexec,
    sentry,
    settings as app_settings,
)

registry = ComponentRegistry()
inject: Injector = make_injector(registry)


def main():

    from tubedlapi.routes import (
        destination,
        job,
        profile,
    )

    blueprints = [
        destination.blueprint,
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

    # Register Flask app as a component
    registry.add(
        flask.Flask,
        init=lambda: app,
        persist=True,
    )

    # Register the Sentry component only after app creation!
    registry.add(**sentry.component)

    run()


@inject
def run(app: flask.Flask, settings: app_settings.Settings):

    app.run(debug=settings.DEBUG)

# -*- coding: utf-8 -*-

import logging
import pkg_resources
import typing

from flask import Flask
try:
    from raven.contrib.flask import Sentry
    from raven.transport import Transport, default_transports
except ImportError:
    Sentry = None
    Transport = None
    default_transports = []

from tubedlapi.components import settings as app_settings

log = logging.getLogger(__name__)


def get_package_version() -> str:
    ''' Retrieves the package version from the registered egg.
    '''

    try:
        package = pkg_resources.require('tubedlapi')
        return package[0].version
    except IndexError:
        return 'source'
    except pkg_resources.DistributionNotFound:
        return 'source'


def get_transport_class(name: str) -> typing.Type[Transport]:
    ''' Given the name of a transport class, find it and
        return the class object for use with the Sentry client.
    '''

    return list(filter(
        lambda t: t.__name__ == name,
        default_transports,
    ))[0]


def init_sentry(app: Flask, settings: app_settings.Settings) -> Sentry:
    ''' Initializes the Sentry DSN for Flask, if configured.
    '''

    if not Sentry:
        log.info('`raven.contrib.flask.Sentry` could not be imported -- is it installed?')
        return None

    if settings.SENTRY_URL:
        app.config['SENTRY_CONFIG'] = {
            'release': get_package_version(),
            'environment': settings.environment,
            'transport': get_transport_class(settings.SENTRY_TRANSPORT),
        }

        return Sentry(
            app=app,
            dsn=settings.SENTRY_URL,
            logging=True,
            level=settings.SENTRY_LOG_LEVEL,
        )

    return None


component = {
    'cls': Sentry,
    'init': init_sentry,
    'persist': True,
}

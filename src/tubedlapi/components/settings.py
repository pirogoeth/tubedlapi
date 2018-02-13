# -*- coding: utf-8 -*-

import logging
import os
from typing import Type

from diecast.component import Component


class Settings(Component):

    DATABASE_URI: str = None
    DEBUG: bool = False
    LOG_LEVEL: int = logging.INFO
    SENTRY_TRANSPORT: str = 'HTTPTransport'
    SENTRY_URL: str = None

    @classmethod
    def init(cls: Type[Component]):

        this = Settings()

        # Core application settings
        this.DATABASE_URI = os.getenv('DB_URI', 'sqlite:///:memory:')
        this.DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
        this.LOG_LEVEL = logging._nameToLevel.get(
            os.getenv('LOG_LEVEL', 'INFO').upper(),
            logging.INFO,
        )

        # Sentry settings
        this.SENTRY_TRANSPORT = os.getenv('SENTRY_TRANSPORT', 'HTTPTransport')
        this.SENTRY_URL = os.getenv('SENTRY_URL', None)

        return this

    @property
    def environment(self):
        ''' Assume the environment based on the DEBUG flag.
        '''

        if self.DEBUG:
            return 'develop'
        else:
            return 'production'


component = {
    'cls': Settings,
    'init': Settings.init,
    'persist': True,
}

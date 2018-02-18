# -*- coding: utf-8 -*-

import base64
import binascii
import logging
import os
from typing import Type

from diecast.component import Component

log = logging.getLogger(__name__)


class Settings(Component):

    CRYPTO_SALT: str = None
    CRYPTO_SECRET: str = None
    CRYPTO_KDF_ITERATIONS: int = 10000
    DATABASE_URI: str = None
    DEBUG: bool = False
    LOG_LEVEL: int = logging.INFO
    SENTRY_LOG_LEVEL: int = logging.WARNING
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

        # Crypto settings
        this.CRYPTO_SECRET = os.getenv('CRYPTO_SECRET')
        this.CRYPTO_SALT = os.getenv('CRYPTO_SALT')

        try:
            this.CRYPTO_KDF_ITERATIONS = int(os.getenv('CRYPTO_KDF_ITERATIONS', '10000'))
        except ValueError:
            log.exception('env:CRYPTO_KDF_ITERATIONS is not an integer, default to 10000')
            this.CRYPTO_KDF_ITERATIONS = 10000

        # Sentry settings
        this.SENTRY_LOG_LEVEL = logging._nameToLevel.get(
            os.getenv('SENTRY_LOG_LEVEL', 'WARNING').upper(),
            logging.WARNING,
        )
        this.SENTRY_TRANSPORT = os.getenv('SENTRY_TRANSPORT', 'HTTPTransport')
        this.SENTRY_URL = os.getenv('SENTRY_URL', None)

        # Validate important settings
        if not this.CRYPTO_SECRET:
            raise ValueError('env:CRYPTO_SECRET must be provided!')

        return this

    @property
    def environment(self):
        ''' Assume the environment based on the DEBUG flag.
        '''

        if self.DEBUG:
            return 'develop'
        else:
            return 'production'

    @property
    def crypto_salt_bytes(self) -> bytes:
        ''' Try to return CRYPTO_SALT as decoded bytes.
        '''

        try:
            return base64.b64decode(self.CRYPTO_SALT)
        except binascii.Error:
            return bytes(self.CRYPTO_SALT, 'utf-8')

    @property
    def crypto_secret_bytes(self) -> bytes:
        ''' Try to return CRYPTO_SECRET as decoded bytes.
        '''

        try:
            return base64.b64decode(self.CRYPTO_SECRET)
        except binascii.Error:
            return bytes(self.CRYPTO_SECRET, 'utf-8')


component = {
    'cls': Settings,
    'init': Settings.init,
    'persist': True,
}

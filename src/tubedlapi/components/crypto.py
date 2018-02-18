# -*- coding: utf-8 -*-

import logging

from tubedlapi.components import settings as app_settings
from tubedlapi.util import crypto

log = logging.getLogger(__name__)


def make_crypt_provider(settings: app_settings.Settings) -> crypto.CryptoProvider:
    ''' Component initializer for CryptoProvider.
    '''

    if not settings.CRYPTO_SALT:
        log.warning(
            'env:CRYPTO_SALT is None -- this can cause unexpected behaviour '
            'due to regeneration of salt on each initialization of CryptoProvider'
        )
        salt = None
    else:
        salt = settings.crypto_salt_bytes

    return crypto.CryptoProvider(
        secret=settings.crypto_secret_bytes,
        iterations=settings.CRYPTO_KDF_ITERATIONS,
        salt=salt,
    )


component = {
    'cls': crypto.CryptoProvider,
    'init': make_crypt_provider,
    'persist': False,
}

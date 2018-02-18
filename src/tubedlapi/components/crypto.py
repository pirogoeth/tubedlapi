# -*- coding: utf-8 -*-

import logging

from tubedlapi.components import settings as app_settings
from tubedlapi.util import crypto

log = logging.getLogger(__name__)


def make_crypt_provider(settings: app_settings.Settings) -> crypto.CryptProvider:
    ''' Component initializer for CryptoProvider.
    '''

    if not settings.CRYPTO_SALT:
        log.warning(
            'env:CRYPTO_SALT is None -- this can cause unexpected behaviour '
            'due to regeneration of salt on each initialization of CryptProvider'
        )
        salt = None
    else:
        salt = bytes(settings.CRYPTO_SALT, 'utf-8')

    return crypto.CryptProvider(
        secret=bytes(settings.CRYPTO_SECRET, 'utf-8'),
        iterations=settings.CRYPTO_KDF_ITERATIONS,
        salt=salt,
    )


component = {
    'cls': crypto.CryptProvider,
    'init': make_crypt_provider,
    'persist': False,
}

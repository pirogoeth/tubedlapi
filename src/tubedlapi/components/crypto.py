# -*- coding: utf-8 -*-

from tubedlapi.components import settings as app_settings
from tubedlapi.util import crypto


def make_crypt_provider(settings: app_settings.Settings) -> crypto.CryptProvider:
    ''' Component initializer for CryptoProvider.
    '''

    return crypto.CryptProvider(
        secret=bytes(settings.CRYPTO_SECRET, 'utf-8'),
        iterations=settings.CRYPTO_KDF_ITERATIONS,
    )


component = {
    'cls': crypto.CryptProvider,
    'init': make_crypt_provider,
    'persist': False,
}

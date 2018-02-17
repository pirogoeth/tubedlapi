# -*- coding: utf-8 -*-

from typing import Any

from peewee import BlobField


class EncryptedJSONBlobField(BlobField):
    ''' A normal `BlobField`, with transparent encryption on top.
    '''

    CRYPTO_KEY: bytes = None

    def __init__(self, *args, **kw):

        super().__init__(self, *args, **kw)

    def db_value(self, value: Any) -> str:
        ''' Encode some value into JSON, encrypt
            the JSON blob, and encode as `utf-8` string.
        '''

        pass

    def python_value(self, value: bytes) -> Any:
        ''' Decrypt and decode the stored value from JSON
            into a Python object.
        '''

        pass

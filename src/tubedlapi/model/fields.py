# -*- coding: utf-8 -*-

import json
from typing import Any

from peewee import BlobField

from tubedlapi.app import inject
from tubedlapi.util.crypto import CryptoProvider


@inject
def encrypt_blob(crypt: CryptoProvider, blob: bytes) -> bytes:

    return crypt.encrypt_blob(blob)


@inject
def decrypt_blob(crypt: CryptoProvider, message: bytes) -> bytes:

    return crypt.decrypt_message(message)


class EncryptedJSONBlobField(BlobField):
    ''' A normal `BlobField`, with transparent encryption on top.
    '''

    def db_value(self, value: Any) -> str:
        ''' Encode some value into JSON, encrypt
            the JSON blob, and encode as `utf-8` string.
        '''

        blob = json.dumps(value)
        enc_blob = encrypt_blob(blob)
        return enc_blob.decode('utf-8')

    def python_value(self, value: bytes) -> Any:
        ''' Decrypt and decode the stored value from JSON
            into a Python object.
        '''

        blob = decrypt_blob(value)
        return json.loads(blob)

# -*- coding: utf-8 -*-

import json
import logging
from typing import Any, Union

from peewee import BlobField

from tubedlapi.app import inject
from tubedlapi.util.crypto import CryptoProvider

log = logging.getLogger(__name__)


@inject
def encrypt_blob(crypt: CryptoProvider, blob: bytes) -> bytes:

    return crypt.encrypt_blob(blob)


@inject
def decrypt_blob(crypt: CryptoProvider, message: bytes) -> bytes:

    return crypt.decrypt_message(message)


class EncryptedBlobField(BlobField):
    ''' A normal `BlobField` with transparent encryption on top.
    '''

    def db_value(self, value: Union[bytes, str]) -> bytes:
        ''' Encrypt some bytes value and encode as `utf-8` string.
        '''

        value_bytes: bytes = b''
        if isinstance(value, str):
            value_bytes = value.encode('utf-8')
        else:
            value_bytes = value

        enc_blob: bytes = encrypt_blob(value_bytes)
        return enc_blob

    def python_value(self, value: bytes) -> str:
        ''' Decrypt and decode the database value into a bytes
            value.
        '''

        return decrypt_blob(value).decode('utf-8')


class EncryptedJSONBlobField(EncryptedBlobField):
    ''' A normal `BlobField` with transparent encryption on top.
        Marshals/unmarshals the underlying blob value with the JSON
        library.
    '''

    def db_value(self, value: Any) -> bytes:
        ''' Encode some value into JSON, encrypt
            the JSON blob, and encode as `utf-8` string.
        '''

        return super().db_value(json.dumps(value))

    def python_value(self, value: bytes) -> Any:
        ''' Decrypt and decode the stored value from JSON
            into a Python object.
        '''

        return json.loads(super().python_value(value))

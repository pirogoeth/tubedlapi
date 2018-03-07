# -*- coding: utf-8 -*-

import fs
from fs.base import FS
from malibu.text import parse_uri
from peewee import (
    AutoField,
    TextField,
)

from tubedlapi.model import BaseModel
from tubedlapi.model.fields import EncryptedBlobField


class Destination(BaseModel):

    id = AutoField(primary_key=True)
    name = TextField(unique=True)
    url = EncryptedBlobField()

    @property
    def as_fs(self) -> FS:
        ''' Returns a filesystem implementation derived from fs.base.FS
        '''

        return fs.open_fs(self.url)

    @property
    def sanitized_url(self) -> str:
        ''' Returns a sanitized version of the underlying storage URL.
        '''

        uri = parse_uri(self.url)
        password_value = uri.get('password')
        if not password_value:
            return self.url

        sanitized = self.url.replace(password_value, '****')
        return sanitized

    def to_dict(self):
        ''' Dictionary representation of a Destination object
        '''

        return {
            'id': self.id,
            'name': self.name,
            'url': self.sanitized_url,
        }

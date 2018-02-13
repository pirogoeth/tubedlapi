# -*- coding: utf-8 -*-

import codecs

from flask import json
from peewee import (
    AutoField,
    BlobField,
    TextField,
)

from tubedlapi.model import BaseModel


class Profile(BaseModel):

    id = AutoField(primary_key=True)
    name = TextField(unique=True)
    options = BlobField()

    @classmethod
    def from_json(cls, data: bytes) -> 'Profile':

        return Profile(**json.loads(data))

    @property
    def options_dict(self) -> dict:

        return json.loads(self.options)

    def to_dict(self) -> dict:

        return {
            'id': self.id,
            'name': self.name,
            'options': self.options_dict,
        }

    def to_json(self) -> bytes:

        return json.dumps(self.to_dict())

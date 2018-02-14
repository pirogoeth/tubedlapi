# -*- coding: utf-8 -*-

import codecs
import uuid
from datetime import datetime

from flask import json
from peewee import (
    BlobField,
    DateTimeField,
    TextField,
    UUIDField,
)

from tubedlapi.model import BaseModel


class Job(BaseModel):

    id = UUIDField(primary_key=True, unique=True, default=uuid.uuid4)
    created_at = DateTimeField(default=datetime.now)
    status = TextField()
    meta = BlobField()

    @classmethod
    def from_json(self, data: bytes) -> 'Job':

        return Job(**json.loads(data))

    @property
    def meta_dict(self) -> dict:

        return json.loads(self.meta)

    def meta_update(self, **kw) -> dict:

        meta = self.meta_dict
        meta.update(kw)
        self.meta = json.dumps(meta)

    def to_dict(self) -> dict:

        return {
            'id': self.id,
            'created_at': self.created_at,
            'status': self.status,
            'meta': self.meta_dict,
        }

    def to_json(self) -> bytes:

        return json.dumps(self.to_dict())

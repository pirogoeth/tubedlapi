# -*- coding: utf-8 -*-

import logging

from peewee import (
    AutoField,
    TextField,
)

from tubedlapi.model import BaseModel
from tubedlapi.model.fields import EncryptedJSONBlobField


class Destination(BaseModel):

    id = AutoField(primary_key=True)
    name = TextField()
    type = TextField()
    config = EncryptedJSONBlobField()

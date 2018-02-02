# -*- coding: utf-8 -*-

import json

from apistar import typesystem
from sqlalchemy import (
    Column,
    Integer,
    LargeBinary,
    String,
)
from sqlalchemy.orm.query import Query

from tubedlapi.model import BaseModel, get_session

ProfileName = typesystem.string(
    description='Name of profile, url-encoded if necessary',
    default='default',
)


class Profile(BaseModel):

    __tablename__ = 'profile'

    id = Column(Integer, primary_key=True, autoincrement='auto')
    name = Column(String, unique=True)
    options = Column(LargeBinary)

    @classmethod
    def find(cls, **query) -> Query:

        session = get_session()
        return session.query(cls).filter_by(**query)


class ProfileOptions(dict):

    description = (
        'youtube-dl options dictionary. see <a href=\'https://github.com/rg3/youtube-dl'
        '/blob/master/README.md#embedding-youtube-dl\'>rg3/youtube-dl</a> for examples.'
    )


class ProfileObject(typesystem.Object):

    properties = {
        'id': typesystem.integer(
            description='Profile identifier',
        ),
        'name': ProfileName,
        'options': typesystem.newtype(
            ProfileOptions,
        ),
    }

    default = {
        'options': {
            'format': 'bestaudio/best',
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                },
            ],
        },
    }

    @classmethod
    def from_model(cls, model: Profile):

        return ProfileObject(
            id=model.id,
            name=model.name,
            options=json.loads(model.options),
        )

    def to_model(self) -> Profile:

        return Profile(
            id=self.get('id', None),
            name=self.get('name', None),
            options=bytes(json.dumps(self.get('options', '{}')), 'utf-8'),
        )

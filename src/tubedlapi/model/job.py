# -*- coding: utf-8 -*-

import json
import typing
import uuid
from datetime import datetime

from apistar import typesystem
from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    LargeBinary,
    String,
)
from sqlalchemy.orm.query import Query

from tubedlapi.model import BaseModel, get_session
from tubedlapi.model.profile import ProfileName


JobId = typesystem.string(
    max_length=36,
    min_length=36,
    description='UUID4 representing this job',
)


class Job(BaseModel):

    __tablename__ = 'job'

    id = Column(String, primary_key=True, unique=True)
    created_at = Column(DateTime)
    status = Column(String)
    meta = Column(LargeBinary)

    @classmethod
    def new(cls):

        return Job(
            id=str(uuid.uuid4()),
            created_at=datetime.now(),
            status='queued',
            meta=json.dumps({}),
        )

    @classmethod
    def find(cls, **query) -> Query:

        session = get_session()
        return session.query(cls).filter_by(**query)


class JobStatus(typesystem.Enum):

    description = 'Job status as returned from the API'
    enum = ['queued', 'downloading', 'finished']


class JobMetadata(typesystem.Object):

    description = 'Metadata for execution of the job by youtube-dl'
    properties = {
        'url': typesystem.string(
            description='URL of video to download',
            pattern='https?://(.+)',
        ),
        'profile': ProfileName,
    }

    def to_json(self) -> bytes:

        return bytes(json.dumps(self), 'utf-8')


class JobObject(typesystem.Object):

    description = 'Job structure'
    properties = {
        'id': JobId,
        'created_at': typesystem.string(
            format='date',
            description='Creation timestamp for this job',
        ),
        'status': JobStatus,
        'meta': JobMetadata,
    }

    default = {}

    @classmethod
    def from_model(cls, model: Job) -> 'JobObject':

        return JobObject(
            id=model.id,
            created_at=model.created_at,
            status=model.status,
            meta=JobMetadata(json.loads(model.meta)),
        )

    def to_model(self) -> Job:

        return Job(
            id=self['id'],
            created_at=datetime.strptime(self['created_at'], '%Y-%m-%d %H:%M:%S.%f'),
            status=self['status'],
            meta=self.get('meta', JobMetadata()).to_json(),
        )

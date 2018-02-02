# -*- coding: utf-8 -*-

import logging
import typing
from http import HTTPStatus as status
from urllib.parse import unquote_plus

import sqlalchemy
from apistar import Response, Route, typesystem
from apistar.backends.sqlalchemy_backend import Session
from tubedlapi.model import binding
from tubedlapi.model.profile import (
    Profile,
    ProfileName,
    ProfileObject,
)

log = logging.getLogger(__name__)


def list_profiles(session: Session) -> typing.List[ProfileObject]:

    profiles = session.query(Profile).all()
    return [ProfileObject.from_model(p) for p in profiles]


def create_profile(session: Session, profile: ProfileObject) -> ProfileObject:

    # TODO: Do not allow overwriting of profiles
    new_profile = profile.to_model()
    try:
        session.add(new_profile)
        session.flush()
        return ProfileObject.from_model(new_profile)
    except sqlalchemy.exc.IntegrityError:
        session.rollback()

        return Response({
            'message': 'name already in use',
        }, status=status.CONFLICT)


def show_profile(session: Session, name: ProfileName) -> ProfileObject:

    name = unquote_plus(name)
    res = []

    with binding(session):
        res = Profile.find(name=name).all()

    if len(res) > 0:
        return ProfileObject.from_model(res[0])
    else:
        return Response({
            'message': 'not found',
            'query': {
                'name': name,
            },
        }, status=status.NOT_FOUND)


def delete_profile(session: Session, name: ProfileName) -> dict:

    name = unquote_plus(name)

    res = session.query(Profile).filter_by(name=name).all()
    if len(res) > 0:
        ret = ProfileObject.from_model(res[0])
        session.delete(res[0])
        session.commit()
        return Response({
            'message': 'deleted',
            'profile': ret,
        }, status=status.OK)
    else:
        return Response({
            'message': 'not found',
            'query': {
                'name': name,
            },
        }, status=status.NOT_FOUND)


routes = [
    Route('/', 'GET', list_profiles),
    Route('/', 'POST', create_profile),
    Route('/{name}', 'GET', show_profile),
    Route('/{name}', 'DELETE', delete_profile),
]

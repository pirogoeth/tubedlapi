# -*- coding: utf-8 -*-

import contextlib
import typing

from apistar.backends.sqlalchemy_backend import (
    Session,
    SQLAlchemyBackend,
    get_session as session_manager,
)
from sqlalchemy.ext.declarative import declarative_base

BaseModel = declarative_base()
__session = None


@contextlib.contextmanager
def binding(session: Session) -> typing.Generator:
    ''' Used in the duration of a request to bind models to the
        current, active Session instance.

        Mostly useful for 'hygienic' classmethods on models,
        a la `Profile.find()`.
    '''

    global __session
    __session = session

    yield

    __session = None


def get_session() -> Session:
    ''' Returns the Session or raises a RuntimeError
        if session access is attempted outside of a request.
    '''

    global __session

    if not __session:
        raise RuntimeError('Attempted session access outside of request')

    return __session


@contextlib.contextmanager
def make_new_session() -> typing.Generator[Session, None, None]:
    ''' Uses the app instance to bind a new session object
        for use when a request is not in progress.
    '''

    from tubedlapi.app import get_app

    backend = get_app().preloaded_state[SQLAlchemyBackend]

    with session_manager(backend) as session:
        yield session


@contextlib.contextmanager
def binding_new_session() -> typing.Generator:
    ''' Generative wrapper around `make_new_session`.
    '''

    with make_new_session() as session:
        with binding(session):
            yield session

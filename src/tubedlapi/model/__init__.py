# -*- coding: utf-8 -*-

import glob
import inspect
import logging
import os
import peewee
import playhouse

from playhouse.migrate import (
    PostgresqlMigrator,
    SqliteMigrator,
)
from importlib import import_module
from malibu.text import parse_uri

from tubedlapi.components import settings

modules = glob.glob(os.path.dirname(__file__) + '/*.py')
__all__ = [os.path.basename(f)[:-3] for f in modules
           if not os.path.basename(f).startswith('_') and
              not f.endswith('__init__.py') and os.path.isfile(f)]

LOG = logging.getLogger(__name__)

database_proxy = peewee.Proxy()
database_migrator = None


class FKSqliteDatabase(peewee.SqliteDatabase):
    ''' A simple wrapper around peewee's SqliteDatabase that
        enables foreign keys with a pragma when the connection
        is initialized.
    '''

    def initialize_connection(self, conn):

        self.execute_sql('PRAGMA foreign_keys=ON;')


class BaseModel(peewee.Model):
    ''' Simple base model with the database set as a peewee
        database proxy so we can dynamically initialize the
        database connection with information from the config
        file.
    '''

    class Meta:
        database = database_proxy


def init_database_from_uri(db_uri: str) -> peewee.Proxy:
    ''' Builds a database connection from a DB URI.
    '''

    global database_migrator

    db_uri = parse_uri(db_uri)

    if db_uri['protocol'] == 'sqlite':
        database = FKSqliteDatabase(db_uri['resource'])
        database_migrator = SqliteMigrator(database)
    elif db_uri['protocol'] == 'postgres':
        database = playhouse.postgres_ext.PostgresqlExtDatabase(
            db_uri['database'],
            user=db_uri['username'],
            password=db_uri['password'],
            host=db_uri['host'],
            port=db_uri['port'],
        )
        database_migrator = PostgresqlMigrator(database)
    else:
        raise ValueError('Unknown DB schema: {}'.format(db_uri['protocol']))

    database_proxy.initialize(database)
    database.connect()

    # Import all BaseModels and run create_tables(...)
    tables = []
    for module in __all__:
        mod = import_module('{}.{}'.format(__package__, module))
        for member in dir(mod):
            member_obj = getattr(mod, member)

            if not inspect.isclass(member_obj):
                continue

            if member_obj.__name__ == 'BaseModel':
                continue

            if issubclass(member_obj, BaseModel):
                LOG.debug('Loading database model: %s.%s.%s' % (
                    __package__, module, member))
                tables.append(member_obj)

    LOG.debug('Ensuring tables are safely created..')

    try:
        database.create_tables(tables, safe=True)
    except:
        LOG.exception('An error occurred while ensuring tables')

    return database_proxy

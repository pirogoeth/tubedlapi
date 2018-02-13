# -*- coding: utf-8 -*-

import peewee

from tubedlapi.components import settings as app_settings
from tubedlapi.model import init_database_from_uri


def init_database_with_settings(settings: app_settings.Settings) -> peewee.Proxy:
    ''' Component initializer for a peewee.Proxy
    '''

    return init_database_from_uri(settings.DATABASE_URI)


component = {
    'cls': peewee.Proxy,
    'init': init_database_with_settings,
    'persist': True,
}

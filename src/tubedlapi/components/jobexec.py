# -*- coding: utf-8 -*-

from tubedlapi.util.async import JobExecutor

component = {
    'cls': JobExecutor,
    'init': lambda: JobExecutor(),
    'persist': True,
}

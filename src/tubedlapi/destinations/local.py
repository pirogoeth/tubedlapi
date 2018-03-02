# -*- coding: utf-8 -*-

import io
import logging

from tubedlapi.destinations import BaseDestination

log = logging.getLogger(__name__)


class LocalDestination(BaseDestination):

    def __init__(self, config):

        self._config = config
        # TODO: config validation for the destination

    def create(self, filename, content, meta=None) -> dict:

        return None

    def delete(self, filename) -> bool:

        return False

    def read(self, filename) -> io.BufferedReader:

        return None

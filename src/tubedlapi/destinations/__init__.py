# -*- coding: utf-8 -*-

import abc
import glob
import io
import os

modules = glob.glob(os.path.dirname(__file__) + "/*.py")
__all__ = [os.path.basename(f)[:-3] for f in modules
           if not os.path.basename(f).startswith('_') and
           not f.endswith('__init__.py') and os.path.isfile(f)]


class BaseDestination(abc.ABC):
    """ Basic CR(!U)D-style API for storing files to a (possibly remote)
        destination.
    """

    @abc.abstractmethod
    def create(self, filename, content, meta=None) -> dict:
        """ Create a file on the remote
        """

        pass

    @abc.abstractmethod
    def delete(self, filename) -> bool:
        """ Delete a file on the remote
        """

        pass

    @abc.abstractmethod
    def read(self, filename) -> io.BufferedReader:
        """ Read the contents of a file from the remote
            (Will this even be necessary??)
        """

        pass

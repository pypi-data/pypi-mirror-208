import zipfile
import os
from contextlib import contextmanager
from functools import lru_cache
from abc import ABC, abstractmethod
from typing import List
import re
import sys


class DataSource:
    """ An abstract class describing a datasource: either standard folder or a Zip file"""
    def __init__(self, path: str):
        self.path = path
        if not os.path.isdir(path):
            self._archive: zipfile.ZipFile = zipfile.ZipFile(self.path, mode='r')
        else:
            self._archive = None

    @contextmanager
    def open(self, file):
        """ Wrapper around the zipfile.open and open context managers """
        if self._archive:
            f = self._archive.open(file, 'r')
        else:
            f = open(os.path.join(self.path, file), mode='rb')
        try:
            yield f
        finally:
            f.close()

    @lru_cache(None)
    def listdir(self):
        """ List directory contents """
        if self._archive:
            return self._archive.namelist()
        else:
            return os.listdir(self.path)

    def __repr__(self):
        if self._archive:
            return f'<DataSource @ {self.path} (Zip archive)>'
        else:
            return f'<DataSource @ {self.path}>'


class LazyClass(ABC):
    """ A Lazy class that loads data on demand """
    def __init__(self):
        self._loaded = False
        for attribute in self._lazy:
            self.__setattr__(attribute, None)

    def __getattribute__(self, item):
        if item in ['_lazy', '_loaded', 'load', '__setattr__', 'loaded']:
            return super().__getattribute__(item)

        if item in self._lazy and not self._loaded:
            self.load()
        return super().__getattribute__(item)

    @abstractmethod
    def load(self):
        pass

    @property
    @abstractmethod
    def _lazy(self) -> List[str]:
        pass

    @property
    def loaded(self):
        return self._loaded


def make_valid_tag_name(var_name: str):
    """ Make a valid tag name """
    split = re.split(r'[^0-9a-zA-Z_]', var_name)
    var_name = '_'.join([cp.upper() for cp in split if cp])
    return re.sub('^[^a-zA-Z_]+', '', var_name)


def in_notebook():
    """ Check to see if we are in jupyter notebook """
    return 'ipykernel' in sys.modules


def load_pv():
    """ Load pyvista """
    try:
        import pyvista as pv
    except ImportError:
        raise ImportError('Pyvista must be installed for this method to work. '
                          'Use pip install carto_reader[viz] to install visualization dependencies.')
    return pv

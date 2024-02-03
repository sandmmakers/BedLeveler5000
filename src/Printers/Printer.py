from Common.LoggedFunction import loggedFunction
from PySide6 import QtCore
import abc
import logging

class Printer(QtCore.QObject):
    __metaclass__ = abc.ABCMeta

    def __init__(self, parent=None):
        super().__init__(parent)

        # Create logger
        self.logger = logging.getLogger(self.__class__.__name__)

    def connected(self, *args, **kwargs):
        return self._connected(*args, **kwargs)

    @abc.abstractmethod
    def _connected(self):
        raise NotImplementedError

    @loggedFunction
    def open(self, *args, **kwargs):
        self._open(*args, **kwargs)

    @abc.abstractmethod
    def _open(self):
        raise NotImplementedError

    @loggedFunction
    def close(self, *args, **kwargs):
        self._close()

    @abc.abstractmethod
    def _close(self):
        raise NotImplementedError
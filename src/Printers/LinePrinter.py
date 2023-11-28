from .Printer import Printer
from Common.LoggedFunction import loggedFunction
from PySide6 import QtCore
import abc
import logging

class LinePrinter(Printer):
    __metaclass__ = abc.ABCMeta

    sent = QtCore.Signal(str)
    received = QtCore.Signal(str)
    errorOccured = QtCore.Signal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Get logger
        self.logger = logging.getLogger(self.__class__.__name__)

    @loggedFunction
    def abort(self):
        self._abort()

    @abc.abstractmethod
    def _abort(self):
        raise NotImplementedError

    @loggedFunction
    def sendCommand(self, command):
        self._sendCommand(command)

    @abc.abstractmethod
    def _sendCommand(self, command):
        raise NotImplementedError

    @loggedFunction
    def _reportReceived(self, line):
        self.received.emit(line)

    @loggedFunction
    def _reportError(self, message):
        self.errorOccurred.emit(message)
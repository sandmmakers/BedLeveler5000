#!/usr/bin/env python

from .SerialConnection import SerialConnection
from PySide6 import QtCore

class LineConnection(SerialConnection):
    errorOccurred = QtCore.Signal(str)
    received = QtCore.Signal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _processLine(self, line):
        self.received.emit(line)
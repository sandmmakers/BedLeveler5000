from ..LinePrinter import LinePrinter
from .LineConnection import LineConnection
from Common.LoggedFunction import loggedFunction
from PySide6 import QtCore

class Marlin2LinePrinter(LinePrinter):
    def __init__(self, *args, printerInfo, port=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.port = port
        self.lineConnection = LineConnection(printerInfo)
        self.lineConnection.received.connect(self._reportReceived)
        # TODO: Determine if errorOccurred is required

    def _connected(self):
        return self.lineConnection.connected()

    def _open(self, port=None):
        if port is not None:
            self.port = port
        if self.port is None:
            raise ValueError('Port has not been set.')

        self.lineConnection.open(self.port)

    def _close(self):
        self.lineConnection.close()

    def _abort(self):
        pass

    def _sendCommand(self, command):
        self.lineConnection.write(command)
        self.sent.emit(command)
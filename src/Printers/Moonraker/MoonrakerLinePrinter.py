from Printers.LinePrinter import LinePrinter
from Common.LoggedFunction import loggedFunction
from PySide6 import QtCore
from PySide6 import QtNetwork

class MoonrakerLinePrinter(LinePrinter):
    def __init__(self, printerInfo, host=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.host = host
        self.networkAccessManager = QtNetwork.QNetworkAccessManager()
        self.networkAccessManager.finished.connect(self._processReply)

        self.isConnected = False
        self.replySet = set()

    def _connected(self):
        return self.isConnected

    def _open(self, host=None):
        self.host = host if host is not None else self.host
        if self.host is None:
            raise ValueError('Host has not been set.')

        self.isConnected = True

    def _close(self):
        self.isConnected = False

    def _sendCommand(self, command):
        if command.startswith('/'):
            endpoint = command
        else:
            endpoint = '/printer/gcode/script?script=' + command

        requestCommand = f'http://{self.host}{endpoint}'
        self.logger.debug(f'Sending get: {requestCommand}')

        request = QtNetwork.QNetworkRequest(requestCommand)
        self.replySet.add(self.networkAccessManager.get(request))
        self.sent.emit(requestCommand)

    def _processReply(self, reply):
        replyBuffer = reply.readAll()

        # TODO: Add error handling on conversion and parsing
        self.received.emit(str(replyBuffer, 'ascii'))

        reply.deleteLater()
        self.replySet.remove(reply)

    def _abort(self):
        for reply in self.replySet:
            reply.abort()
            reply.deleteLater()
        self.replySet.clear()

    def _errorOccurred(self, message):
        pass
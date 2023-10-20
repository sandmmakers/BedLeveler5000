#!/usr/bin/env python

from Connection import Connection
from PySide6 import QtCore
import logging

class LineConnection(Connection):
    received = QtCore.Signal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _processLine(self, line):
        self.logger.info(f'Received: \'{line}\'')
        self.received.emit(line)

    def sendCommand(self, command):
        self.logger.info(f'Sending: \'{command}\'')
        self.serialPort.write((command + '\n').encode())

if __name__ == '__main__':
    # Main only imports
    from PrinterInfo import PrinterInfo
    from PySide6 import QtCore
    from PySide6 import QtWidgets
    from PySide6 import QtSerialPort
    import sys

    app = QtWidgets.QApplication(sys.argv)

    # Configure logging
    logging.basicConfig(level = logging.DEBUG)
    logger = logging.getLogger()

    connection = LineConnection(printerInfo = PrinterInfo())
    connection.received.connect(lambda string : print(f'Received: {string}'))
    connection.open('COM4')

    connection.sendCommand('M114')

    widget = QtWidgets.QWidget()
    widget.show()

    sys.exit(app.exec())
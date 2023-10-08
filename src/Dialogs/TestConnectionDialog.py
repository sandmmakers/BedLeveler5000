#!/usr/bin/env python3

import pathlib
import sys
sys.path.append(pathlib.Path(__file__).parent.parent.as_posix())

from CommandConnection import CommandConnection
from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets
import logging
import uuid

class TestConnectionDialog(QtWidgets.QDialog):
    MAX_ATTEMPTS = 3
    TIMEOUT = 1000

    def __init__(self, port, printerInfo, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle('Testing connection')

        self.port = port
        self.connection = CommandConnection(printerInfo=printerInfo, commonSignal=True)
        self.connection.received.connect(self.processResponse)
        self.connection.error.connect(self.handleError)

        self.label = QtWidgets.QLabel('Status: Testing')

        self.button = QtWidgets.QPushButton('Cancel')
        self.button.clicked.connect(self.close)

        dialogButtonBox = QtWidgets.QDialogButtonBox()
        dialogButtonBox.addButton(self.button, QtWidgets.QDialogButtonBox.ButtonRole.ActionRole)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(dialogButtonBox)
        self.setLayout(layout)

        self.attempts = 0

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(lambda : self._end(False))

        try:
            self.connection.open(self.port)
        except OSError:
            self._end(False)

        self.test()

    def test(self):
        self.timer.start(self.TIMEOUT)
        self.uuid = str(uuid.uuid1())
        self.attempts += 1
        self.connection.sendM118(self.uuid, string=self.uuid)

    def processResponse(self, commandName, _id, _, response):
        # Test if command succeeded
        self._end(commandName == 'M118' and _id == self.uuid and response['string'] == self.uuid)

    def handleError(self):
        if self.attempts >= self.MAX_ATTEMPTS:
            self._error(False)
        else:
            self.test()

    def close(self):
        self.connection.close()
        self.timer.stop()
        self.accept()

    def _end(self, result):
        self.button.setText('Close')
        self.timer.stop()
        self.label.setText(f'Status: {"Success" if result else "Fail"}')

if __name__ == '__main__':
    # Main only imports
    from PrinterInfo import PrinterInfo
    import sys
    from PySide6 import QtCore
    from PySide6 import QtWidgets
    from PySide6 import QtSerialPort

    app = QtWidgets.QApplication(sys.argv)

    # Configure logging
    logging.basicConfig(level = logging.DEBUG)
    logger = logging.getLogger()

    testConnectionDialog = TestConnectionDialog('COM4', PrinterInfo())
    testConnectionDialog.show()

    sys.exit(app.exec())
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

class PerformHomingDialog(QtWidgets.QDialog):
    def __init__(self, port, printerInfo, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle('Performing homing')

        self.port = port
        self.connection = CommandConnection(printerInfo=printerInfo, commonSignal=True)
        self.connection.received.connect(self.processResponse)

        self.label = QtWidgets.QLabel('Status: Homing')

        self.button = QtWidgets.QPushButton('Cancel')
        self.button.clicked.connect(lambda : self.finish(False))

        dialogButtonBox = QtWidgets.QDialogButtonBox()
        dialogButtonBox.addButton(self.button, QtWidgets.QDialogButtonBox.ButtonRole.ActionRole)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(dialogButtonBox)
        self.setLayout(layout)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(lambda : self._error)
        self.timer.start(15000)
        self.uuid = str(uuid.uuid1())

        try:
            self.connection.open(self.port)
            self.connection.sendG28(self.uuid)
        except OSError:
            self._error()

    def processResponse(self, commandName, _id, _, response):
        if commandName != 'G28' or _id != self.uuid: # Replace hardcoded name
            self._error()
        else:
            self.finish(True)

    def finish(self, accept):
        self.connection.close()
        self.timer.stop()

        if accept:
            self.accept()
        else:
            self.reject()

    def _error(self):
        self.connection.close()
        self.timer.stop()
        QtWidgets.QMessageBox.warning(self, 'Error', 'Query failed.')
        self.reject()

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

    performHomingDialog = PerformHomingDialog('COM4', PrinterInfo())
    performHomingDialog.show()

    sys.exit(app.exec())
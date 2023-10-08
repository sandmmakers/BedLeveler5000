#!/usr/bin/env python3

import pathlib
import sys
sys.path.append(pathlib.Path(__file__).parent.parent.as_posix())

from CommandConnection import CommandConnection
import PrinterInfo
from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets
import logging
import uuid

class ConfigureGridPointDialog(QtWidgets.QDialog):
    MAXIMUM = 999
    DECIMALS = 2

    def __init__(self, port, printerInfo, point, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle('Configure Grid Point')

        self.__createWidgets(point)
        self.__layoutWidgets()

        self.port = port
        self.connection = CommandConnection(printerInfo=printerInfo, commonSignal=True)
        self.connection.received.connect(self.processResponse)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(lambda : self._error())

        self.updateGui()

    def __createWidgets(self, point):
        self.rowLineEdit = QtWidgets.QLineEdit(str(point.row))
        self.rowLineEdit.setEnabled(False)
        self.columnLineEdit = QtWidgets.QLineEdit(str(point.column))
        self.columnLineEdit.setEnabled(False)

        # Create editable widgets
        self.nameLineEdit = QtWidgets.QLineEdit('' if point.name is None else point.name)
        self.nameLineEdit.textChanged.connect(self.updateGui)
        self.xSpinBox = QtWidgets.QDoubleSpinBox()
        self.xSpinBox.setMaximum(self.MAXIMUM)
        self.xSpinBox.setDecimals(self.DECIMALS)
        if point.x is not None:
            self.xSpinBox.setValue(point.x)
        self.ySpinBox = QtWidgets.QDoubleSpinBox()
        self.ySpinBox.setMaximum(self.MAXIMUM)
        self.ySpinBox.setDecimals(self.DECIMALS)
        if point.y is not None:
            self.ySpinBox.setValue(point.y)

        self.okButton = QtWidgets.QPushButton('Ok')
        self.okButton.clicked.connect(lambda : self.finish(True))
        self.okButton.setToolTip('Name field must be set.')

        self.cancelButton = QtWidgets.QPushButton('Cancel')
        self.cancelButton.clicked.connect(lambda : self.finish(False))

        self.queryButton = QtWidgets.QPushButton('Query')
        self.queryButton.clicked.connect(self.query)

    def __layoutWidgets(self):
        dialogButtonBox = QtWidgets.QDialogButtonBox(QtCore.Qt.Vertical)
        dialogButtonBox.addButton(self.okButton, QtWidgets.QDialogButtonBox.ButtonRole.AcceptRole)
        dialogButtonBox.addButton(self.cancelButton, QtWidgets.QDialogButtonBox.ButtonRole.RejectRole)
        dialogButtonBox.addButton(self.queryButton, QtWidgets.QDialogButtonBox.ButtonRole.ActionRole)

        layout = QtWidgets.QGridLayout()
        layout.addWidget(QtWidgets.QLabel('Name:'), 0, 0)
        layout.addWidget(self.nameLineEdit, 0, 1, 1, 3)
        layout.addWidget(QtWidgets.QLabel('Row:'), 1, 0)
        layout.addWidget(self.rowLineEdit, 1, 1)
        layout.addWidget(QtWidgets.QLabel('Col:'), 1, 2)
        layout.addWidget(self.columnLineEdit, 1, 3)
        layout.addWidget(QtWidgets.QLabel('X:'), 2, 0)
        layout.addWidget(self.xSpinBox, 2, 1)
        layout.addWidget(QtWidgets.QLabel('Y:'), 2, 2)
        layout.addWidget(self.ySpinBox, 2, 3)
        layout.addWidget(dialogButtonBox, 0, 4, 3, 1)

        self.setLayout(layout)
        self.resize(layout.minimumSize())

    def updateGui(self):
        self.okButton.setEnabled(len(self.nameLineEdit.text()) > 0)

    def processResponse(self, commandName, _id, _, response):
        self.connection.close()
        self.timer.stop()

        if commandName != 'M114' or _id != self.uuid: # TODO: Replace 'M114' with CommandM114.name
            self.error()

        else:
            self.xSpinBox.setValue(response['x']) # TODO: Verify range
            self.ySpinBox.setValue(response['y']) # TODO: Verify range

    def finish(self, accept):
        self.connection.close()
        self.timer.stop()

        if accept:
            self.accept()
        else:
            self.reject()

    def query(self):
        self.timer.start(3000)
        self.uuid = str(uuid.uuid1())

        try:
            self.connection.open(self.port)
            self.connection.sendM114(self.uuid)
        except OSError:
            self._error()

    def point(self):
        return PrinterInfo.GridProbePoint(name = self.nameLineEdit.text(),
                                          row = int(self.rowLineEdit.text()),
                                          column = int(self.columnLineEdit.text()),
                                          x = self.xSpinBox.value(),
                                          y = self.ySpinBox.value())

    def _error(self):
        self.connection.close()
        self.timer.stop()
        QtWidgets.QMessageBox.warning(self, 'Error', 'Query failed.')

if __name__ == '__main__':
    # Main only imports
    import sys
    from PySide6 import QtCore
    from PySide6 import QtWidgets
    from PySide6 import QtSerialPort

    app = QtWidgets.QApplication(sys.argv)

    # Configure logging
    logging.basicConfig(level = logging.DEBUG)
    logger = logging.getLogger()

    gridPoint = PrinterInfo.GridProbePoint(row=2, column=0)
    configureGridPointDialog = ConfigureGridPointDialog('COM4', PrinterInfo.PrinterInfo(), gridPoint)
    configureGridPointDialog.show()

    sys.exit(app.exec())
#!/usr/bin/env python

from Common.PrinterInfo import GridProbePoint
from Printers.CommandPrinter import GetCurrentPositionResult
from Common.PrinterInfo import Marlin2Connection
from Common.PrinterInfo import MoonrakerConnection
from Printers.Marlin2.Marlin2Printer import Marlin2Printer
from Printers.Moonraker.MoonrakerPrinter import MoonrakerPrinter
from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets
import logging
import uuid

class ConfigureGridPointDialog(QtWidgets.QDialog):
    MAXIMUM = 999
    DECIMALS = 3

    def __init__(self, *args, host, port, printerInfo, gridPoint, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle('Configure Grid Point')

        self.__createWidgets(gridPoint)
        self.__layoutWidgets()

        if isinstance(printerInfo.connection, Marlin2Connection):
            assert(port is not None)
            self.printer = Marlin2Printer(printerInfo=printerInfo, port=port, parent=self)
        elif isinstance(printerInfo.connection, MoonrakerConnection):
            assert(host is not None)
            self.printer = MoonrakerPrinter(printerInfo=printerInfo, host=host, parent=self)
        else:
            raise ValueError('Detected unsupported connection mode.')

        self.printer.gotCurrentPosition.connect(self.processPosition)

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

    def processPosition(self, _id, _, response):
        self.printer.close()
        self.timer.stop()

        if _id != self.uuid:
            self.error()
        else:
            self.xSpinBox.setValue(response.x)
            self.ySpinBox.setValue(response.y)

    def finish(self, accept):
        self.printer.close()
        self.timer.stop()

        if accept:
            self.accept()
        else:
            self.reject()

    def query(self):
        self.timer.start(3000)
        self.uuid = str(uuid.uuid1())

        try:
            self.printer.open()
            self.printer.getCurrentPosition(self.uuid)
        except OSError:
            self._error()

    def point(self):
        return GridProbePoint(name = self.nameLineEdit.text(),
                              row = int(self.rowLineEdit.text()),
                              column = int(self.columnLineEdit.text()),
                              x = self.xSpinBox.value(),
                              y = self.ySpinBox.value())

    def _error(self):
        self.printer.close()
        self.timer.stop()
        QtWidgets.QMessageBox.warning(self, 'Error', 'Query failed.')

if __name__ == '__main__':
    # Main only imports
    from Common.Common import configureLogging
    from Common import PrinterInfo
    from Common.PrinterInfo import ConnectionMode
    from PySide6 import QtCore
    from PySide6 import QtWidgets
    from PySide6 import QtSerialPort
    import argparse
    import pathlib
    import signal
    import sys

    # Enable CTRL-C killing the application
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Create the application
    app = QtWidgets.QApplication(sys.argv)

    # Parse arguments
    parser = argparse.ArgumentParser(description='TestConnectionDialog Test App')
    printerSpecificGroup = parser.add_mutually_exclusive_group(required=True)
    printerSpecificGroup.add_argument('--port', default=None, help='port to use for Marlin2 connection')
    printerSpecificGroup.add_argument('--host', default=None, help='host to use for Moonraker connection')
    parser.add_argument('--log-level', choices=['all', 'debug', 'info', 'warning', 'error', 'critical'], default=None, help='logging level')
    parser.add_argument('--log-console', action='store_true', help='log to the console')
    parser.add_argument('--log-file', type=pathlib.Path, default=None, help='log file')

    args = parser.parse_args()

    # Configure logging
    configureLogging(level=args.log_level, console=args.log_console, file=args.log_file)

    # Create the PrinterInfo
    printerInfo = PrinterInfo.default(ConnectionMode.MOONRAKER if args.port is None else ConnectionMode.MARLIN_2)

    # Create the dialog
    gridPoint = GridProbePoint(row=2, column=0)
    configureGridPointDialog = ConfigureGridPointDialog(printerInfo=printerInfo, port=args.port, host=args.host, gridPoint=gridPoint)
    configureGridPointDialog.show()

    try:
       sys.exit(app.exec())
    except KeyboardInterrupt:
        sys.exit(1)
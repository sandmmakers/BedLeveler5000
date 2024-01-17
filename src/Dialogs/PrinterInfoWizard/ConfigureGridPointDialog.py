#!/usr/bin/env python

from Common.PrinterInfo import ConnectionMode
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
    TIMEOUT = 3000
    MAXIMUM = 999
    DECIMALS = 3

    def __init__(self, *args, host, port, printerInfo, gridPoint, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle('Configure Grid Point')
        self.xOffset = None
        self.yOffset = None

        self.__createWidgets(gridPoint)
        self.__layoutWidgets()

        # Create the printer
        assert printerInfo.connectionMode in [ConnectionMode.MARLIN_2, ConnectionMode.MOONRAKER]
        if printerInfo.connectionMode == ConnectionMode.MARLIN_2:
            assert port is not None
            self.printer = Marlin2Printer(printerInfo=printerInfo, port=port, parent=self)
        elif printerInfo.connectionMode == ConnectionMode.MOONRAKER:
            assert host is not None
            self.printer = MoonrakerPrinter(printerInfo=printerInfo, host=host, parent=self)

        # Setup printer connections
        self.printer.gotProbeOffsets.connect(self._query)
        self.printer.gotCurrentPosition.connect(self._processPosition)
        self.printer.errorOccurred.connect(self._error)

        # Create timer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(lambda : self._error())

        # Ensure the printer is always closed
        self.finished.connect(self.close)

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
        self.fixedComboBox = QtWidgets.QComboBox()
        self.fixedComboBox.addItem('Yes', True)
        self.fixedComboBox.addItem('No', False)
        self.fixedComboBox.setCurrentText('Yes' if point.fixed else 'No')

        self.okButton = QtWidgets.QPushButton('Ok')
        self.okButton.clicked.connect(self.accept)
        self.okButton.setToolTip('Name field must be set.')

        self.cancelButton = QtWidgets.QPushButton('Cancel')
        self.cancelButton.clicked.connect(self.reject)

        self.queryNozzleButton = QtWidgets.QPushButton('Query Nozzle')
        self.queryNozzleButton.clicked.connect(lambda: self.getProbeOffsets(False))

        self.queryProbeButton = QtWidgets.QPushButton('Query Probe')
        self.queryProbeButton.clicked.connect(lambda: self.getProbeOffsets(True))

    def __layoutWidgets(self):
        dialogButtonBox = QtWidgets.QDialogButtonBox(QtCore.Qt.Vertical)
        dialogButtonBox.addButton(self.okButton, QtWidgets.QDialogButtonBox.ButtonRole.AcceptRole)
        dialogButtonBox.addButton(self.cancelButton, QtWidgets.QDialogButtonBox.ButtonRole.RejectRole)
        dialogButtonBox.addButton(self.queryNozzleButton, QtWidgets.QDialogButtonBox.ButtonRole.ActionRole)
        dialogButtonBox.addButton(self.queryProbeButton, QtWidgets.QDialogButtonBox.ButtonRole.ActionRole)

        layout = QtWidgets.QGridLayout()
        layout.addWidget(QtWidgets.QLabel('Name:'), 0, 0)
        layout.addWidget(self.nameLineEdit, 0, 1)
        layout.addWidget(QtWidgets.QLabel('Fixed:'), 0, 2)
        layout.addWidget(self.fixedComboBox, 0, 3)
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
        self.xSpinBox.setEnabled(not self.printer.connected())
        self.ySpinBox.setEnabled(not self.printer.connected())

    def close(self):
        self.printer.close()
        self.timer.stop()

    def finish(self, accept):
        if accept:
            self.accept()
        else:
            self.reject()

    def getProbeOffsets(self, probe):
        self.timer.start(self.TIMEOUT)
        self.uuid = str(uuid.uuid1())

        try:
            self.printer.open()
            self.printer.getProbeOffsets(f'{self.uuid}-offsets', context={'probe': probe})
            self.updateGui()
        except OSError:
            self._error()

    def _query(self, _id, context, response):
        self.xOffset = response.xOffset
        self.yOffset = response.yOffset

        if _id != f'{self.uuid}-offsets':
            self.error()
        else:
            self.timer.start(self.TIMEOUT)
            self.printer.getCurrentPosition(f'{self.uuid}-query', context=context)

    def _processPosition(self, _id, context, response):
        self.printer.close()
        self.timer.stop()

        if _id != f'{self.uuid}-query':
            self.error()
        else:
            x = response.x
            y = response.y
            if context['probe']:
                x += self.xOffset
                y += self.yOffset

            self.xSpinBox.setValue(x)
            self.ySpinBox.setValue(y)
        self.updateGui()

    def point(self):
        return GridProbePoint(name = self.nameLineEdit.text(),
                              fixed = self.fixedComboBox.currentData(),
                              row = int(self.rowLineEdit.text()),
                              column = int(self.columnLineEdit.text()),
                              x = self.xSpinBox.value(),
                              y = self.ySpinBox.value())

    def _error(self):
        self.close()
        QtWidgets.QMessageBox.warning(self, 'Error', 'Query failed.')
        self.updateGui()

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


    parser.add_argument('-n', '--name', default='Test', help='name of point')
    parser.add_argument('-f', '--fixed', action='store_true', help='is point fixed')
    parser.add_argument('-r', '--row', default=2, type=int, help='row value')
    parser.add_argument('-c', '--column', default=0, type=int, help='column value')
    parser.add_argument('-x', default=0.0, type=float, help='x coordinate')
    parser.add_argument('-y', default=0.0, type=float, help='y coordinate')
    parser.add_argument('--log-level', choices=['all', 'debug', 'info', 'warning', 'error', 'critical'], default=None, help='logging level')
    parser.add_argument('--log-console', action='store_true', help='log to the console')
    parser.add_argument('--log-file', type=pathlib.Path, default=None, help='log file')

    args = parser.parse_args()

    # Configure logging
    configureLogging(level=args.log_level, console=args.log_console, file=args.log_file)

    # Create the PrinterInfo
    printerInfo = PrinterInfo.default(ConnectionMode.MOONRAKER if args.port is None else ConnectionMode.MARLIN_2)

    # Create the dialog
    gridPoint = GridProbePoint(name = args.name,
                               fixed = args.fixed,
                               row = args.row,
                               column = args.column,
                               x = args.x,
                               y = args.y)
    configureGridPointDialog = ConfigureGridPointDialog(printerInfo=printerInfo, port=args.port, host=args.host, gridPoint=gridPoint)

    try:
        if configureGridPointDialog.exec() == QtWidgets.QDialog.Accepted:
            print(str(configureGridPointDialog.point()))
        else:
            print('Canceled')
    except KeyboardInterrupt:
        sys.exit(1)
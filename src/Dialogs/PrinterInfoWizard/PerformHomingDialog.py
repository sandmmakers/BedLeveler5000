#!/usr/bin/env python

from Common.PrinterInfo import Marlin2Connection
from Common.PrinterInfo import MoonrakerConnection
from Printers.Marlin2.Marlin2Printer import Marlin2Printer
from Printers.Moonraker.MoonrakerPrinter import MoonrakerPrinter
from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets
import logging
import uuid

class PerformHomingDialog(QtWidgets.QDialog):
    def __init__(self, *args, printerInfo, host=None, port=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle('Performing homing')

        if isinstance(printerInfo.connection, Marlin2Connection):
            assert(port is not None)
            self.printer = Marlin2Printer(printerInfo=printerInfo, port=port, parent=self)
        elif isinstance(printerInfo.connection, MoonrakerConnection):
            assert(host is not None)
            self.printer = MoonrakerPrinter(printerInfo=printerInfo, host=host, parent=self)
        else:
            raise ValueError('Detected unsupported connection mode.')

        self.printer.homed.connect(self.processHomed)

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
            self.printer.open()
            self.printer.home(self.uuid)
        except OSError:
            self._error()

    def processHomed(self, _id, _):
        if _id != self.uuid:
            self._error()
        else:
            self.finish(True)

    def finish(self, accept):
        self.printer.close()
        self.timer.stop()

        if accept:
            self.accept()
        else:
            self.reject()

    def _error(self):
        self.printer.abort()
        self.printer.close()
        self.timer.stop()
        QtWidgets.QMessageBox.warning(self, 'Error', 'Query failed.')
        self.reject()

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
    parser.add_argument('--log-level', choices=['all', 'debug', 'info', 'warning', 'error', 'critical'], default='warning', help='logging level')
    parser.add_argument('--log-console', action='store_true', help='log to the console')
    parser.add_argument('--log-file', type=pathlib.Path, default=None, help='log file')

    args = parser.parse_args()

    # Configure logging
    configureLogging(level=args.log_level, console=args.log_console, file=args.log_file)

    # Create the PrinterInfo
    printerInfo = PrinterInfo.default(ConnectionMode.MOONRAKER if args.port is None else ConnectionMode.MARLIN_2)

    # Create the dialog
    performHomingDialog = PerformHomingDialog(printerInfo=printerInfo, host=args.host, port=args.port)
    performHomingDialog.show()

    try:
       sys.exit(app.exec())
    except KeyboardInterrupt:
        sys.exit(1)
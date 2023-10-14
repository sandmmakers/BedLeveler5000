#!/usr/bin/env python3

import Common
from Dialogs.AboutDialog import AboutDialog
from Dialogs.WarningDialog import WarningDialog
from Dialogs.ErrorDialog import ErrorDialog
from Dialogs.FatalErrorDialog import FatalErrorDialog
from LineConnection import LineConnection
from PrinterInfo import PrinterInfo
from PortComboBox import PortComboBox
import Version
from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets
from PySide6 import QtSerialPort
import argparse
import json
import logging
import pathlib
import sys

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, printersDir, printer=None, port=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle(QtCore.QCoreApplication.applicationName())
        self.logger = logging.getLogger(QtCore.QCoreApplication.applicationName())

        self.connection = LineConnection()
        self.connection.received.connect(self._logLine)

        self._createWidgets()
        self._layoutWidgets()
        self._createMenus()
        self._createDialogs()

        self.printersDir = printersDir
        self.loadPrinters(printer)

        if port is not None:
            try:
                self.portCombBox.setPort(port)
            except ValueError as exception:
                self._warning(exception)

        self._updateState()

    def loadPrinters(self, desiredPrinter=None):
        self.printerComboBox.blockSignals(True)

        self.printerComboBox.clear()

        for filePath in self.printersDir.glob('**/*.json'):
            printerInfo = PrinterInfo.fromFile(filePath)
            self.printerComboBox.addItem(printerInfo.displayName, printerInfo)

        if self.printerComboBox.count() <= 0:
            self._fatalError('No printers found.')

        self.printerComboBox.blockSignals(False)

        index = 0 if desiredPrinter is None else self.printerComboBox.findText(desiredPrinter)
        if index == -1:
            self._warning('Failed to find requested printer.')
        else:
            self.printerComboBox.setCurrentIndex(index)

        # Ensure switchPrinter always gets called
        if index == 0:
            self.switchPrinter()

    def switchPrinter(self):
        try:
            self.printerInfo = self.printerComboBox.currentData()
            self.connection.setPrinter(self.printerInfo)

        except ValueError as valueError:
            self._fatalError(valueError.args[0])

    def _createWidgets(self):
        # Connection widgets
        self.printerComboBox = QtWidgets.QComboBox()
        self.printerComboBox.currentIndexChanged.connect(self.switchPrinter)

        self.portComboBox = PortComboBox()
        self.connectButton = QtWidgets.QPushButton()

        self.commandLineEdit = QtWidgets.QLineEdit()
        self.commandLineEdit.textChanged.connect(self._updateState)

        self.sendCommandButton = QtWidgets.QPushButton('Send')
        self.sendCommandButton.clicked.connect(lambda : self.sendCommand(self.commandLineEdit.text()))

        self.logTextEdit = QtWidgets.QTextEdit()
        self.logTextEdit.setReadOnly(True)
        font = self.logTextEdit.document().defaultFont()
        font.setFamily('Courier New')
        self.logTextEdit.document().setDefaultFont(font)

        self.clearButton = QtWidgets.QPushButton('Clear')
        self.clearButton.clicked.connect(lambda : self.logTextEdit.clear())

    def _layoutWidgets(self):
        # Connection layout
        connectionLayout = QtWidgets.QHBoxLayout()
        connectionLayout.addWidget(QtWidgets.QLabel('Printer:'))
        connectionLayout.addWidget(self.printerComboBox)
        connectionLayout.addWidget(QtWidgets.QLabel('Port:'))
        connectionLayout.addWidget(self.portComboBox)
        connectionLayout.addWidget(self.connectButton)
        connectionLayout.addStretch()
        connectionGroupBox = QtWidgets.QGroupBox('Connection')
        connectionGroupBox.setLayout(connectionLayout)

        # Command layout
        commandLayout = QtWidgets.QHBoxLayout()
        commandLayout.addWidget(QtWidgets.QLabel('Command:'))
        commandLayout.addWidget(self.commandLineEdit)
        commandLayout.addWidget(self.sendCommandButton)

        # Clear layout
        clearLayout = QtWidgets.QHBoxLayout()
        clearLayout.addStretch()
        clearLayout.addWidget(self.clearButton)
        clearLayout.addStretch()

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(connectionGroupBox)
        layout.addLayout(commandLayout)
        layout.addWidget(self.logTextEdit)
        layout.addLayout(clearLayout)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def _createMenus(self):
        # File menu
        self.fileMenu = QtWidgets.QMenu('File', self)
        self.exitAction = QtGui.QAction('Exit', self)
        self.exitAction.setStatusTip('Exit the application')
        self.exitAction.triggered.connect(self.close)
        self.fileMenu.addAction(self.exitAction)
        self.menuBar().addMenu(self.fileMenu)

        # Ports
        self.portsMenu = QtWidgets.QMenu('Ports', self)
        self.enumeratePortsAction = QtGui.QAction('Enumerate', self)
        self.enumeratePortsAction.setStatusTip('Reenumerate COM ports')
        self.enumeratePortsAction.triggered.connect(self.portComboBox.enumeratePorts)
        self.portsMenu.addAction(self.enumeratePortsAction)
        self.menuBar().addMenu(self.portsMenu)

        self.settingsMenu = QtWidgets.QMenu('Settings', self)
        self.menuBar().addMenu(self.settingsMenu)

        self.helpMenu = QtWidgets.QMenu('Help', self)
        self.aboutAction = QtGui.QAction('About', self)
        self.aboutAction.triggered.connect(lambda : self.dialogs['about'].exec())
        self.helpMenu.addAction(self.aboutAction)
        self.aboutQtAction = QtGui.QAction('About Qt', self)
        self.aboutQtAction.triggered.connect(qApp.aboutQt)
        self.helpMenu.addAction(self.aboutQtAction)
        self.menuBar().addMenu(self.helpMenu)

    def _createStatusBar(self):
        self.statusBar()

    def _createDialogs(self):
        self.dialogs = {'about': AboutDialog('A simple G-code testing utility.')}

    def _updateState(self):
        self.printerComboBox.setEnabled(not self.connection.connected())
        self.portComboBox.setEnabled(not self.connection.connected())
        self.enumeratePortsAction.setEnabled(not self.connection.connected())
        self.sendCommandButton.setEnabled(self.connection.connected() and len(self.commandLineEdit.text()) > 0)

        QtCore.QObject.disconnect(self.connectButton, None, None, None)
        if not self.connection.connected():
            self.connectButton.setText('Connect')
            self.connectButton.clicked.connect(lambda x: self._openSerialPort(self.portComboBox.currentText()))
            self.statusBar().showMessage('Disconnected')
        else:
            self.connectButton.setText('Disconnect')
            self.connectButton.clicked.connect(self._closeSerialPort)
            self.statusBar().showMessage('Connected')

    def _openSerialPort(self, portName):
        try:
            # Open serial port
            self.connection.open(portName)
        except IOError as exception:
            self._error(exception.args[1])

        self._updateState()

    def _closeSerialPort(self):
        self.connection.close()
        self._updateState()

    def sendCommand(self, command):
        assert(self.connection.connected())
        self.logTextEdit.append(f'SENT: \'{command}\'')
        self.connection.sendCommand(command)

    def _logLine(self, line):
        self.logTextEdit.append(f'RECV: \'{line}\'')

    def _fatalError(self, message):
        self.logger.critical(message)
        self._closeSerialPort()
        for dialog in self.dialogs.values():
            dialog.reject()
        FatalErrorDialog(self, message)

    def _error(self, message):
        self.logger.error(message)
        self._closeSerialPort()
        for dialog in self.dialogs.values():
            dialog.reject()
        ErrorDialog(self, message)

    def _warning(self, message):
        self.logger.warning(message)
        WarningDialog(self, message)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon((Common.baseDir() / 'Resources' / 'InspectorG-code_Icon_128x128.png').as_posix()))

    QtCore.QCoreApplication.setApplicationName('Inspector G-code')
    QtCore.QCoreApplication.setApplicationVersion(Version.version())

    # Windows only, configure icon settings
    try:
        from ctypes import windll
        myappid = f'com.sandmmakers.inspectorg-code.{QtCore.QCoreApplication.setApplicationVersion}'
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except ImportError:
        pass

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Utility for testing G-code')
    parser.add_argument('-v', '--version', action='version', version=QtCore.QCoreApplication.applicationVersion())
    parser.add_argument('--printers-dir', default=Common.baseDir() / 'Printers', type=pathlib.Path, help='printer information directory')
    parser.add_argument('--printer', default=None, help='printer to use')
    parser.add_argument('--port', default=None, help='port to use')
    parser.add_argument('--log_level', choices=['debug', 'info', 'warning', 'error', 'critical'], default=None, help='logging level')
    parser.add_argument('--log_console', action='store_true', help='log to the console')
    parser.add_argument('--log_file', type=pathlib.Path, default=None, help='log file')

    args = parser.parse_args()

    # Configure logging
    Common.configureLogging(level=args.log_level, console=args.log_console, file=args.log_file)

    # Verify the printers directory exists
    if args.printers_dir is not None and not args.printers_dir.exists():
        FatalErrorDialog(None, f'Failed to find printer directory: {args.printers_dir}.')

    mainWindow = MainWindow(printersDir=args.printers_dir, printer=args.printer, port=args.port)
    mainWindow.show()
    app.exec()
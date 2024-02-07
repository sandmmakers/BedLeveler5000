#!/usr/bin/env python

from Common import Common
from Common.CommonArgumentParser import CommonArgumentParser
from Dialogs.AboutDialog import AboutDialog
from Dialogs.WarningDialog import WarningDialog
from Dialogs.ErrorDialog import ErrorDialog
from Dialogs.FatalErrorDialog import FatalErrorDialog
from Printers.Marlin2.Marlin2LinePrinter import Marlin2LinePrinter
from Printers.Moonraker.MoonrakerLinePrinter import MoonrakerLinePrinter
from Common import PrinterInfo
from Widgets.PrinterConnectWidget import PrinterConnectWidget
from Common.PrinterInfo import ConnectionMode
from Common import Version
from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets
from PySide6 import QtSerialPort
import argparse
import json
import logging
import pathlib
import signal
import sys

# Enable CTRL-C killing the application
signal.signal(signal.SIGINT, signal.SIG_DFL)

DESCRIPTION = 'A simple G-code testing utility.'

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, printersDir, *args, printer=None, host=None, port=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle(QtCore.QCoreApplication.applicationName())
        self.logger = logging.getLogger(QtCore.QCoreApplication.applicationName())

        self.__createWidgets()
        self.__layoutWidgets()
        self.__createMenus()
        self.__createDialogs()
        self.__createStatusBar()

        self.printer = None
        self.printerQtConnections = []
        self.printerConnectWidget.loadPrinters(printersDir,
                                               desiredPrinter = printer,
                                               desiredHost = host,
                                               desiredPort = port)

        self._updateState()

    def __createWidgets(self):
        # Printer connect widget
        self.printerConnectWidget = PrinterConnectWidget(hasHomeButton=False)
        self.printerConnectWidget.connectRequested.connect(self.connectToPrinter)
        self.printerConnectWidget.disconnectRequested.connect(self.disconnectFromPrinter)

        self.commandLineEdit = QtWidgets.QLineEdit()
        self.commandLineEdit.textChanged.connect(self._updateState)

        self.sendCommandButton = QtWidgets.QPushButton('Send')
        self.sendCommandButton.clicked.connect(self.sendCommand)

        self.logTextEdit = QtWidgets.QTextEdit()
        self.logTextEdit.setReadOnly(True)
        font = self.logTextEdit.document().defaultFont()
        font.setFamily('Courier New')
        self.logTextEdit.document().setDefaultFont(font)

        self.autoClearCheckBox = QtWidgets.QCheckBox('Auto Clear')
        self.autoClearCheckBox.setChecked(True)

        self.clearButton = QtWidgets.QPushButton('Clear')
        self.clearButton.clicked.connect(self.clear)

    def __layoutWidgets(self):
        # Command layout
        commandLayout = QtWidgets.QHBoxLayout()
        commandLayout.addWidget(QtWidgets.QLabel('Command:'))
        commandLayout.addWidget(self.commandLineEdit)
        commandLayout.addWidget(self.sendCommandButton)

        # button layout
        buttonLayout = QtWidgets.QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.autoClearCheckBox)
        buttonLayout.addWidget(self.clearButton)
        buttonLayout.addStretch()

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.printerConnectWidget)
        layout.addLayout(commandLayout)
        layout.addWidget(self.logTextEdit)
        layout.addLayout(buttonLayout)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def __createMenus(self):
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
        self.enumeratePortsAction.triggered.connect(self.printerConnectWidget.enumeratePorts)
        self.portsMenu.addAction(self.enumeratePortsAction)
        self.menuBar().addMenu(self.portsMenu)

        self.settingsMenu = QtWidgets.QMenu('Settings', self)
        self.menuBar().addMenu(self.settingsMenu)

        self.helpMenu = QtWidgets.QMenu('Help', self)
        self.aboutAction = QtGui.QAction('About', self)
        self.aboutAction.triggered.connect(lambda : AboutDialog(DESCRIPTION).exec())
        self.helpMenu.addAction(self.aboutAction)
        self.aboutQtAction = QtGui.QAction('About Qt', self)
        self.aboutQtAction.triggered.connect(qApp.aboutQt)
        self.helpMenu.addAction(self.aboutQtAction)
        self.menuBar().addMenu(self.helpMenu)

    def __createStatusBar(self):
        self.statusBar()

    def __createDialogs(self):
        self.dialogs = {'about': AboutDialog(DESCRIPTION)}

    def _updateState(self):
        connected = self.printer is not None and self.printer.connected()

        if not connected:
            self.printerConnectWidget.setDisconnected()
            self.statusBar().showMessage('Disconnected')
        else:
            self.printerConnectWidget.setConnected()
            self.statusBar().showMessage('Connected')

        self.enumeratePortsAction.setEnabled(not connected)
        self.sendCommandButton.setEnabled(connected and len(self.commandLineEdit.text()) > 0)

    def connectToPrinter(self):
        # Create the printer and determine open arguments
        assert self.printerConnectWidget.connectionMode() in [ConnectionMode.MARLIN_2, ConnectionMode.MOONRAKER]
        if self.printerConnectWidget.connectionMode() == ConnectionMode.MARLIN_2:
            self.printer = Marlin2LinePrinter(printerInfo = self.printerConnectWidget.printerInfo(),
                                              port = self.printerConnectWidget.port(),
                                              parent = self)
        elif self.printerConnectWidget.connectionMode() == ConnectionMode.MOONRAKER:
            self.printer = MoonrakerLinePrinter(printerInfo = self.printerConnectWidget.printerInfo(),
                                                host = self.printerConnectWidget.host(),
                                                parent = self)

        self.printerQtConnections.append(self.printer.sent.connect(self._logCommand))
        self.printerQtConnections.append(self.printer.received.connect(self._logLine))
        #self.printerQtConnections.append(self.printer.errorOccured.connect(self.logError))

        self.printer.open()
        self._updateState()

    def disconnectFromPrinter(self):
        self.printer.close()

        # Break connections
        for qtConnection in self.printerQtConnections:
            self.printer.disconnect(qtConnection)
        self.printerQtConnections = []

        self.printer = None
        self._updateState()

    def clear(self):
        self.logTextEdit.clear()

    def sendCommand(self):
        assert(self.printer.connected())
        if self.autoClearCheckBox.isChecked():
            self.clear()
        self.printer.sendCommand(self.commandLineEdit.text())

    def _logCommand(self, command):
        self.logTextEdit.append(f'SENT: \'{command}\'')

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
    app.setWindowIcon(QtGui.QIcon((Common.resourcesDir() / 'InspectorG-code_Icon_128x128.png').as_posix()))
    app.setApplicationName('Inspector G-code')
    app.setApplicationVersion(Version.displayVersion())

    # Windows only, configure icon settings
    try:
        from ctypes import windll
        myappid = f'com.sandmmakers.inspectorg-code.{QtCore.QCoreApplication.setApplicationVersion}'
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except ImportError:
        pass

    # Parse command line arguments
    parser = CommonArgumentParser(description=DESCRIPTION)
    args = parser.parse_args()

    # Configure logging
    Common.configureLogging(level=args.log_level, console=args.log_console, file=args.log_file)
    logging.getLogger(QtCore.QCoreApplication.applicationName()).info(f'Starting {app.applicationName()}')

    # Verify the printers directory exists
    if args.printers_dir is not None and not args.printers_dir.exists():
        FatalErrorDialog(None, f'Failed to find printer directory: {args.printers_dir}.')

    try:
        mainWindow = MainWindow(printersDir=args.printers_dir,
                                printer=args.printer,
                                host=args.host,
                                port=args.port)
        mainWindow.show()
        sys.exit(app.exec())
    except KeyboardInterrupt:
        sys.exit(1)
    except Exception as exception:
        FatalErrorDialog(None, str(exception))
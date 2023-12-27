#!/usr/bin/env python

from Common import Common
from Common.CommonArgumentParser import CommonArgumentParser
from Dialogs.AboutDialog import AboutDialog
from Dialogs.PrinterInfoWizard.TestConnectionDialog import TestConnectionDialog
from Dialogs.PrinterInfoWizard.ConfigureGridPointDialog import ConfigureGridPointDialog
from Dialogs.PrinterInfoWizard.PerformHomingDialog import PerformHomingDialog
from Dialogs.ErrorDialog import ErrorDialog
from Dialogs.FatalErrorDialog import FatalErrorDialog
from Common import PrinterInfo
from Common.PrinterInfo import ConnectionMode
from Common.PrinterInfo import CONNECTION_MODE_MAP
from Common.PrinterInfo import BAUD_RATE_MAP
from Common.PrinterInfo import DATA_BITS_MAP
from Common.PrinterInfo import PARITY_MAP
from Common.PrinterInfo import STOP_BITS_MAP
from Common.PrinterInfo import FLOW_CONTROL_MAP
from Common.PrinterInfo import PRINTER_INFO_FILE_FILTER
from Common.PrinterInfo import Marlin2Connection
from Common.PrinterInfo import MoonrakerConnection
from Widgets.PrinterConnectWidget import PrinterConnectWidget
from Widgets.PrinterInfoWizard import WizardGrid
from Widgets.PrinterInfoWizard.SerialWidget import SerialWidget
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

DESCRIPTION = 'A utility for creating and editing printer infos.'

class PrinterInfoWizard(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle('Printer Info Wizard')
        self.logger = logging.getLogger(self.windowTitle())

        self.__createWidgets()
        self.__layoutWidgets()
        self.__createMenus()
        self.__createDialogs()

        self.loadDefaults()
        self.updateConnectionMode()
        self.enumeratePorts()

    def __createWidgets(self):
        self.connectionModeComboBox = QtWidgets.QComboBox()
        for label, mode in CONNECTION_MODE_MAP.items():
            self.connectionModeComboBox.addItem(label, mode)
        self.connectionModeComboBox.currentIndexChanged.connect(self.updateConnectionMode)

        self.specificStackedWidget = QtWidgets.QStackedWidget()
        self.specificStackedWidget.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.portComboBox = QtWidgets.QComboBox()
        self.hostLineEdit = QtWidgets.QLineEdit()

        self.displayNameLineEdit = QtWidgets.QLineEdit()

        self.marlin2ConnectionWidget = SerialWidget()
        self.moonrakerConnectionWidget = QtWidgets.QWidget()

        self.connectionStackedWidget = QtWidgets.QStackedWidget()
        self.connectionStackedWidget.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.testButton = QtWidgets.QPushButton('Test')
        self.testButton.clicked.connect(self.test)

        self.homeButton = QtWidgets.QPushButton('Home')
        self.homeButton.clicked.connect(self.home)

        self.grid = WizardGrid.Grid('Manual Test Points')
        self.grid.cellClicked.connect(self.configureManualProbePoint)

    def __layoutWidgets(self):
        # Layout stacked widgets
        for label, mode in CONNECTION_MODE_MAP.items():
            if mode == ConnectionMode.MOONRAKER:
                hostLayout = QtWidgets.QHBoxLayout()
                hostLayout.addWidget(QtWidgets.QLabel('Host:'))
                hostLayout.addWidget(self.hostLineEdit)
                hostLayout.addStretch()
                hostWidget = QtWidgets.QWidget()
                hostWidget.setLayout(hostLayout)
                hostWidget.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
                self.specificStackedWidget.addWidget(hostWidget)

                self.connectionStackedWidget.addWidget(self.moonrakerConnectionWidget)
            elif mode == ConnectionMode.MARLIN_2:
                portLayout = QtWidgets.QHBoxLayout()
                portLayout.addWidget(QtWidgets.QLabel('Port:'))
                portLayout.addWidget(self.portComboBox)
                portLayout.addStretch()
                portWidget = QtWidgets.QWidget()
                portWidget.setLayout(portLayout)
                portWidget.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
                self.specificStackedWidget.addWidget(portWidget)

                self.connectionStackedWidget.addWidget(self.marlin2ConnectionWidget)
            else:
                assert('Unsupported communication mode detected.')

        topLayout = QtWidgets.QHBoxLayout()
        topLayout.addWidget(QtWidgets.QLabel('Connection mode:'))
        topLayout.addWidget(self.connectionModeComboBox)
        topLayout.addWidget(self.specificStackedWidget)
        topLayout.addStretch()

        displayNameLayout = QtWidgets.QHBoxLayout()
        displayNameLayout.addWidget(QtWidgets.QLabel('Display Name:'))
        displayNameLayout.addWidget(self.displayNameLineEdit)

        connectionButtonLayout = QtWidgets.QHBoxLayout()
        connectionButtonLayout.addWidget(self.testButton)
        connectionButtonLayout.addWidget(self.homeButton)

        connectionLayout = QtWidgets.QVBoxLayout()
        connectionLayout.addWidget(self.connectionStackedWidget)
        connectionLayout.addStretch()
        connectionLayout.addLayout(connectionButtonLayout)

        connectionGroupBox = QtWidgets.QGroupBox('Connection')
        connectionGroupBox.setLayout(connectionLayout)

        connectionGridLayout = QtWidgets.QHBoxLayout()
        connectionGridLayout.addWidget(connectionGroupBox)
        connectionGridLayout.addWidget(self.grid)

        printerInfoLayout = QtWidgets.QVBoxLayout()
        printerInfoLayout.addLayout(displayNameLayout)
        printerInfoLayout.addLayout(connectionGridLayout)

        printerInfoGroupBox = QtWidgets.QGroupBox('Printer Info')
        printerInfoGroupBox.setLayout(printerInfoLayout)

        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(topLayout)
        layout.addWidget(printerInfoGroupBox)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def __createMenus(self):
        # File menu
        self.fileMenu = QtWidgets.QMenu('File', self)
        self.openAction = QtGui.QAction('Open', self)
        self.openAction.setStatusTip('Open a printer info file')
        self.openAction.triggered.connect(self.openFile)
        self.fileMenu.addAction(self.openAction)

        self.loadDefaultsAction = QtGui.QAction('Load defaults', self)
        self.loadDefaultsAction.setStatusTip('Open a printer info file')
        self.loadDefaultsAction.triggered.connect(self.loadDefaults)
        self.fileMenu.addAction(self.loadDefaultsAction)

        self.saveAsAction = QtGui.QAction('Save as', self)
        self.saveAsAction.setStatusTip('Save printer info to a new file')
        self.saveAsAction.triggered.connect(self.saveAsFile)
        self.fileMenu.addAction(self.saveAsAction)
        self.exitAction = QtGui.QAction('Exit', self)
        self.exitAction.setStatusTip('Exit the application')
        self.exitAction.triggered.connect(self.close)
        self.fileMenu.addAction(self.exitAction)
        self.menuBar().addMenu(self.fileMenu)

        # Ports
        self.portsMenu = QtWidgets.QMenu('Ports', self)
        self.enumeratePortsAction = QtGui.QAction('Enumerate', self)
        self.enumeratePortsAction.setStatusTip('Reenumerate COM ports')
        self.enumeratePortsAction.triggered.connect(self.enumeratePorts)
        self.portsMenu.addAction(self.enumeratePortsAction)
        self.menuBar().addMenu(self.portsMenu)

        self.helpMenu = QtWidgets.QMenu('Help', self)
        self.aboutAction = QtGui.QAction('About', self)
        self.aboutAction.triggered.connect(lambda : self.dialogs['about'].exec())
        self.helpMenu.addAction(self.aboutAction)
        self.aboutQtAction = QtGui.QAction('About Qt', self)
        self.aboutQtAction.triggered.connect(qApp.aboutQt)
        self.helpMenu.addAction(self.aboutQtAction)
        self.menuBar().addMenu(self.helpMenu)

    def __createDialogs(self):
        self.dialogs = {'about': AboutDialog(DESCRIPTION)}

    def updateConnectionMode(self):
        self.specificStackedWidget.setCurrentIndex(self.connectionModeComboBox.currentIndex())
        self.connectionStackedWidget.setCurrentIndex(self.connectionModeComboBox.currentIndex())

    def enumeratePorts(self):
        previous = self.portComboBox.currentText()

        self.portComboBox.clear()
        for serialPortInfo in QtSerialPort.QSerialPortInfo.availablePorts():
            self.portComboBox.addItem(serialPortInfo.portName())
        self.portComboBox.setCurrentText(previous)

    def saveAsFile(self):
        if len(self.displayNameLineEdit.text()) <= 0:
            self.warning('Display name can not be empty.')
            return

        filePath = QtWidgets.QFileDialog.getSaveFileName(self,
                                                         'Select new printer info file',
                                                         None,
                                                         PRINTER_INFO_FILE_FILTER)[0]
        if len(filePath) <= 0:
            return
        filePath = pathlib.Path(filePath)

        with open(filePath, 'w', newline='') as file:
            json.dump(self.currentPrinterInfo().asJson(), file, indent=4)

    def loadDefaults(self):
        self.displayNameLineEdit.clear()

        defaultMarlin2Connection = PrinterInfo.default(ConnectionMode.MARLIN_2).connection
        self.marlin2ConnectionWidget.setBaudRate(defaultMarlin2Connection.baudRate)
        self.marlin2ConnectionWidget.setDataBits(defaultMarlin2Connection.dataBits)
        self.marlin2ConnectionWidget.setParity(defaultMarlin2Connection.parity)
        self.marlin2ConnectionWidget.setStopBits(defaultMarlin2Connection.stopBits)
        self.marlin2ConnectionWidget.setFlowControl(defaultMarlin2Connection.flowControl)
        self.grid.clear()

    def openFile(self):
        filePath = QtWidgets.QFileDialog.getOpenFileName(self,
                                                         'Open printer info',
                                                         None,
                                                         PRINTER_INFO_FILE_FILTER)[0]
        if len(filePath) > 0:
            self.loadPrinterInfo(filePath)

    def loadPrinterInfo(self, filePath):
        try:
            self.setPrinterInfo(PrinterInfo.fromFile(filePath))
        except(ValueError, IOError) as exception:
            ErrorDialog(self, str(exception))
            return

    def setPrinterInfo(self, printerInfo):
        def setComboBox(comboBox, value):
            index = comboBox.findData(value)
            if value == -1:
                raise ValueError()

            comboBox.setCurrentIndex(index)

        self.displayNameLineEdit.setText(printerInfo.displayName)

        connectionModeIndex = self.connectionModeComboBox.findData(printerInfo.connectionMode)
        if connectionModeIndex == -1:
            raise ValueError('Detected an unsupported connection mode.')
        self.connectionModeComboBox.setCurrentIndex(connectionModeIndex)

        if printerInfo.connectionMode == ConnectionMode.MARLIN_2:
            self.marlin2ConnectionWidget.setBaudRate(printerInfo.connection.baudRate)
            self.marlin2ConnectionWidget.setDataBits(printerInfo.connection.dataBits)
            self.marlin2ConnectionWidget.setParity(printerInfo.connection.parity)
            self.marlin2ConnectionWidget.setStopBits(printerInfo.connection.stopBits)
            self.marlin2ConnectionWidget.setFlowControl(printerInfo.connection.flowControl)

        self.grid.clear()
        for point in printerInfo.manualProbePoints:
            self.grid.setPoint(point)

    def test(self):
        testConnectionDialog = TestConnectionDialog(host = self.hostLineEdit.text(),
                                                    port = self.portComboBox.currentText(),
                                                    printerInfo = self.currentPrinterInfo())
        testConnectionDialog.exec()

    def home(self):
        dialog = PerformHomingDialog(host = self.hostLineEdit.text(),
                                     port = self.portComboBox.currentText(),
                                     printerInfo = self.currentPrinterInfo())
        dialog.exec()

    def configureManualProbePoint(self, gridProbePoint):
        dialog = ConfigureGridPointDialog(host = self.hostLineEdit.text(),
                                          port = self.portComboBox.currentText(),
                                          printerInfo = self.currentPrinterInfo(),
                                          gridPoint = gridProbePoint)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self.grid.setPoint(dialog.point())

    def currentPrinterInfo(self):
        assert self.connectionModeComboBox.currentData() in [ConnectionMode.MARLIN_2, ConnectionMode.MOONRAKER]
        if self.connectionModeComboBox.currentData() == ConnectionMode.MARLIN_2:
            connection = Marlin2Connection(baudRate = self.marlin2ConnectionWidget.baudRate(),
                                           dataBits = self.marlin2ConnectionWidget.dataBits(),
                                           parity = self.marlin2ConnectionWidget.parity(),
                                           stopBits = self.marlin2ConnectionWidget.stopBits(),
                                           flowControl = self.marlin2ConnectionWidget.flowControl())
        else:
            connection = MoonrakerConnection()

        return PrinterInfo._PrinterInfo(displayName = self.displayNameLineEdit.text(),
                                        connectionMode = self.connectionModeComboBox.currentData(),
                                        connection = connection,
                                        manualProbePoints = self.grid.getPoints())

    def warning(self, message):
        QtWidgets.QMessageBox.warning(self, 'Warning', message)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon((Common.baseDir() / 'Resources' / 'PrinterInfoWizard-128x128.png').as_posix()))
    QtCore.QCoreApplication.setApplicationName('Printer Info Wizard')
    QtCore.QCoreApplication.setApplicationVersion(Version.displayVersion())

    # Windows only, configure icon settings
    try:
        from ctypes import windll
        myappid = f'com.sandmmakers.printerinfowizard.{QtCore.QCoreApplication.setApplicationVersion}'
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except ImportError:
        pass

    # Parse command line arguments
    parser = CommonArgumentParser(description=DESCRIPTION, addPrinters=False)
    args = parser.parse_args()

    # Configure logging
    Common.configureLogging(level=args.log_level, console=args.log_console, file=args.log_file)

    printerInfoWizard = PrinterInfoWizard()
    printerInfoWizard.show()

    try:
       sys.exit(app.exec())
    except KeyboardInterrupt:
        sys.exit(1)
    except Exception as exception:
        FatalErrorDialog(None, str(exception))
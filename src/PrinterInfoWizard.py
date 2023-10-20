#!/usr/bin/env python

from CommandConnection import CommandConnection
import Common
from Dialogs.AboutDialog import AboutDialog
from Dialogs.NoButtonStatusDialog import NoButtonStatusDialog
from Dialogs.WarningDialog import WarningDialog
from Dialogs.ErrorDialog import ErrorDialog
from Dialogs.FatalErrorDialog import FatalErrorDialog
from Dialogs.TestConnectionDialog import TestConnectionDialog
from Dialogs.ConfigureGridPointDialog import ConfigureGridPointDialog # TODO: Standardize how dialogs are used
from Dialogs.PerformHomingDialog import PerformHomingDialog # TODO: Standardize how dialogs are used
import PrinterInfo
from PortComboBox import PortComboBox
import WizardGrid
import Version
from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets
from PySide6 import QtSerialPort
import json
import logging
import pathlib

class PrinterInfoWizard(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle('Printer Info Wizard')
        self.logger = logging.getLogger(self.windowTitle())

        self._createWidgets()
        self._layoutWidgets()
        self._createMenus()
        self._createDialogs()

        self.loadDefaults()

    def _createWidgets(self):
        self.portComboBox = PortComboBox()

        self.defaultsButton = QtWidgets.QPushButton('Defaults')
        self.defaultsButton.clicked.connect(self.loadDefaults)

        self.homeButton = QtWidgets.QPushButton('Home')
        self.homeButton.clicked.connect(self.home)

        self.displayNameLineEdit = QtWidgets.QLineEdit()

        self.gCodeFlavorComboBox = QtWidgets.QComboBox()
        for label, value in PrinterInfo.G_CODE_FLAVOR_MAP.items():
            self.gCodeFlavorComboBox.addItem(label, value)

        self.baudRateComboBox = QtWidgets.QComboBox()
        for label, value in PrinterInfo.BAUD_RATE_MAP.items():
            self.baudRateComboBox.addItem(label, value)

        self.dataBitsComboBox = QtWidgets.QComboBox()
        for label, value in PrinterInfo.DATA_BITS_MAP.items():
            self.dataBitsComboBox.addItem(label, value)

        self.parityComboBox = QtWidgets.QComboBox()
        for label, value in PrinterInfo.PARITY_MAP.items():
            self.parityComboBox.addItem(label, value)

        self.stopBitsComboBox = QtWidgets.QComboBox()
        for label, value in PrinterInfo.STOP_BITS_MAP.items():
            self.stopBitsComboBox.addItem(label, value)

        self.flowControlComboBox = QtWidgets.QComboBox()
        for label, value in PrinterInfo.FLOW_CONTROL_MAP.items():
            self.flowControlComboBox.addItem(label, value)

        self.testButton = QtWidgets.QPushButton('Test')
        self.testButton.clicked.connect(self.test)

        self.columnCountSpinBox = QtWidgets.QSpinBox()
        self.columnCountSpinBox.setMinimum(2)
        self.columnCountSpinBox.setMaximum(20)

        self.rowCountSpinBox = QtWidgets.QSpinBox()
        self.rowCountSpinBox.setMinimum(2)
        self.rowCountSpinBox.setMaximum(20)

        self.grid = WizardGrid.Grid('Manual Test Points')
        self.grid.cellClicked.connect(self.configureManualProbePoint)

    def _layoutWidgets(self):
        portLayout = QtWidgets.QHBoxLayout()
        portLayout.addWidget(QtWidgets.QLabel('Port:'))
        portLayout.addWidget(self.portComboBox)
        portLayout.addStretch()
        portLayout.addWidget(self.defaultsButton)
        portLayout.addWidget(self.homeButton)

        displayNameLayout = QtWidgets.QHBoxLayout()
        displayNameLayout.addWidget(QtWidgets.QLabel('Display Name:'))
        displayNameLayout.addWidget(self.displayNameLineEdit)

        testLayout = QtWidgets.QHBoxLayout()
        testLayout.addStretch()
        testLayout.addWidget(self.testButton)
        testLayout.addStretch()

        connectionLayout = QtWidgets.QFormLayout()
        connectionLayout.addRow('G-code:' , self.gCodeFlavorComboBox)
        connectionLayout.addRow('Baud Rate:', self.baudRateComboBox)
        connectionLayout.addRow('Data Bits:', self.dataBitsComboBox)
        connectionLayout.addRow('Parity:', self.parityComboBox)
        connectionLayout.addRow('Stop Bits:', self.stopBitsComboBox)
        connectionLayout.addRow('Flow Control:', self.flowControlComboBox)
        connectionLayout.addRow(testLayout)

        connectionGroupBox = QtWidgets.QGroupBox('Connection')
        connectionGroupBox.setLayout(connectionLayout)

        meshLayout = QtWidgets.QFormLayout()
        meshLayout.addRow('Cols:', self.columnCountSpinBox)
        meshLayout.addRow('Rows:', self.rowCountSpinBox)

        meshGroupBox = QtWidgets.QGroupBox('Mesh')
        meshGroupBox.setLayout(meshLayout)

        groupBoxLayout = QtWidgets.QHBoxLayout()
        groupBoxLayout.addWidget(connectionGroupBox)
        groupBoxLayout.addWidget(meshGroupBox)

        printerInfoLayout = QtWidgets.QVBoxLayout()
        printerInfoLayout.addLayout(displayNameLayout)
        printerInfoLayout.addLayout(groupBoxLayout)
        printerInfoLayout.addWidget(self.grid)

        printerInfoGroupBox = QtWidgets.QGroupBox('Printer Info')
        printerInfoGroupBox.setLayout(printerInfoLayout)

        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(portLayout)
        layout.addWidget(printerInfoGroupBox)


        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def _createMenus(self):
        # File menu
        self.fileMenu = QtWidgets.QMenu('File', self)
        self.openAction = QtGui.QAction('Open', self)
        self.openAction.setStatusTip('Open a printer info file')
        self.openAction.triggered.connect(self.openFile)
        self.fileMenu.addAction(self.openAction)
        self.saveAsAction = QtGui.QAction('Save as', self)
        self.saveAsAction.setStatusTip('Save printer info to a new file')
        self.saveAsAction.triggered.connect(self.saveAsFile)
        self.fileMenu.addAction(self.saveAsAction)
        self.exitAction = QtGui.QAction('Exit', self)
        self.exitAction.setStatusTip('Exit the application') # TODO: Handle getting opened as a dialog
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

        self.helpMenu = QtWidgets.QMenu('Help', self)
        self.aboutAction = QtGui.QAction('About', self)
        self.aboutAction.triggered.connect(lambda : self.dialogs['about'].exec())
        self.helpMenu.addAction(self.aboutAction)
        self.aboutQtAction = QtGui.QAction('About Qt', self)
        self.aboutQtAction.triggered.connect(qApp.aboutQt)
        self.helpMenu.addAction(self.aboutQtAction)
        self.menuBar().addMenu(self.helpMenu)

    def _createDialogs(self):
        self.dialogs = {'about': AboutDialog('A utility for creating and editing printer infos.')} # TODO: Handle getting opened as a dialog

    def loadDefaults(self):
        self.setPrinterInfo(PrinterInfo.PrinterInfo())

    def saveAsFile(self):
        if len(self.displayNameLineEdit.text()) <= 0:
            self.warning('Display name can not be empty.')
            return

        filePath = QtWidgets.QFileDialog.getSaveFileName(self,
                                                         'Select new printer info file',
                                                         None,
                                                         PrinterInfo.PRINTER_INFO_FILE_FILTER)[0]
        if len(filePath) <= 0:
            return
        filePath = pathlib.Path(filePath)

        with open(filePath, 'w', newline='') as file:
            json.dump(self.currentPrinterInfo().asJson(), file, indent=4)

    def openFile(self):
        filePath = QtWidgets.QFileDialog.getOpenFileName(self,
                                                         'Open printer info',
                                                         None,
                                                         PrinterInfo.PRINTER_INFO_FILE_FILTER)[0]
        if len(filePath) > 0:
            self.loadPrinterInfo(filePath)

    def loadPrinterInfo(self, filePath):
        printerInfo = PrinterInfo.PrinterInfo()
        if filePath is not None:
            printerInfo.load(filePath)

        self.setPrinterInfo(printerInfo)

    def setPrinterInfo(self, loadedPrinterInfo):
        def setComboBox(comboBox, value):
            index = comboBox.findData(value)
            if value == -1:
                raise ValueError()

            comboBox.setCurrentIndex(index)

        self.loadedPrinterInfo = loadedPrinterInfo

        self.displayNameLineEdit.setText(self.loadedPrinterInfo.displayName)
        setComboBox(self.gCodeFlavorComboBox, self.loadedPrinterInfo.connection.gCodeFlavor)
        setComboBox(self.baudRateComboBox, self.loadedPrinterInfo.connection.baudRate)
        setComboBox(self.dataBitsComboBox, self.loadedPrinterInfo.connection.dataBits)
        setComboBox(self.parityComboBox, self.loadedPrinterInfo.connection.parity)
        setComboBox(self.stopBitsComboBox, self.loadedPrinterInfo.connection.stopBits)
        setComboBox(self.flowControlComboBox, self.loadedPrinterInfo.connection.flowControl)
        self.columnCountSpinBox.setValue(self.loadedPrinterInfo.mesh.columnCount)
        self.rowCountSpinBox.setValue(self.loadedPrinterInfo.mesh.rowCount)

        self.grid.clear()
        for point in self.loadedPrinterInfo.manualProbePoints:
            self.grid.setPoint(point)

    def test(self):
        testConnectionDialog = TestConnectionDialog(self.portComboBox.currentText(),
                                                    self.currentPrinterInfo())
        testConnectionDialog.exec()

    def home(self):
        dialog = PerformHomingDialog(self.portComboBox.currentText(),
                                          self.currentPrinterInfo())
        dialog.exec()

    def configureManualProbePoint(self, gridProbePoint):
        dialog = ConfigureGridPointDialog(self.portComboBox.currentText(),
                                          self.currentPrinterInfo(),
                                          gridProbePoint)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self.grid.setPoint(dialog.point())

    def currentPrinterInfo(self):
        return PrinterInfo.PrinterInfo(self.displayNameLineEdit.text(),
                                       PrinterInfo.Connection(gCodeFlavor = self.gCodeFlavorComboBox.currentData(),
                                                              baudRate = self.baudRateComboBox.currentData(),
                                                              dataBits = self.dataBitsComboBox.currentData(),
                                                              parity = self.parityComboBox.currentData(),
                                                              stopBits = self.stopBitsComboBox.currentData(),
                                                              flowControl = self.flowControlComboBox.currentData()),
                                       PrinterInfo.Mesh(self.columnCountSpinBox.value(),
                                                        self.rowCountSpinBox.value()),
                                       self.grid.getPoints())

    def warning(self, message):
        QtWidgets.QMessageBox.warning(self, 'Warning', message)

if __name__ == '__main__':
    # Main only imports
    import sys

    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon((Common.baseDir() / 'Resources' / 'PrinterInfoWizard-128x128.png').as_posix()))
    QtCore.QCoreApplication.setApplicationName('Printer Info Wizard')
    QtCore.QCoreApplication.setApplicationVersion(Version.version())

    # Windows only, configure icon settings
    try:
        from ctypes import windll
        myappid = f'com.sandmmakers.printerinfowizard.{QtCore.QCoreApplication.setApplicationVersion}'
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except ImportError:
        pass

    printerInfoWizard = PrinterInfoWizard()

    printerInfoWizard.show()
    sys.exit(app.exec())
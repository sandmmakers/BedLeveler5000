#!/usr/bin/env python

from Common.Common import printersDir
from Common import PrinterInfo
from Common.PrinterInfo import ConnectionMode
from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets
from PySide6 import QtSerialPort
import enum
import pathlib
from typing import NamedTuple

class PrinterConnectWidget(QtWidgets.QWidget):
    printerChanged = QtCore.Signal(PrinterInfo._PrinterInfo)
    connectRequested = QtCore.Signal(PrinterInfo._PrinterInfo, str)
    disconnectRequested = QtCore.Signal(PrinterInfo._PrinterInfo, str)
    homeRequested = QtCore.Signal()

    class PrinterDetails(NamedTuple):
        path: pathlib.Path
        printerInfo: PrinterInfo._PrinterInfo

    class FieldType(enum.IntEnum):
        HOST = 0
        PORT = 1

    def __init__(self, *args, hasHomeButton=True, **kwargs):
        super().__init__(*args, **kwargs)

        self.hasHomeButton = hasHomeButton

        self._createWidgets()
        self._layoutWidgets()

        self.setDisconnected()

    def _createWidgets(self):
        self.printerComboBox = QtWidgets.QComboBox()
        self.printerComboBox.currentIndexChanged.connect(self._switchPrinter)

        self.stackedLabelWidget = QtWidgets.QStackedWidget()
        self.stackedLabelWidget.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.stackedLabelWidget.addWidget(QtWidgets.QLabel('Host:'))
        self.stackedLabelWidget.addWidget(QtWidgets.QLabel('Port:'))

        self.stackedWidget = QtWidgets.QStackedWidget()
        self.stackedWidget.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        # Connections are made in the setConnected and setDisconnected functions
        self.connectButton = QtWidgets.QPushButton('UNSET')

        if self.hasHomeButton:
            self.homeButton = QtWidgets.QPushButton('Home')
            self.homeButton.clicked.connect(self.homeRequested)

    def _layoutWidgets(self):
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(QtWidgets.QLabel('Printer:'))
        layout.addWidget(self.printerComboBox)
        layout.addWidget(self.stackedLabelWidget)
        layout.addWidget(self.stackedWidget)
        layout.addWidget(self.connectButton)
        layout.addStretch()

        if self.hasHomeButton:
            layout.addWidget(self.homeButton)

        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def _switchPrinter(self):
        self._updateFieldTypeLabel()
        self.stackedWidget.setCurrentIndex(self.printerComboBox.currentIndex())
        self.printerChanged.emit(self.printerComboBox.currentData().printerInfo)

    def printerCount(self):
        return self.printerComboBox.count()

    def _updateFieldTypeLabel(self):
        if self.connectionMode() == ConnectionMode.MARLIN_2:
            fieldType = self.FieldType.PORT
        elif self.connectionMode() == ConnectionMode.MOONRAKER:
            fieldType = self.FieldType.HOST

        self.stackedLabelWidget.setCurrentIndex(fieldType)

    def setBusy(self):
        self.printerComboBox.setEnabled(False)
        self.stackedWidget.setEnabled(False)

        try:
            self.connectButton.clicked.disconnect()
        except RuntimeError:
            pass
        self.connectButton.setText('Disconnect')
        self.connectButton.clicked.connect(lambda: self._requestConnectionChange(False))

        if self.hasHomeButton:
            self.homeButton.setEnabled(False)

    def setConnected(self):
        self.setBusy()

        if self.hasHomeButton:
            self.homeButton.setEnabled(True)

    def setDisconnected(self):
        self.printerComboBox.setEnabled(True)
        self.stackedWidget.setEnabled(True)

        try:
            self.connectButton.clicked.disconnect()
        except RuntimeError:
            pass
        self.connectButton.setText('Connect')
        self.connectButton.clicked.connect(lambda: self._requestConnectionChange(True))

        if self.hasHomeButton:
            self.homeButton.setEnabled(False)

    def _requestConnectionChange(self, connect):
        printerInfo = self.printerComboBox.currentData().printerInfo
        specific = self._currentSpecific()

        if connect:
            self.connectRequested.emit(printerInfo, specific)
        else:
            self.disconnectRequested.emit(printerInfo, specific)

    def loadPrinters(self, printersDir, desiredPrinter=None, desiredPort=None, desiredHost=None, onlyConnectionModes=None):
        """ Calls enumeratePorts."""

        # Verify argument requirements
        assert (desiredPrinter is not None) or (desiredPort is None and desiredHost is None)

        # Verify there are no connected printers
        assert(self.printerComboBox.isEnabled())

        # Disable printer changed signal
        self.printerComboBox.blockSignals(True)

        # Record previous values
        previousMap = {}
        previousSelectedPrinterDetails = None if self.printerCount() == 0 else self.printerComboBox.currentData()
        previousSelectedSpecific = None if self.printerCount() == 0 else self._currentSpecific()
        for printerIndex in range(self.printerCount()):
            printerDetails = self.printerComboBox.itemData(printerIndex)
            if printerDetails.printerInfo.connectionMode == ConnectionMode.MARLIN_2:
                specific = self.stackedWidget.widget(printerIndex).getCurrentText()
            elif printerDetails.printerInfo.connectionMode == ConnectionMode.MOONRAKER:
                specific = self.stackedWidget.widget(printerIndex).text()

            previousMap[printerDetails.path] = (printerDetails, specific)

        # Remove previous printers and widgets
        self.printerComboBox.clear()
        while self.stackedWidget.count() > 0:
            widget = self.stackedWidget.widget(0)
            self.stackedWidget.removeWidget(widget)
            widget.setParent(None)
            widget.deleteLater()

        # Load each detected PrinterInfo
        for filePath in printersDir.glob('**/*.json'):
            printerInfo = PrinterInfo.fromFile(filePath)
            if onlyConnectionModes is not None and printerInfo.connectionMode not in onlyConnectionModes:
                continue

            # Add to the printer combo box
            self.printerComboBox.addItem(printerInfo.displayName, self.PrinterDetails(filePath, printerInfo))

            # Add to the stacked widget
            if printerInfo.connectionMode == ConnectionMode.MARLIN_2:
                self.stackedWidget.addWidget(QtWidgets.QComboBox())
            elif printerInfo.connectionMode == ConnectionMode.MOONRAKER:
                self.stackedWidget.addWidget(QtWidgets.QLineEdit())
            else:
                raise IOError('Detected an unsupported printer type.')

        # Verify at least one printer was found
        if self.printerComboBox.count() <= 0:
            raise IOError('No printers found.')

        self.enumeratePorts()

        # Restore previous values and selections, plus find desired printer
        desiredPrinterIndex = None
        for printerIndex in range(self.printerCount()):
            printerDetails = self.printerComboBox.itemData(printerIndex)
            previous = previousMap.get(printerDetails.path, None)

            if desiredPrinter == printerDetails.printerInfo.displayName:
                desiredPrinterIndex = printerIndex

            if previous is not None:
                previousPrinterInfo = previous[0]
                previousSpecific = previous[1]

                # Test if the previously selected printer is still present
                if printerDetails.path == previousSelectedPrinterDetails.path and printerDetails.printerInfo == previousPrinterInfo:
                    self.printerComboBox.setCurrentIndex(printerIndex)
                    self.stackedWidget.setCurrentIndex(printerIndex)

                # Restore previous instance specific values
                if previousPrinterInfo.connectionMode == printerDetails.printerInfo.connectionMode:
                    self._setCurrentSpecific(previousSpecific)

        # If there is a desired printer, ensure it was found
        if desiredPrinter is not None and desiredPrinterIndex is None:
            raise IOError(f'Failed to find desired printer \'{desiredPrinter}\'.')

        # Set desired printer and values
        if desiredPrinterIndex is not None:
            self.printerComboBox.setCurrentIndex(desiredPrinterIndex)
            self.stackedWidget.setCurrentIndex(desiredPrinterIndex)
            printerInfo = self.printerComboBox.currentData().printerInfo

            if printerInfo.connectionMode == ConnectionMode.MARLIN_2 and desiredPort is not None:
                self._setCurrentSpecific(desiredPort)
            elif printerInfo.connectionMode == ConnectionMode.MOONRAKER and desiredHost is not None:
                self._setCurrentSpecific(desiredHost)

        # Update field type label
        self._updateFieldTypeLabel()

        # Restore printer changed signal
        self.printerComboBox.blockSignals(False)

        # Signal printer changed
        if previousSelectedPrinterDetails != self.printerComboBox.currentData() or \
           previousSelectedSpecific != self._currentSpecific():
            self.printerChanged.emit(self.printerComboBox.currentData().printerInfo)

    def enumeratePorts(self):
        serialPortInfoList = QtSerialPort.QSerialPortInfo.availablePorts()

        for printerIndex in range(self.printerComboBox.count()):
            if self.connectionMode(printerIndex) == ConnectionMode.MARLIN_2:
                comboBox = self.stackedWidget.widget(printerIndex)
                previous = comboBox.currentText()

                comboBox.clear()
                for serialPortInfo in serialPortInfoList:
                    comboBox.addItem(serialPortInfo.portName())
                comboBox.setCurrentText(previous)

    def printerInfo(self, index=None):
        index = self.printerComboBox.currentIndex() if index is None else index
        return self.printerComboBox.itemData(index).printerInfo

    def connectionMode(self, index=None):
        return self.printerInfo(index).connectionMode

    def host(self):
        assert(self.connectionMode() == ConnectionMode.MOONRAKER)
        return self._currentSpecific()

    def port(self):
        assert(self.connectionMode() == ConnectionMode.MARLIN_2)
        return self._currentSpecific()

    def _currentSpecific(self):
        specificWidget = self.stackedWidget.currentWidget()
        if isinstance(specificWidget, QtWidgets.QComboBox):
            return specificWidget.currentText()
        elif isinstance(specificWidget, QtWidgets.QLineEdit):
            return specificWidget.text()
        else:
            raise RuntimeError('Tried to get specific value from missing or unsupported widget type.')

    def _setCurrentSpecific(self, value):
        specificWidget = self.stackedWidget.currentWidget()
        if isinstance(specificWidget, QtWidgets.QComboBox):
            index = specificWidget.findText(value)
            if index == -1:
                raise ValueError('Port not available.')
            specificWidget.setCurrentIndex(index)
        elif isinstance(specificWidget, QtWidgets.QLineEdit):
            specificWidget.setText(value)
        else:
            raise RuntimeError('Tried to set specific value of missing or unsupported widget type.')

if __name__ == '__main__':
    # Main only imports
    import pathlib
    import sys

    class MainWindow(QtWidgets.QMainWindow):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self._createWidgets()
            self._layoutWidgets()

        def _createWidgets(self):
            self.withHomePrinterConnectWidget = PrinterConnectWidget()
            self.withHomePrinterConnectWidget.printerChanged.connect(lambda: print('withHomePrinterConnectWidget.printerChanged'))
            self.withHomePrinterConnectWidget.connectRequested.connect(self.withHomePrinterConnectWidget.setBusy)
            self.withHomePrinterConnectWidget.disconnectRequested.connect(self.withHomePrinterConnectWidget.setDisconnected)
            self.withHomePrinterConnectWidget.loadPrinters(printersDir())

            self.withoutHomePrinterConnectWidget = PrinterConnectWidget()
            self.withoutHomePrinterConnectWidget.printerChanged.connect(lambda: print('withoutHomePrinterConnectWidget.printerChanged'))
            self.withoutHomePrinterConnectWidget.connectRequested.connect(self.withoutHomePrinterConnectWidget.setBusy)
            self.withoutHomePrinterConnectWidget.disconnectRequested.connect(self.withoutHomePrinterConnectWidget.setDisconnected)
            self.withoutHomePrinterConnectWidget.loadPrinters(printersDir())

            self.connectedButton = QtWidgets.QPushButton('Connected')
            self.connectedButton.clicked.connect(self.connected)

            self.enumeratePortsButton = QtWidgets.QPushButton('Enumerate Ports')
            self.enumeratePortsButton.clicked.connect(self.enumeratePorts)

        def _layoutWidgets(self):
            withLayout = QtWidgets.QHBoxLayout()
            withLayout.setContentsMargins(0, 0, 0, 0)
            withLayout.addWidget(self.withHomePrinterConnectWidget)
            withGroupBox = QtWidgets.QGroupBox('With')
            withGroupBox.setLayout(withLayout)

            withoutLayout = QtWidgets.QHBoxLayout()
            withoutLayout.setContentsMargins(0, 0, 0, 0)
            withoutLayout.addWidget(self.withoutHomePrinterConnectWidget)
            withoutGroupBox = QtWidgets.QGroupBox('Without')
            withoutGroupBox.setLayout(withoutLayout)

            controlsLayout = QtWidgets.QHBoxLayout()
            controlsLayout.addStretch()
            controlsLayout.addWidget(self.connectedButton)
            controlsLayout.addWidget(self.enumeratePortsButton)
            controlsLayout.addStretch()

            layout = QtWidgets.QVBoxLayout()
            layout.addWidget(withGroupBox)
            layout.addWidget(withoutGroupBox)
            layout.addLayout(controlsLayout)

            widget = QtWidgets.QWidget()
            widget.setLayout(layout)
            self.setCentralWidget(widget)

        def connected(self):
            self.withHomePrinterConnectWidget.setConnected()
            self.withoutHomePrinterConnectWidget.setConnected()

        def enumeratePorts(self):
            self.withHomePrinterConnectWidget.enumeratePorts()
            self.withoutHomePrinterConnectWidget.enumeratePorts()


    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())
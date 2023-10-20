#!/usr/bin/env python

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets
from PySide6 import QtSerialPort

class PortComboBox(QtWidgets.QComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.enumeratePorts()

    def enumeratePorts(self):
        current = self.currentText()
        self.clear()
        serialPortInfoList = QtSerialPort.QSerialPortInfo.availablePorts()
        for serialPortInfo in serialPortInfoList:
            self.addItem(serialPortInfo.portName())
        self.setCurrentText(current)

    def setPort(self, port):
        portIndex = self.portComboBox.findText(port)
        if portIndex == -1:
            raise ValueError('Failed to find requested port.')
        self.portComboBox.setCurrentIndex(portIndex)

    def printerInfo(self):
        return self.currentData()

if __name__ == '__main__':
    # Main only imports
    import sys

    app = QtWidgets.QApplication(sys.argv)

    portComboBox = PortComboBox()
    portComboBox.show()
    sys.exit(app.exec())
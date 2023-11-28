#!/usr/bin/env python

from Common.PrinterInfo import CONNECTION_MODE_MAP
from Common.PrinterInfo import BAUD_RATE_MAP
from Common.PrinterInfo import DATA_BITS_MAP
from Common.PrinterInfo import PARITY_MAP
from Common.PrinterInfo import STOP_BITS_MAP
from Common.PrinterInfo import FLOW_CONTROL_MAP
from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

class SerialWidget(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.__createWidgets()
        self.__layoutWidgets()
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

    def __createWidgets(self):
        self.baudRateComboBox = QtWidgets.QComboBox()
        for label, value in BAUD_RATE_MAP.items():
            self.baudRateComboBox.addItem(label, value)

        self.dataBitsComboBox = QtWidgets.QComboBox()
        for label, value in DATA_BITS_MAP.items():
            self.dataBitsComboBox.addItem(label, value)

        self.parityComboBox = QtWidgets.QComboBox()
        for label, value in PARITY_MAP.items():
            self.parityComboBox.addItem(label, value)

        self.stopBitsComboBox = QtWidgets.QComboBox()
        for label, value in STOP_BITS_MAP.items():
            self.stopBitsComboBox.addItem(label, value)

        self.flowControlComboBox = QtWidgets.QComboBox()
        for label, value in FLOW_CONTROL_MAP.items():
            self.flowControlComboBox.addItem(label, value)

    def __layoutWidgets(self):
        layout = QtWidgets.QFormLayout()
        layout.addRow('Baud Rate:', self.baudRateComboBox)
        layout.addRow('Data Bits:', self.dataBitsComboBox)
        layout.addRow('Parity:', self.parityComboBox)
        layout.addRow('Stop Bits:', self.stopBitsComboBox)
        layout.addRow('Flow Control:', self.flowControlComboBox)

        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    @staticmethod
    def __setComboBox(comboBox, value):
        index = comboBox.findData(value)
        if value == -1:
            raise ValueError()

        comboBox.setCurrentIndex(index)

    def baudRate(self):
        return self.baudRateComboBox.currentData()

    def setBaudRate(self, value):
        self.__setComboBox(self.baudRateComboBox, value)

    def dataBits(self):
        return self.dataBitsComboBox.currentData()

    def setDataBits(self, value):
        self.__setComboBox(self.dataBitsComboBox, value)

    def parity(self):
        return self.parityComboBox.currentData()

    def setParity(self, value):
        self.__setComboBox(self.parityComboBox, value)

    def stopBits(self):
        return self.stopBitsComboBox.currentData()

    def setStopBits(self, value):
        self.__setComboBox(self.stopBitsComboBox, value)

    def flowControl(self):
        return self.flowControlComboBox.currentData()

    def setFlowControl(self, value):
        self.__setComboBox(self.flowControlComboBox, value)
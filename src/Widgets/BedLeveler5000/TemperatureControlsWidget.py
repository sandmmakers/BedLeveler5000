#!/usr/bin/env python

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

class TemperatureControlsWidget(QtWidgets.QWidget):
    bedHeaterChanged = QtCore.Signal(bool, float)
    nozzleHeaterChanged = QtCore.Signal(bool, float)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__createWidgets()
        self.__layoutWidgets()
        self.resetButtons()

    def __createWidgets(self):
        # Bed widgets
        self.bedTempSpinBox = QtWidgets.QDoubleSpinBox()
        self.bedTempSpinBox.setMaximum(200)
        self.bedTempSpinBox.valueChanged.connect(self._requestBedHeaterChange)
        self.bedHeaterOnButton = QtWidgets.QRadioButton('On')
        self.bedHeaterOnButton.toggled.connect(self._requestBedHeaterChange)
        self.bedHeaterOffButton = QtWidgets.QRadioButton('Off')

        # Bed button group
        self.bedHeaterButtonGroup = QtWidgets.QButtonGroup()
        self.bedHeaterButtonGroup.addButton(self.bedHeaterOnButton)
        self.bedHeaterButtonGroup.addButton(self.bedHeaterOffButton)

        # Nozzle widgets
        self.nozzleTempSpinBox = QtWidgets.QDoubleSpinBox()
        self.nozzleTempSpinBox.setMaximum(500)
        self.nozzleTempSpinBox.valueChanged.connect(self._requestNozzleHeaterChange)
        self.nozzleHeaterOnButton = QtWidgets.QRadioButton('On')
        self.nozzleHeaterOnButton.toggled.connect(self._requestNozzleHeaterChange)
        self.nozzleHeaterOffButton = QtWidgets.QRadioButton('Off')

        # Nozzle button group
        self.nozzleHeaterButtonGroup = QtWidgets.QButtonGroup()
        self.nozzleHeaterButtonGroup.addButton(self.nozzleHeaterOnButton)
        self.nozzleHeaterButtonGroup.addButton(self.nozzleHeaterOffButton)

    def __layoutWidgets(self):
        groupBoxLayout = QtWidgets.QGridLayout()
        groupBoxLayout.addWidget(QtWidgets.QLabel('Desired Bed Temp (\x00\xB0C):'), 0, 0)
        groupBoxLayout.addWidget(self.bedTempSpinBox, 0, 1)
        groupBoxLayout.addWidget(QtWidgets.QLabel('State:'), 0, 2)
        groupBoxLayout.addWidget(self.bedHeaterOnButton, 0, 3)
        groupBoxLayout.addWidget(self.bedHeaterOffButton, 0, 4)
        groupBoxLayout.addWidget(QtWidgets.QLabel(f'Desired Nozzle Temp (\x00\xB0C):'), 1, 0)
        groupBoxLayout.addWidget(self.nozzleTempSpinBox, 1, 1)
        groupBoxLayout.addWidget(QtWidgets.QLabel('State:'), 1, 2)
        groupBoxLayout.addWidget(self.nozzleHeaterOnButton, 1, 3)
        groupBoxLayout.addWidget(self.nozzleHeaterOffButton, 1, 4)
        groupBoxLayout.setColumnStretch(4, 100)
        groupBox = QtWidgets.QGroupBox('Temperature')
        groupBox.setLayout(groupBoxLayout)

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(groupBox)
        self.setLayout(layout)

    def resetButtons(self):
        self.nozzleHeaterOffButton.setChecked(True)
        self.bedHeaterOffButton.setChecked(True)

    def _requestBedHeaterChange(self):
        self.bedHeaterChanged.emit(self.bedHeaterOnButton.isChecked(),
                                   self.bedTempSpinBox.value())

    def _requestNozzleHeaterChange(self):
        self.nozzleHeaterChanged.emit(self.nozzleHeaterOnButton.isChecked(),
                                      self.nozzleTempSpinBox.value())

if __name__ == '__main__':
    # Main only imports
    import sys

    app = QtWidgets.QApplication(sys.argv)
    widget = QtWidgets.QWidget()

    # Create test TemperatureControlsWidget
    temperatureControlsWidget = TemperatureControlsWidget()
    temperatureControlsWidget.bedHeaterChanged.connect(lambda state, temp: print(f'Bed heater: {state} - {temp}'))
    temperatureControlsWidget.nozzleHeaterChanged.connect(lambda state, temp: print(f'Nozzle heater: {state} - {temp}'))

    # Layout widgets
    layout = QtWidgets.QVBoxLayout()
    layout.addWidget(temperatureControlsWidget)
    widget.setLayout(layout)

    widget.show()
    sys.exit(app.exec())
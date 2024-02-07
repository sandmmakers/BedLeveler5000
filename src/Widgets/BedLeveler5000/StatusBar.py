#!/usr/bin/env python

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

class StatusBar(QtWidgets.QStatusBar):
    class TempWidget(QtWidgets.QWidget):
        def __init__(self, name, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.nameLabel = QtWidgets.QLabel(f'{name}: ')
            font = self.nameLabel.font()
            font.setBold(True)
            self.nameLabel.setFont(font)

            self.tempLabel = QtWidgets.QLabel()
            self.tempLabel.setFixedWidth(self.tempLabel.fontMetrics().horizontalAdvance('XXX.X'))
            self.tempLabel.setToolTip('Current Temperature')

            self.desiredLabel = QtWidgets.QLabel()
            self.desiredLabel.setFixedWidth(self.desiredLabel.fontMetrics().horizontalAdvance('(XXX.X)'))
            self.desiredLabel.setToolTip('Desired Temperature')

            self.powerLabel = QtWidgets.QLabel()
            self.powerLabel.setFixedWidth(self.powerLabel.fontMetrics().horizontalAdvance('(XXX.X%)'))
            self.powerLabel.setToolTip('Power')

            layout = QtWidgets.QHBoxLayout()
            layout.setSpacing(0)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self.nameLabel)
            layout.addWidget(self.tempLabel)
            layout.addWidget(self.desiredLabel)
            layout.addWidget(self.powerLabel)
            self.setLayout(layout)

        def setTemp(self, temp):
            self.tempLabel.setText(f'{temp:>.1f}')

        def setDesired(self, temp):
            self.desiredLabel.setText(f'({temp:>.1f})')

        def setPower(self, power):
            self.powerLabel.setText(f'[{100.0*power:>.1f}%]')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bedTempWidget = self.TempWidget('Bed')
        self.bedTempWidget.setToolTip('Current bed temperature')
        self.addPermanentWidget(self.bedTempWidget)

        self.nozzleTempWidget = self.TempWidget('Noz')
        self.nozzleTempWidget.setToolTip('Current nozzle temperature')
        self.addPermanentWidget(self.nozzleTempWidget)

    def setState(self, state):
        self.showMessage(state)

    def setBedTemp(self, *, actual, desired, power):
        self.bedTempWidget.setTemp(actual)
        self.bedTempWidget.setDesired(desired)
        self.bedTempWidget.setPower(power)

    def setNozzleTemp(self, *, actual, desired, power):
        self.nozzleTempWidget.setTemp(actual)
        self.nozzleTempWidget.setDesired(desired)
        self.nozzleTempWidget.setPower(power)

if __name__ == '__main__':
    # Main only imports
    import sys

    app = QtWidgets.QApplication(sys.argv)
    QtCore.QCoreApplication.setApplicationName('StatusBar Test App')

    # QMainWindow
    mainWindow = QtWidgets.QMainWindow()

    # Create test StatusBar
    statusBar = StatusBar()
    mainWindow.setStatusBar(statusBar)

    # Testing widgets
    bedSpinBox = QtWidgets.QDoubleSpinBox()
    bedSpinBox.setMaximum(999)
    bedSpinBox.valueChanged.connect(lambda _: statusBar.setBedTemp(actual = bedSpinBox.value(),
                                                                   desired = bedDesiredSpinBox.value(),
                                                                   power = bedPowerSpinBox.value()))
    bedDesiredSpinBox = QtWidgets.QDoubleSpinBox()
    bedDesiredSpinBox.setMaximum(999)
    bedDesiredSpinBox.valueChanged.connect(lambda _: statusBar.setBedTemp(actual = bedSpinBox.value(),
                                                                          desired = bedDesiredSpinBox.value(),
                                                                          power = bedPowerSpinBox.value()))
    bedPowerSpinBox = QtWidgets.QDoubleSpinBox()
    bedPowerSpinBox.setMaximum(100.0)
    bedPowerSpinBox.valueChanged.connect(lambda _: statusBar.setBedTemp(actual = bedSpinBox.value(),
                                                                        desired = bedDesiredSpinBox.value(),
                                                                        power = bedPowerSpinBox.value()))

    nozzleSpinBox = QtWidgets.QDoubleSpinBox()
    nozzleSpinBox.setMaximum(999)
    nozzleSpinBox.valueChanged.connect(lambda _: statusBar.setNozzleTemp(actual = nozzleSpinBox.value(),
                                                                         desired = nozzleDesiredSpinBox.value(),
                                                                         power = nozzlePowerSpinBox.value()))
    nozzleDesiredSpinBox = QtWidgets.QDoubleSpinBox()
    nozzleDesiredSpinBox.setMaximum(999)
    nozzleDesiredSpinBox.valueChanged.connect(lambda _: statusBar.setNozzleTemp(actual = nozzleSpinBox.value(),
                                                                                desired = nozzleDesiredSpinBox.value(),
                                                                                power = nozzlePowerSpinBox.value()))
    nozzlePowerSpinBox = QtWidgets.QDoubleSpinBox()
    nozzlePowerSpinBox.setMaximum(100.0)
    nozzlePowerSpinBox.valueChanged.connect(lambda _: statusBar.setNozzleTemp(actual = nozzleSpinBox.value(),
                                                                              desired = nozzleDesiredSpinBox.value(),
                                                                              power = nozzlePowerSpinBox.value()))

    # Layout widgets
    layout = QtWidgets.QFormLayout()
    layout.addRow('Bed Temp:', bedSpinBox)
    layout.addRow('Bed Desired Temp:', bedDesiredSpinBox)
    layout.addRow('Bed Power:', bedPowerSpinBox)
    layout.addRow('Nozzle Temp:', nozzleSpinBox)
    layout.addRow('Nozzle Desired Temp:', nozzleDesiredSpinBox)
    layout.addRow('Nozzle Power:', nozzlePowerSpinBox)
    widget = QtWidgets.QWidget()
    widget.setLayout(layout)

    mainWindow.setCentralWidget(widget)

    mainWindow.show()
    sys.exit(app.exec())
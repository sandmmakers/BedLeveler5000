from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

class StatusBar(QtWidgets.QStatusBar):
    test = QtCore.Signal(QtCore.QPointF)

    class TempWidget(QtWidgets.QWidget):
        def __init__(self, name, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.nameLabel = QtWidgets.QLabel(f'{name}: ')
            self.tempLabel = QtWidgets.QLabel()
            self.tempLabel.setFixedWidth(self.tempLabel.fontMetrics().horizontalAdvance('XXX.X'))
            self.desiredLabel = QtWidgets.QLabel()
            self.desiredLabel.setFixedWidth(self.desiredLabel.fontMetrics().horizontalAdvance('(XXX.X)'))

            layout = QtWidgets.QHBoxLayout()
            layout.setSpacing(0)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self.nameLabel)
            layout.addWidget(self.tempLabel)
            layout.addWidget(self.desiredLabel)
            self.setLayout(layout)

        def setTemp(self, temp):
            self.tempLabel.setText(f'{temp:>.1f}')

        def setDesired(self, temp):
            self.desiredLabel.setText(f'({temp:>.1f})')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bedTempWidget = self.TempWidget('Bed')
        self.bedTempWidget.setToolTip('Current bed temperature')
        self.addPermanentWidget(self.bedTempWidget)

        self.nozzleTempWidget = self.TempWidget('Noz: ')
        self.nozzleTempWidget.setToolTip('Current nozzle temperature')
        self.addPermanentWidget(self.nozzleTempWidget)

    def setState(self, state):
        self.showMessage(state)

    def setBedTemp(self, actual, desired):
        self.bedTempWidget.setTemp(actual)
        self.bedTempWidget.setDesired(desired)

    def setNozzleTemp(self, actual, desired):
        self.nozzleTempWidget.setTemp(actual)
        self.nozzleTempWidget.setDesired(desired)

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
    bedDesiredSpinBox = QtWidgets.QDoubleSpinBox()
    bedDesiredSpinBox.setMaximum(999)
    bedSpinBox.valueChanged.connect(lambda _: statusBar.setBedTemp(bedSpinBox.value(), bedDesiredSpinBox.value()))
    bedDesiredSpinBox.valueChanged.connect(lambda _: statusBar.setBedTemp(bedSpinBox.value(), bedDesiredSpinBox.value()))

    nozzleSpinBox = QtWidgets.QDoubleSpinBox()
    nozzleSpinBox.setMaximum(999)
    nozzleDesiredSpinBox = QtWidgets.QDoubleSpinBox()
    nozzleDesiredSpinBox.setMaximum(999)
    nozzleSpinBox.valueChanged.connect(lambda _: statusBar.setNozzleTemp(nozzleSpinBox.value(), nozzleDesiredSpinBox.value()))
    nozzleDesiredSpinBox.valueChanged.connect(lambda _: statusBar.setNozzleTemp(nozzleSpinBox.value(), nozzleDesiredSpinBox.value()))

    # Layout widgets
    layout = QtWidgets.QFormLayout()
    layout.addRow('Bed Temp:', bedSpinBox)
    layout.addRow('Bed Desired Temp:', bedDesiredSpinBox)
    layout.addRow('Nozzle Temp:', nozzleSpinBox)
    layout.addRow('Nozzle Desired Temp:', nozzleDesiredSpinBox)
    widget = QtWidgets.QWidget()
    widget.setLayout(layout)

    mainWindow.setCentralWidget(widget)

    mainWindow.show()
    sys.exit(app.exec())
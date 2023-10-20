#!/usr/bin/env python

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

class ManualProbeButtonArea(QtWidgets.QMainWindow):
    probe = QtCore.Signal(str, float, float)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def configure(self, printerInfo):
        if self.centralWidget() is not None:
            self.centralWidget().deleteLater()

        # Create grid layout
        layout = QtWidgets.QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Create buttons
        for details in printerInfo.manualProbePoints:
            button = QtWidgets.QPushButton(details.name)
            point = QtCore.QPointF(details.x, details.y)
            button.clicked.connect(lambda name=details.name, x=point.x(), y=point.y(): self.probe.emit(name, x, y))
            layout.addWidget(button, details.row, details.column)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

if __name__ == '__main__':
    # Main only imports
    from PrinterInfo import PrinterInfo
    import sys

    # Read in the test printer descriptions
    printer1 = PrinterInfo.fromFile('Printers/ElegooNeptune3Plus.json')
    printer2 = PrinterInfo.fromFile('Printers/ElegooNeptune3Max.json')

    app = QtWidgets.QApplication(sys.argv)
    widget = QtWidgets.QWidget()

    def update():
        print(printerComboBox.currentData().manualProbePoints)
        manualProbeButtonArea.configure(printerComboBox.currentData())

    printerComboBox = QtWidgets.QComboBox()
    printerComboBox.addItem(printer1.displayName, printer1)
    printerComboBox.addItem(printer2.displayName, printer2)
    printerComboBox.currentIndexChanged.connect(lambda : update())

    # Create test ManualProbeButtonArea
    manualProbeButtonArea = ManualProbeButtonArea()
    manualProbeButtonArea.probe.connect(lambda id_, x, y : print(f'{id_} ({x}, {y})'))
    update()

    groupBoxLayout = QtWidgets.QHBoxLayout()
    groupBoxLayout.addWidget(manualProbeButtonArea)
    groupBox = QtWidgets.QGroupBox('Manual Probe Button Area')
    groupBox.setLayout(groupBoxLayout)

    # Layout widgets
    layout = QtWidgets.QVBoxLayout()
    layout.addWidget(printerComboBox)
    layout.addWidget(groupBox)
    widget.setLayout(layout)

    widget.show()
    sys.exit(app.exec())
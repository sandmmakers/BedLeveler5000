#!/usr/bin/env python3

from ManualProbeButtonArea import ManualProbeButtonArea
from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

class ManualWidget(QtWidgets.QWidget):
    probe = QtCore.Signal(str, float, float)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._createWidgets()
        self._layoutWidgets()

    def _createWidgets(self):
        # Test button area
        self.manualProbeButtonArea = ManualProbeButtonArea()
        self.manualProbeButtonArea.probe.connect(self.probe)

        # Log
        self.log = QtWidgets.QTextEdit()
        self.log.setReadOnly(True)

        self.clearButton = QtWidgets.QPushButton('Clear')
        self.clearButton.clicked.connect(lambda x: self.log.clear())

    def _layoutWidgets(self):
        buttonLayout = QtWidgets.QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.clearButton)
        buttonLayout.addStretch()

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.manualProbeButtonArea)
        layout.addWidget(self.log)
        layout.addLayout(buttonLayout)

        self.setLayout(layout)

    def reportProbe(self, id_, response):
        self.log.append(f'Probed {id_} ({response["bed"]["x"]}, {response["bed"]["y"]}): {response["bed"]["z"]} ({response["position"]["z"]})')

    def setPrinter(self, printer):
        self.manualProbeButtonArea.configure(printer)

if __name__ == '__main__':
    # Main only imports
    import sys
    import json

    def manualProbe(id_, x, y):
        print(f'{id_} ({x}, {y})')
        response = {'bed': {'x': x, 'y': y, 'z': 0.14}, 'position': {'count': {'x': 5293, 'y': 1243, 'z': 615}, 'e': 0.0, 'x': 66.0, 'y': 15.5, 'z': 1.54}}
        manualWidget.reportProbe(id_, response)

    # Read in the test printer description
    with open('Printers/ElegooNeptune3Max.json', 'r') as file:
        printer = json.load(file)

    app = QtWidgets.QApplication(sys.argv)
    widget = QtWidgets.QWidget()

    # Create test ManualWidget
    manualWidget = ManualWidget()
    manualWidget.setPrinter(printer)
    manualWidget.probe.connect(lambda id_, x, y : manualProbe(id_, x, y))

    # Layout widgets
    layout = QtWidgets.QVBoxLayout()
    layout.addWidget(manualWidget)
    widget.setLayout(layout)

    widget.show()
    sys.exit(app.exec())
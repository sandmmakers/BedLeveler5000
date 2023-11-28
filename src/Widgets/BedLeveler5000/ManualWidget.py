#!/usr/bin/env python

from Printers.CommandPrinter import ProbeResult
from .ManualProbeButtonArea import ManualProbeButtonArea
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
        self.log.append(f'Probed {id_} ({response.x}, {response.y}): {response.z:.3f}')

    def setPrinter(self, printerInfo):
        self.manualProbeButtonArea.configure(printerInfo)

if __name__ == '__main__':
    # Main only imports
    from Common import Common
    from Common import PrinterInfo
    import sys
    import json

    def manualProbe(id_, x, y):
        manualWidget.reportProbe(id_, ProbeResult(x=x, y=y, z=0.02))

    # Read in the test printer description
    printerInfo = PrinterInfo.fromFile(Common.baseDir() / 'Printers/ElegooNeptune3Max.json')

    app = QtWidgets.QApplication(sys.argv)
    widget = QtWidgets.QWidget()

    # Create test ManualWidget
    manualWidget = ManualWidget()
    manualWidget.setPrinter(printerInfo)
    manualWidget.probe.connect(lambda id_, x, y : manualProbe(id_, x, y))

    # Layout widgets
    layout = QtWidgets.QVBoxLayout()
    layout.addWidget(manualWidget)
    widget.setLayout(layout)

    widget.show()
    sys.exit(app.exec())
#!/usr/bin/env python3

from .NoButtonStatusDialog import NoButtonStatusDialog
from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

class ManualProbeDialog(NoButtonStatusDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setProbePoint(self, *, name, x, y):
        self.setText(f'Manually probing location {name} ({x}, {y}).')

if __name__ == '__main__':
    # Main only imports
    import sys

    app = QtWidgets.QApplication(sys.argv)

    manualProbeDialog = ManualProbeDialog()

    def probe():
        QtCore.QTimer.singleShot(3000, manualProbeDialog.accept)
        manualProbeDialog.setProbePoint(name='1',
                                        x=32,
                                        y=47.2)
        manualProbeDialog.show()

    probeButton = QtWidgets.QPushButton('Probe')
    probeButton.clicked.connect(probe)

    probeButton.show()
    sys.exit(app.exec())
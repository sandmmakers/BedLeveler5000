#!/usr/bin/env python

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets
import signal

# Enable CTRL-C killing the application
signal.signal(signal.SIGINT, signal.SIG_DFL)

class CancellableStatusDialog(QtWidgets.QMessageBox):
    def __init__(self, *args, text='UNSET', **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowTitleHint)
        self.setIcon(QtWidgets.QMessageBox.Information)
        self.setWindowTitle('Status')
        self.setText(text)
        self.setStandardButtons(QtWidgets.QMessageBox.Cancel)
        self.setModal(True)

if __name__ == '__main__':
    # Main only imports
    import sys

    app = QtWidgets.QApplication(sys.argv)

    cancellableStatusDialog = CancellableStatusDialog()
    cancellableStatusDialog.rejected.connect(lambda: print('cancel'))

    showButton = QtWidgets.QPushButton('Show')
    showButton.clicked.connect(lambda: cancellableStatusDialog.show())

    spinBox = QtWidgets.QSpinBox()

    timer = QtCore.QTimer()
    timer.setInterval(1000)
    timer.timeout.connect(lambda: spinBox.setValue(spinBox.value() + 1))
    timer.start()


    layout = QtWidgets.QVBoxLayout()
    layout.addWidget(spinBox)
    layout.addWidget(showButton)
    widget = QtWidgets.QWidget()
    widget.setLayout(layout)
    widget.show()

    try:
       sys.exit(app.exec())
    except KeyboardInterrupt:
        sys.exit(1)
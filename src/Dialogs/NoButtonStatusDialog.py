#!/usr/bin/env python

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

class NoButtonStatusDialog(QtWidgets.QMessageBox):
    def __init__(self, *args, text='UNSET', **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowTitleHint)
        self.setIcon(QtWidgets.QMessageBox.Information)
        self.setWindowTitle('Status')
        self.setText(text)
        self.setStandardButtons(QtWidgets.QMessageBox.NoButton)
        self.setModal(True)

if __name__ == '__main__':
    # Main only imports
    import sys

    app = QtWidgets.QApplication(sys.argv)

    dialog1 = NoButtonStatusDialog()
    dialog2 = NoButtonStatusDialog(text='two')

    def test():
        QtCore.QTimer.singleShot(3500, dialog1.accept)
        dialog1.show()
        print('Dialog 1 was opened.')
        QtCore.QTimer.singleShot(3500, dialog2.accept)
        dialog2.show()
        print('Dialog 2 was opened.')

    testButton = QtWidgets.QPushButton('Test')
    testButton.clicked.connect(test)

    testButton.show()
    sys.exit(app.exec())
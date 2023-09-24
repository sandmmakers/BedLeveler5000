#!/usr/bin/env python3

from PySide6 import QtWidgets
import sys

def FatalErrorDialog(parent, message, errorCode=1):
    """ Open an application modal fatal error dialog. This dialog will quit the entire application on close. """
    QtWidgets.QMessageBox.critical(parent, 'Fatal Error', message)
    sys.exit(errorCode)

if __name__ == '__main__':
    # Main only imports
    from PySide6 import QtCore
    import sys

    app = QtWidgets.QApplication(sys.argv)
    QtCore.QCoreApplication.setApplicationName('FatalErrorDialog TestApp')

    button = QtWidgets.QPushButton('Open')
    button.clicked.connect(lambda : FatalErrorDialog(button, 'Test'))

    button.show()
    app.exec()
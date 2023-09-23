from PySide6 import QtWidgets
import sys

def FatalErrorDialog(parent, message, errorCode=1):
    QtWidgets.QMessageBox.critical(parent, 'Fatal Error', message)
    sys.exit(errorCode)
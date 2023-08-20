from PySide6 import QtWidgets

def FatalErrorDialog(parent, message):
    QtWidgets.QMessageBox.critical(parent, 'Fatal Error', message)
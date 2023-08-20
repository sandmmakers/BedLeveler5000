from PySide6 import QtWidgets

def WarningDialog(parent, message):
    QtWidgets.QMessageBox.warning(parent, 'Warning', message)
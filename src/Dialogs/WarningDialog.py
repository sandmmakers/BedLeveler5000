from PySide6 import QtWidgets

def WarningDialog(parent, message):
    """ Open an application modal warning dialog. """
    QtWidgets.QMessageBox.warning(parent, 'Warning', message)

if __name__ == '__main__':
    # Main only imports
    from PySide6 import QtCore
    import sys

    app = QtWidgets.QApplication(sys.argv)
    QtCore.QCoreApplication.setApplicationName('WarningDialog TestApp')

    button = QtWidgets.QPushButton('Open')
    button.clicked.connect(lambda : WarningDialog(button, 'Test'))

    button.show()
    app.exec()
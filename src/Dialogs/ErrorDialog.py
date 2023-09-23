from PySide6 import QtWidgets

def ErrorDialog(parent, message):
    """ Open an application modal error dialog. """
    QtWidgets.QMessageBox.critical(parent, 'Error', message)

if __name__ == '__main__':
    # Main only imports
    from PySide6 import QtCore
    import sys

    app = QtWidgets.QApplication(sys.argv)
    QtCore.QCoreApplication.setApplicationName('ErrorDialog TestApp')

    button = QtWidgets.QPushButton('Open')
    button.clicked.connect(lambda : ErrorDialog(button, 'Test'))

    button.show()
    app.exec()
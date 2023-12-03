from Common import Common

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

import argparse
import platform
import pathlib
import sys
import os

class CommonArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, addPrinters=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.showDialog = platform.system() == 'Windows'
        self.errorColumnCount = 40
        self.helpColumnCount = 80

        self.add_argument('-v', '--version', action='version', version=QtCore.QCoreApplication.applicationVersion())
        self.add_argument('--log-level', choices=['all', 'debug', 'info', 'warning', 'error', 'critical'], default=None, help='logging level')
        self.add_argument('--log-console', action='store_true', help='log to the console')
        self.add_argument('--log-file', type=pathlib.Path, default=None, help='log file')

        if addPrinters:
            self.add_argument('--printers-dir', default=Common.printersDir(), type=pathlib.Path, help='printer information directory')
            self.add_argument('--printer', default=None, help='printer to use')

            printerSpecificGroup = self.add_mutually_exclusive_group()
            printerSpecificGroup.add_argument('--port', default=None, help='port to use for Marlin2 connection')
            printerSpecificGroup.add_argument('--host', default=None, help='host to use for Moonraker connection')

    def _showMessage(self, message, errorCode=0):
        # Create the messagebox
        icon = QtWidgets.QMessageBox.Icon.Information if errorCode == 0 else QtWidgets.QMessageBox.Icon.Critical
        messageBox = QtWidgets.QMessageBox(icon, self.prog, message)

        # Set the font to a fixed width family
        font = messageBox.font()
        font.setFamily('Consolas')
        messageBox.setFont(font)

        # Adjust the dialog width
        gridLayout = messageBox.layout()
        textLayoutItem = gridLayout.itemAtPosition(0, gridLayout.columnCount() - 1)
        textWidget = textLayoutItem.widget()
        fontMetrics = QtGui.QFontMetrics(font)
        textWidget.setFixedWidth(fontMetrics.size(0, message).width())

        # Set the message
        messageBox.setText(message)

        messageBox.exec()
        sys.exit(errorCode)

    def error(self, message):
        if self.showDialog:
            os.environ['COLUMNS'] = str(self.errorColumnCount)
            self._showMessage(self.format_usage() + f'{self.prog}: error: {message}', errorCode=2)
        else:
            super().error(message)

    def print_help(self, *args, **kwargs):
        if self.showDialog:
            os.environ['COLUMNS'] = str(self.helpColumnCount)
            self._showMessage(self.format_help())
        else:
            super().print_help(*args, **kwargs)

if __name__ == '__main__':
    app = QtWidgets.QApplication()
    app.setApplicationName('CommonArgumentParser')

    # Parse command line arguments
    parser = CommonArgumentParser(app.applicationName())
    args = parser.parse_args()
#!/usr/bin/env python

from .Commands.CommandBase import CommandBase
from .Commands.CommandG0 import CommandG0
from .Commands.CommandG28 import CommandG28
from .Commands.CommandG30 import CommandG30
from .Commands.CommandG42 import CommandG42
from .Commands.CommandG90 import CommandG90
from .Commands.CommandG91 import CommandG91
from .Commands.CommandM104 import CommandM104
from .Commands.CommandM105 import CommandM105
from .Commands.CommandM114 import CommandM114
from .Commands.CommandM118 import CommandM118
from .Commands.CommandM140 import CommandM140
from .Commands.CommandM400 import CommandM400
from .Commands.CommandM420 import CommandM420
from .Commands.CommandM851 import CommandM851
from .SerialConnection import SerialConnection
from PySide6 import QtCore
import queue

class CommandConnection(SerialConnection):
    errorOccurred = QtCore.Signal(CommandBase)
    finished = QtCore.Signal(CommandBase)
    finishedG0 = QtCore.Signal(CommandBase)
    finishedG28 = QtCore.Signal(CommandBase)
    finishedG30 = QtCore.Signal(CommandBase)
    finishedG42 = QtCore.Signal(CommandBase)
    finishedG90 = QtCore.Signal(CommandBase)
    finishedG91 = QtCore.Signal(CommandBase)
    finishedM104 = QtCore.Signal(CommandBase)
    finishedM105 = QtCore.Signal(CommandBase)
    finishedM114 = QtCore.Signal(CommandBase)
    finishedM118 = QtCore.Signal(CommandBase)
    finishedM140 = QtCore.Signal(CommandBase)
    finishedM400 = QtCore.Signal(CommandBase)
    finishedM420 = QtCore.Signal(CommandBase)
    finishedM851 = QtCore.Signal(CommandBase)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.commandQueue = queue.SimpleQueue()
        self.currentCommand = None

    def pendingCount(self):
        return self.commandQueue.qsize()

    def _processLine(self, line):
        """ Improve error handling here """

        # Skip echo lines
        if line.startswith('echo:'):
            return

        # Verify there is a current command
        if self.currentCommand is None:
            raise IOError('Received a line without a command ({line}).')

        # Send the line to the current command
        self.currentCommand.processLine(line)

    def _createCommand(self, commandType, *args, **kwargs):
        command = commandType(*args, **kwargs)
        command.finished.connect(self._finished)
        command.errorOccurred.connect(self._errorOccurred)

        self.logger.info(f'Sending command - {command}')
        self.write(command.request)

        if self.currentCommand is None:
            self.currentCommand = command
        else:
            self.commandQueue.put(command)

        return command

    def sendG0(self, *args, **kwargs):
        return self._createCommand(CommandG0, *args, **kwargs)

    def sendG28(self, *args, **kwargs):
        return self._createCommand(CommandG28, *args, **kwargs)

    def sendG30(self, *args, **kwargs):
        return self._createCommand(CommandG30, *args, **kwargs)

    def sendG42(self, *args, **kwargs):
        return self._createCommand(CommandG42, *args, **kwargs)

    def sendG90(self, *args, **kwargs):
        return self._createCommand(CommandG90, *args, **kwargs)

    def sendG91(self, *args, **kwargs):
        return self._createCommand(CommandG91, *args, **kwargs)

    def sendM104(self, *args, **kwargs):
        return self._createCommand(CommandM104, *args, **kwargs)

    def sendM105(self, *args, **kwargs):
        return self._createCommand(CommandM105, *args, **kwargs)

    def sendM114(self, *args, **kwargs):
        return self._createCommand(CommandM114, *args, **kwargs)

    def sendM118(self, *args, **kwargs):
        return self._createCommand(CommandM118, *args, **kwargs)

    def sendM140(self, *args, **kwargs):
        return self._createCommand(CommandM140, *args, **kwargs)

    def sendM400(self, *args, **kwargs):
        return self._createCommand(CommandM400, *args, **kwargs)

    def sendM420(self, *args, **kwargs):
        return self._createCommand(CommandM420, *args, **kwargs)

    def sendM851(self, *args, **kwargs):
        return self._createCommand(CommandM851, *args, **kwargs)

    def _finished(self, command):
        assert(command == self.currentCommand)

        self.logger.debug(f'Command {command} finished with result: {command.result}')

        getattr(self, f'finished{command.NAME}').emit(command)
        self.finished.emit(command)
        command.deleteLater()

        if self.commandQueue.empty():
            self.currentCommand = None
        else:
            self.currentCommand = self.commandQueue.get()

    def _errorOccurred(self, command):
        assert(command == self.currentCommand)

        self.logger.error(f'Command {command} errored with message: {command.error}')
        self.errorOccurred.emit(command)

if __name__ == '__main__':
    # Main only imports
    from Common.PrinterInfo import ConnectionMode
    from Widgets.PrinterConnectWidget import PrinterConnectWidget
    from Dialogs.FatalErrorDialog import FatalErrorDialog
    from Common import Common
    from Common import Version
    from PySide6 import QtCore
    from PySide6 import QtWidgets
    import argparse
    import pathlib
    import sys

    class MainWindow(QtWidgets.QMainWindow):
        def __init__(self, printersDir, *args, printer=None, host=None, port=None, **kwargs):
            super().__init__(*args, **kwargs)

            self.connection = None
            self.qtConnections = []
            self.__createWidgets()
            self.__layoutWidgets()

            self.printerConnectWidget.loadPrinters(printersDir,
                                                   desiredPrinter = printer,
                                                   desiredHost = host,
                                                   desiredPort = port,
                                                   onlyConnectionModes = [ConnectionMode.MARLIN_2])

        def __createWidgets(self):
            self.printerConnectWidget = PrinterConnectWidget(hasHomeButton=False)
            self.printerConnectWidget.connectRequested.connect(self.connectToPrinter)
            self.printerConnectWidget.disconnectRequested.connect(self.disconnectFromPrinter)

            self.startG0Button = QtWidgets.QPushButton('G0')
            self.startG0Button.clicked.connect(self.startG0)
            self.startG0XCheckBox = QtWidgets.QCheckBox()
            self.startG0XSpinBox = QtWidgets.QDoubleSpinBox()
            self.startG0XSpinBox.setMinimum(0)
            self.startG0XSpinBox.setMaximum(500)
            self.startG0YCheckBox = QtWidgets.QCheckBox()
            self.startG0YSpinBox = QtWidgets.QDoubleSpinBox()
            self.startG0YSpinBox.setMinimum(0)
            self.startG0YSpinBox.setMaximum(500)
            self.startG0ZCheckBox = QtWidgets.QCheckBox()
            self.startG0ZSpinBox = QtWidgets.QDoubleSpinBox()
            self.startG0ZSpinBox.setMinimum(0)
            self.startG0ZSpinBox.setMaximum(500)
            self.startG0FCheckBox = QtWidgets.QCheckBox()
            self.startG0FSpinBox = QtWidgets.QDoubleSpinBox()
            self.startG0FSpinBox.setMinimum(0)
            self.startG0FSpinBox.setMaximum(5000)

            self.startG28Button = QtWidgets.QPushButton('G28')
            self.startG28Button.clicked.connect(self.startG28)

            self.startG30Button = QtWidgets.QPushButton('G30')
            self.startG30Button.clicked.connect(self.startG30)
            self.startG30CCheckBox = QtWidgets.QCheckBox('C')
            self.startG30ECheckBox = QtWidgets.QCheckBox('E')
            self.startG30XCheckBox = QtWidgets.QCheckBox()
            self.startG30XCheckBox.setChecked(True)
            self.startG30XSpinBox = QtWidgets.QDoubleSpinBox()
            self.startG30XSpinBox.setMinimum(0)
            self.startG30XSpinBox.setMaximum(500)
            self.startG30YCheckBox = QtWidgets.QCheckBox()
            self.startG30YCheckBox.setChecked(True)
            self.startG30YSpinBox = QtWidgets.QDoubleSpinBox()
            self.startG30YSpinBox.setMinimum(0)
            self.startG30YSpinBox.setMaximum(500)

            self.startG42Button = QtWidgets.QPushButton('G42')
            self.startG42Button.clicked.connect(self.startG42)
            self.startG42FCheckBox = QtWidgets.QCheckBox()
            self.startG42FSpinBox = QtWidgets.QDoubleSpinBox()
            self.startG42FSpinBox.setMinimum(0)
            self.startG42FSpinBox.setMaximum(5000)
            self.startG42ICheckBox = QtWidgets.QCheckBox()
            self.startG42ICheckBox.setChecked(True)
            self.startG42ISpinBox = QtWidgets.QSpinBox()
            self.startG42ISpinBox.setMinimum(0)
            self.startG42ISpinBox.setMaximum(500)
            self.startG42JCheckBox = QtWidgets.QCheckBox()
            self.startG42JCheckBox.setChecked(True)
            self.startG42JSpinBox = QtWidgets.QSpinBox()
            self.startG42JSpinBox.setMinimum(0)
            self.startG42JSpinBox.setMaximum(500)

            self.startG90Button = QtWidgets.QPushButton('G90')
            self.startG90Button.clicked.connect(self.startG90)

            self.startG91Button = QtWidgets.QPushButton('G91')
            self.startG91Button.clicked.connect(self.startG91)

            self.startM104Button = QtWidgets.QPushButton('M104')
            self.startM104Button.clicked.connect(self.startM104)
            self.startM104BCheckBox = QtWidgets.QCheckBox()
            self.startM104BSpinBox = QtWidgets.QDoubleSpinBox()
            self.startM104BSpinBox.setMinimum(0)
            self.startM104BSpinBox.setMaximum(500)
            self.startM104FCheckBox = QtWidgets.QCheckBox()
            self.startM104FLineEdit = QtWidgets.QLineEdit()
            self.startM104ICheckBox = QtWidgets.QCheckBox()
            self.startM104ISpinBox = QtWidgets.QSpinBox()
            self.startM104ISpinBox.setMinimum(0)
            self.startM104ISpinBox.setMaximum(10)
            self.startM104SCheckBox = QtWidgets.QCheckBox()
            self.startM104SCheckBox.setChecked(True)
            self.startM104SSpinBox = QtWidgets.QDoubleSpinBox()
            self.startM104SSpinBox.setMinimum(0)
            self.startM104SSpinBox.setMaximum(500)
            self.startM104TCheckBox = QtWidgets.QCheckBox()
            self.startM104TSpinBox = QtWidgets.QSpinBox()
            self.startM104TSpinBox.setMinimum(0)
            self.startM104TSpinBox.setMaximum(10)

            self.startM105Button = QtWidgets.QPushButton('M105')
            self.startM105Button.clicked.connect(self.startM105)
            self.startM105RCheckBox = QtWidgets.QCheckBox('R')
            self.startM105TCheckBox = QtWidgets.QCheckBox()
            self.startM105TSpinBox = QtWidgets.QSpinBox()
            self.startM105TSpinBox.setMinimum(0)
            self.startM105TSpinBox.setMaximum(10)

            self.startM114Button = QtWidgets.QPushButton('M114')
            self.startM114Button.clicked.connect(self.startM114)
            self.startM114DCheckBox = QtWidgets.QCheckBox('D')
            self.startM114ECheckBox = QtWidgets.QCheckBox('E')
            self.startM114RCheckBox = QtWidgets.QCheckBox('R')

            self.startM118Button = QtWidgets.QPushButton('M118')
            self.startM118Button.clicked.connect(self.startM118)
            self.startM118A1CheckBox = QtWidgets.QCheckBox('A1')
            self.startM118E1CheckBox = QtWidgets.QCheckBox('E1')
            self.startM118PnCheckBox = QtWidgets.QCheckBox()
            self.startM118PnSpinBox = QtWidgets.QSpinBox()
            self.startM118PnSpinBox.setMinimum(0)
            self.startM118PnSpinBox.setMaximum(9)
            self.startM118StringCheckBox = QtWidgets.QCheckBox()
            self.startM118StringLineEdit = QtWidgets.QLineEdit()

            self.startM140Button = QtWidgets.QPushButton('M140')
            self.startM140Button.clicked.connect(self.startM140)
            self.startM140ICheckBox = QtWidgets.QCheckBox()
            self.startM140ISpinBox = QtWidgets.QSpinBox()
            self.startM140ISpinBox.setMinimum(0)
            self.startM140ISpinBox.setMaximum(10)
            self.startM140SCheckBox = QtWidgets.QCheckBox()
            self.startM140SCheckBox.setChecked(True)
            self.startM140SSpinBox = QtWidgets.QDoubleSpinBox()
            self.startM140SSpinBox.setMinimum(0)
            self.startM140SSpinBox.setMaximum(500)

            self.startM400Button = QtWidgets.QPushButton('M400')
            self.startM400Button.clicked.connect(self.startM400)

            self.startM420Button = QtWidgets.QPushButton('M420')
            self.startM420Button.clicked.connect(self.startM420)
            self.startM420CCheckBox = QtWidgets.QCheckBox('C')
            self.startM420LCheckBox = QtWidgets.QCheckBox()
            self.startM420LSpinBox = QtWidgets.QSpinBox()
            self.startM420LSpinBox.setMinimum(0)
            self.startM420LSpinBox.setMaximum(99)
            self.startM420SCheckBox = QtWidgets.QCheckBox()
            self.startM420TCheckBox = QtWidgets.QCheckBox()
            self.startM420TComboBox = QtWidgets.QComboBox()
            self.startM420TComboBox.addItem('0')
            self.startM420TComboBox.addItem('1')
            self.startM420TComboBox.addItem('4')
            self.startM420VCheckBox = QtWidgets.QCheckBox('V')
            self.startM420VCheckBox.setChecked(True)
            self.startM420ZCheckBox = QtWidgets.QCheckBox()
            self.startM420ZSpinBox = QtWidgets.QDoubleSpinBox()
            self.startM420ZSpinBox.setMinimum(0)
            self.startM420ZSpinBox.setMaximum(500)

            self.startM851Button = QtWidgets.QPushButton('M851')
            self.startM851Button.clicked.connect(self.startM851)
            self.startM851XCheckBox = QtWidgets.QCheckBox()
            self.startM851XSpinBox = QtWidgets.QDoubleSpinBox()
            self.startM851XSpinBox.setMinimum(-50)
            self.startM851XSpinBox.setMaximum(50)
            self.startM851YCheckBox = QtWidgets.QCheckBox()
            self.startM851YSpinBox = QtWidgets.QDoubleSpinBox()
            self.startM851YSpinBox.setMinimum(-50)
            self.startM851YSpinBox.setMaximum(50)
            self.startM851ZCheckBox = QtWidgets.QCheckBox()
            self.startM851ZSpinBox = QtWidgets.QDoubleSpinBox()
            self.startM851ZSpinBox.setMinimum(-50)
            self.startM851ZSpinBox.setMaximum(50)

            self.controlsGroupBox = QtWidgets.QGroupBox('Controls')
            self.controlsGroupBox.setEnabled(False)

            self.logTextEdit = QtWidgets.QTextEdit()
            self.logTextEdit.setReadOnly(True)
            self.logTextEdit.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
            font = self.logTextEdit.font()
            font.setFamily('Courier')
            self.logTextEdit.setFont(font)

            self.autoClearCheckBox = QtWidgets.QCheckBox('Auto clear')
            self.autoClearCheckBox.setChecked(True)
            self.clearButton = QtWidgets.QPushButton('Clear')
            self.clearButton.clicked.connect(self.clear)

        def __layoutWidgets(self):
            startG0Layout = QtWidgets.QHBoxLayout()
            startG0Layout.addWidget(self.startG0Button)
            startG0Layout.addWidget(QtWidgets.QLabel('X:'))
            startG0Layout.addWidget(self.startG0XCheckBox)
            startG0Layout.addWidget(self.startG0XSpinBox)
            startG0Layout.addWidget(QtWidgets.QLabel('Y:'))
            startG0Layout.addWidget(self.startG0YCheckBox)
            startG0Layout.addWidget(self.startG0YSpinBox)
            startG0Layout.addWidget(QtWidgets.QLabel('Z:'))
            startG0Layout.addWidget(self.startG0ZCheckBox)
            startG0Layout.addWidget(self.startG0ZSpinBox)
            startG0Layout.addWidget(QtWidgets.QLabel('F:'))
            startG0Layout.addWidget(self.startG0FCheckBox)
            startG0Layout.addWidget(self.startG0FSpinBox)
            startG0Layout.addStretch()

            startG28Layout = QtWidgets.QHBoxLayout()
            startG28Layout.addWidget(self.startG28Button)
            startG28Layout.addStretch()

            startG30Layout = QtWidgets.QHBoxLayout()
            startG30Layout.addWidget(self.startG30Button)
            startG30Layout.addWidget(self.startG30CCheckBox)
            startG30Layout.addWidget(self.startG30ECheckBox)
            startG30Layout.addWidget(QtWidgets.QLabel('X:'))
            startG30Layout.addWidget(self.startG30XCheckBox)
            startG30Layout.addWidget(self.startG30XSpinBox)
            startG30Layout.addWidget(QtWidgets.QLabel('Y:'))
            startG30Layout.addWidget(self.startG30YCheckBox)
            startG30Layout.addWidget(self.startG30YSpinBox)
            startG30Layout.addStretch()

            startG42Layout = QtWidgets.QHBoxLayout()
            startG42Layout.addWidget(self.startG42Button)
            startG42Layout.addWidget(QtWidgets.QLabel('F:'))
            startG42Layout.addWidget(self.startG42FCheckBox)
            startG42Layout.addWidget(self.startG42FSpinBox)
            startG42Layout.addWidget(QtWidgets.QLabel('I:'))
            startG42Layout.addWidget(self.startG42ICheckBox)
            startG42Layout.addWidget(self.startG42ISpinBox)
            startG42Layout.addWidget(QtWidgets.QLabel('J:'))
            startG42Layout.addWidget(self.startG42JCheckBox)
            startG42Layout.addWidget(self.startG42JSpinBox)
            startG42Layout.addStretch()

            startG90Layout = QtWidgets.QHBoxLayout()
            startG90Layout.addWidget(self.startG90Button)
            startG90Layout.addStretch()

            startG91Layout = QtWidgets.QHBoxLayout()
            startG91Layout.addWidget(self.startG91Button)
            startG91Layout.addStretch()

            startM104Layout = QtWidgets.QHBoxLayout()
            startM104Layout.addWidget(self.startM104Button)
            startM104Layout.addWidget(QtWidgets.QLabel('B:'))
            startM104Layout.addWidget(self.startM104BCheckBox)
            startM104Layout.addWidget(self.startM104BSpinBox)
            startM104Layout.addWidget(QtWidgets.QLabel('F:'))
            startM104Layout.addWidget(self.startM104FCheckBox)
            startM104Layout.addWidget(self.startM104FLineEdit)
            startM104Layout.addWidget(QtWidgets.QLabel('I:'))
            startM104Layout.addWidget(self.startM104ICheckBox)
            startM104Layout.addWidget(self.startM104ISpinBox)
            startM104Layout.addWidget(QtWidgets.QLabel('S:'))
            startM104Layout.addWidget(self.startM104SCheckBox)
            startM104Layout.addWidget(self.startM104SSpinBox)
            startM104Layout.addWidget(QtWidgets.QLabel('T:'))
            startM104Layout.addWidget(self.startM104TCheckBox)
            startM104Layout.addWidget(self.startM104TSpinBox)
            startM104Layout.addStretch()

            startM105Layout = QtWidgets.QHBoxLayout()
            startM105Layout.addWidget(self.startM105Button)
            startM105Layout.addWidget(self.startM105RCheckBox)
            startM105Layout.addWidget(QtWidgets.QLabel('T:'))
            startM105Layout.addWidget(self.startM105TCheckBox)
            startM105Layout.addWidget(self.startM105TSpinBox)
            startM105Layout.addStretch()

            startM114Layout = QtWidgets.QHBoxLayout()
            startM114Layout.addWidget(self.startM114Button)
            startM114Layout.addWidget(self.startM114DCheckBox)
            startM114Layout.addWidget(self.startM114ECheckBox)
            startM114Layout.addWidget(self.startM114RCheckBox)
            startM114Layout.addStretch()

            startM118Layout = QtWidgets.QHBoxLayout()
            startM118Layout.addWidget(self.startM118Button)
            startM118Layout.addWidget(self.startM118A1CheckBox)
            startM118Layout.addWidget(self.startM118E1CheckBox)
            startM118Layout.addWidget(QtWidgets.QLabel('Pn:'))
            startM118Layout.addWidget(self.startM118PnCheckBox)
            startM118Layout.addWidget(self.startM118PnSpinBox)
            startM118Layout.addWidget(QtWidgets.QLabel('String:'))
            startM118Layout.addWidget(self.startM118StringCheckBox)
            startM118Layout.addWidget(self.startM118StringLineEdit)

            startM140Layout = QtWidgets.QHBoxLayout()
            startM140Layout.addWidget(self.startM140Button)
            startM140Layout.addWidget(QtWidgets.QLabel('I:'))
            startM140Layout.addWidget(self.startM140ICheckBox)
            startM140Layout.addWidget(self.startM140ISpinBox)
            startM140Layout.addWidget(QtWidgets.QLabel('S:'))
            startM140Layout.addWidget(self.startM140SCheckBox)
            startM140Layout.addWidget(self.startM140SSpinBox)
            startM140Layout.addStretch()

            startM400Layout = QtWidgets.QHBoxLayout()
            startM400Layout.addWidget(self.startM400Button)
            startM400Layout.addStretch()

            startM420Layout = QtWidgets.QHBoxLayout()
            startM420Layout.addWidget(self.startM420Button)
            startM420Layout.addWidget(self.startM420CCheckBox)
            startM420Layout.addWidget(QtWidgets.QLabel('L:'))
            startM420Layout.addWidget(self.startM420LCheckBox)
            startM420Layout.addWidget(self.startM420LSpinBox)
            startM420Layout.addWidget(self.startM420SCheckBox)
            startM420Layout.addWidget(QtWidgets.QLabel('T:'))
            startM420Layout.addWidget(self.startM420TCheckBox)
            startM420Layout.addWidget(self.startM420TComboBox)
            startM420Layout.addWidget(self.startM420VCheckBox)
            startM420Layout.addWidget(QtWidgets.QLabel('Z:'))
            startM420Layout.addWidget(self.startM420ZCheckBox)
            startM420Layout.addWidget(self.startM420ZSpinBox)
            startM420Layout.addStretch()

            startM851Layout = QtWidgets.QHBoxLayout()
            startM851Layout.addWidget(self.startM851Button)
            startM851Layout.addWidget(QtWidgets.QLabel('X:'))
            startM851Layout.addWidget(self.startM851XCheckBox)
            startM851Layout.addWidget(self.startM851XSpinBox)
            startM851Layout.addWidget(QtWidgets.QLabel('Y:'))
            startM851Layout.addWidget(self.startM851YCheckBox)
            startM851Layout.addWidget(self.startM851YSpinBox)
            startM851Layout.addWidget(QtWidgets.QLabel('Z:'))
            startM851Layout.addWidget(self.startM851ZCheckBox)
            startM851Layout.addWidget(self.startM851ZSpinBox)
            startM851Layout.addStretch()

            clearLayout = QtWidgets.QHBoxLayout()
            clearLayout.addStretch()
            clearLayout.addWidget(self.autoClearCheckBox)
            clearLayout.addWidget(self.clearButton)
            clearLayout.addStretch()

            controlsLayout = QtWidgets.QVBoxLayout()
            controlsLayout.addLayout(startG0Layout)
            controlsLayout.addLayout(startG28Layout)
            controlsLayout.addLayout(startG30Layout)
            controlsLayout.addLayout(startG42Layout)
            controlsLayout.addLayout(startG90Layout)
            controlsLayout.addLayout(startG91Layout)
            controlsLayout.addLayout(startM104Layout)
            controlsLayout.addLayout(startM105Layout)
            controlsLayout.addLayout(startM114Layout)
            controlsLayout.addLayout(startM118Layout)
            controlsLayout.addLayout(startM140Layout)
            controlsLayout.addLayout(startM400Layout)
            controlsLayout.addLayout(startM420Layout)
            controlsLayout.addLayout(startM851Layout)

            self.controlsGroupBox.setLayout(controlsLayout)

            layout = QtWidgets.QVBoxLayout()
            layout.addWidget(self.printerConnectWidget)
            layout.addWidget(self.controlsGroupBox)
            layout.addWidget(self.logTextEdit)
            layout.addLayout(clearLayout)

            widget = QtWidgets.QWidget()
            widget.setLayout(layout)
            self.setCentralWidget(widget)

        def makeConnections(self):
            assert(len(self.qtConnections) == 0)

            self.qtConnections.append(self.connection.wrote.connect(lambda line: self.logTextEdit.append(f'Wrote: ->{line}<-')))
            self.qtConnections.append(self.connection.received.connect(lambda line: self.logTextEdit.append(f'Received line: ->{line}<-')))

            self.qtConnections.append(self.connection.errorOccurred.connect(self.logErrorOccurred))
            self.qtConnections.append(self.connection.finished.connect(lambda command: self.logFinished('finished', command)))
            self.qtConnections.append(self.connection.finishedG0.connect(lambda command: self.logFinished('finishedG0', command)))
            self.qtConnections.append(self.connection.finishedG28.connect(lambda command: self.logFinished('finishedG28', command)))
            self.qtConnections.append(self.connection.finishedG30.connect(lambda command: self.logFinished('finishedG30', command)))
            self.qtConnections.append(self.connection.finishedG42.connect(lambda command: self.logFinished('finishedG42', command)))
            self.qtConnections.append(self.connection.finishedG90.connect(lambda command: self.logFinished('finishedG90', command)))
            self.qtConnections.append(self.connection.finishedG91.connect(lambda command: self.logFinished('finishedG91', command)))
            self.qtConnections.append(self.connection.finishedM104.connect(lambda command: self.logFinished('finishedM104', command)))
            self.qtConnections.append(self.connection.finishedM105.connect(lambda command: self.logFinished('finishedM105', command)))
            self.qtConnections.append(self.connection.finishedM114.connect(lambda command: self.logFinished('finishedM114', command)))
            self.qtConnections.append(self.connection.finishedM118.connect(lambda command: self.logFinished('finishedM118', command)))
            self.qtConnections.append(self.connection.finishedM140.connect(lambda command: self.logFinished('finishedM140', command)))
            self.qtConnections.append(self.connection.finishedM400.connect(lambda command: self.logFinished('finishedM400', command)))
            self.qtConnections.append(self.connection.finishedM420.connect(lambda command: self.logFinished('finishedM420', command)))
            self.qtConnections.append(self.connection.finishedM851.connect(lambda command: self.logFinished('finishedM851', command)))

        def breakConnections(self):
            for qtConnection in self.qtConnections:
                self.connection.disconnect(qtConnection)
            self.qtConnections = []

        def connectToPrinter(self):
            self.connection = CommandConnection(printerInfo=self.printerConnectWidget.printerInfo())
            self.makeConnections()
            self.connection.open(self.printerConnectWidget.port())
            self.printerConnectWidget.setConnected()
            self.controlsGroupBox.setEnabled(True)

        def disconnectFromPrinter(self):
            self.controlsGroupBox.setEnabled(False)
            self.printerConnectWidget.setDisconnected()
            self.connection.close()
            self.breakConnections()
            self.connection = None

        def start(self, name, **kwargs):
            if self.autoClearCheckBox.isChecked():
                self.logTextEdit.clear()

            command = getattr(self.connection, f'send{name}')(**kwargs)
            command.finished.connect(self.logCommandFinished)
            command.errorOccurred.connect(self.logCommandErrorOccurred)

        def startG0(self):
            self.start('G0',
                       x=self.startG0XSpinBox.value() if self.startG0XCheckBox.isChecked() else None,
                       y=self.startG0YSpinBox.value() if self.startG0YCheckBox.isChecked() else None,
                       z=self.startG0ZSpinBox.value() if self.startG0ZCheckBox.isChecked() else None,
                       f=self.startG0FSpinBox.value() if self.startG0FCheckBox.isChecked() else None)

        def startG28(self):
            self.start('G28')

        def startG30(self):
            self.start('G30',
                       c=self.startG30CCheckBox.isChecked(),
                       e=self.startG30ECheckBox.isChecked(),
                       x=self.startG30XSpinBox.value() if self.startG30XCheckBox.isChecked() else None,
                       y=self.startG30YSpinBox.value() if self.startG30YCheckBox.isChecked() else None)

        def startG42(self):
            self.start('G42',
                       f=self.startG42FSpinBox.value() if self.startG42FCheckBox.isChecked() else None,
                       i=self.startG42ISpinBox.value() if self.startG42ICheckBox.isChecked() else None,
                       j=self.startG42JSpinBox.value() if self.startG42JCheckBox.isChecked() else None)

        def startG90(self):
            self.start('G90')

        def startG91(self):
            self.start('G91')

        def startM104(self):
            self.start('M104',
                       b=self.startM104BSpinBox.value() if self.startM104BCheckBox.isChecked() else None,
                       f=self.startM104FLineEdit.text() if self.startM104FCheckBox.isChecked() else None,
                       i=self.startM104ISpinBox.value() if self.startM104ICheckBox.isChecked() else None,
                       s=self.startM104SSpinBox.value() if self.startM104SCheckBox.isChecked() else None,
                       t=self.startM104TSpinBox.value() if self.startM104TCheckBox.isChecked() else None)

        def startM105(self):
            self.start('M105',
                       r=self.startM105BSpinBox.value() if self.startM105RCheckBox.isChecked() else None,
                       t=self.startM105TSpinBox.value() if self.startM105TCheckBox.isChecked() else None)

        def startM114(self):
            self.start('M114',
                       d=True if self.startM114DCheckBox.isChecked() else None,
                       e=True if self.startM114ECheckBox.isChecked() else None,
                       r=True if self.startM114RCheckBox.isChecked() else None)

        def startM118(self):
            self.start('M118',
                       a1= True if self.startM118A1CheckBox.isChecked() else None,
                       e1= True if self.startM118E1CheckBox.isChecked() else None,
                       pn=self.startM118PnSpinBox.value() if self.startM118PnCheckBox.isChecked() else None,
                       string=self.startM118StringLineEdit.text() if self.startM118StringCheckBox.isChecked() else None)

        def startM140(self):
            self.start('M140',
                       i=self.startM140ISpinBox.value() if self.startM140ICheckBox.isChecked() else None,
                       s=self.startM140SSpinBox.value() if self.startM140SCheckBox.isChecked() else None)

        def startM400(self):
            self.start('M400')

        def startM420(self):
            self.start('M420',
                       c=True if self.startM420CCheckBox.isChecked() else None,
                       l=self.startM420LSpinBox.value() if self.startM420LCheckBox.isChecked() else None,
                       s=True if self.startM420SCheckBox.isChecked() else None,
                       t=int(self.startM420TComboBox.currentText()) if self.startM420TCheckBox.isChecked() else None,
                       v=True if self.startM420VCheckBox.isChecked() else None,
                       z=self.startM420ZSpinBox.value() if self.startM420ZCheckBox.isChecked() else None)

        def startM851(self):
            self.start('M851',
                       x=self.startM851XSpinBox.value() if self.startM851XCheckBox.isChecked() else None,
                       y=self.startM851YSpinBox.value() if self.startM851YCheckBox.isChecked() else None,
                       z=self.startM851ZSpinBox.value() if self.startM851ZCheckBox.isChecked() else None)

        def clear(self):
            self.logTextEdit.clear()

        def logErrorOccurred(self, command):
            self.logTextEdit.append(f'Connection signal: _errorOccurred:\n    Command: {command}\n    Error: {command.error}\n')

        def logFinished(self, signalName, command):
            if command.error:
                self.logTextEdit.append(f'Connection signal: {signalName}:\n    Command: {command}\n    Error: {command.error}\n')
            else:
                self.logTextEdit.append(f'Connection signal: {signalName}:\n    Command: {command}\n    Result: {command.result}\n')

        def logCommandErrorOccurred(self, command):
            self.logTextEdit.append(f'Command signal: errorOccurred:\n    Command: {command}\n    Error: {command.error}\n')

        def logCommandFinished(self, command):
            if command.error:
                self.logTextEdit.append(f'Command signal: finished:\n    Command: {command}\n    Error: {command.error}\n')
            else:
                self.logTextEdit.append(f'Command signal: finished:\n    Command: {command}\n    Result: {command.result}\n')

    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName('Command Connection Test App')
    app.setApplicationVersion(Version.version())

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Test app for CommandConnection')
    parser.add_argument('-v', '--version', action='version', version=app.applicationVersion())
    parser.add_argument('--printers-dir', default=Common.baseDir() / 'Printers', type=pathlib.Path, help='printer information directory')
    parser.add_argument('--printer', default=None, help='printer to use')

    # port AND host require --printer to be used
    parser.add_argument('--port', default=None, help='port to use for Marlin2 connection')
    parser.add_argument('--host', default=None, help='host to use for Moonraker connection')
    parser.add_argument('--log-level', choices=['debug', 'info', 'warning', 'error', 'critical'], default=None, help='logging level')
    parser.add_argument('--log-console', action='store_true', help='log to the console')
    parser.add_argument('--log-file', type=pathlib.Path, default=None, help='log file')

    args = parser.parse_args()

    # Configure logging
    Common.configureLogging(level=args.log_level, console=args.log_console, file=args.log_file)

    # Verify the printers directory exists
    if args.printers_dir is not None and not args.printers_dir.exists():
        FatalErrorDialog(None, f'Failed to find printer directory: {args.printers_dir}.')

    mainWindow = MainWindow(printersDir=args.printers_dir,
                            printer=args.printer,
                            host=args.host,
                            port=args.port)
    mainWindow.show()
    mainWindow.resize(600, 400)

    try:
       sys.exit(app.exec())
    except KeyboardInterrupt:
        sys.exit(1)
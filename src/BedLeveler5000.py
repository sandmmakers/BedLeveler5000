#!/usr/bin/env python

from Common import Common
from Common.CommonArgumentParser import CommonArgumentParser
from Widgets.BedLeveler5000.ManualWidget import ManualWidget
from Widgets.BedLeveler5000.MeshWidget import MeshWidget
from Common.PrinterInfo import ConnectionMode
from Printers.Marlin2.Marlin2Printer import Marlin2Printer
from Printers.Moonraker.MoonrakerPrinter import MoonrakerPrinter
from Widgets.BedLeveler5000.TemperatureControlsWidget import TemperatureControlsWidget
from Widgets.BedLeveler5000.StatusBar import StatusBar
from Widgets.PrinterConnectWidget import PrinterConnectWidget
from Dialogs.BedLeveler5000.CancellableStatusDialog import CancellableStatusDialog
from Dialogs.AboutDialog import AboutDialog
from Dialogs.WarningDialog import WarningDialog
from Dialogs.ErrorDialog import ErrorDialog
from Dialogs.FatalErrorDialog import FatalErrorDialog
from Common import Version
from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets
from PySide6 import QtSerialPort
import argparse
from enum import StrEnum
import json
import logging
import pathlib
import signal
import sys

# Enable CTRL-C killing the application
signal.signal(signal.SIGINT, signal.SIG_DFL)

DESCRIPTION = 'A utility aiding in FDM printer bed leveling.'

class MainWindow(QtWidgets.QMainWindow):
    class State(StrEnum):
        DISCONNECTED = 'Disconnected'
        INITIALIZING = 'Initializing'
        INITIALIZING_MESH = 'Initializing mesh'
        CONNECTED = 'Connected'
        HOMING = 'Homing'
        MANUAL_PROBE = 'Manually probing point'
        UPDATING_MESH = 'Updating mesh'

    class Dialog(StrEnum):
        INITIALIZING = 'Initializing'
        HOMING = 'Homing'
        PROBE = 'Probe'

    def __init__(self, *args, printersDir, printer=None, host=None, port=None, noTemperatureReporting=False, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle(QtCore.QCoreApplication.applicationName())
        self.logger = logging.getLogger(QtCore.QCoreApplication.applicationName())

        self.__createWidgets()
        self.__layoutWidgets()
        self.__createMenus()
        self.__createStatusBar()
        self.__createDialogs()
        self.__createTimers()

        self.currentId = -1
        self.printer = None
        self.printerInfo = None
        self.meshCoordinates = None
        self.printerQtConnections = []
        self.noTemperatureReporting = noTemperatureReporting
        self.printerConnectWidget.loadPrinters(printersDir, desiredPrinter=printer, desiredHost=host, desiredPort=port)
        self.updateState(self.State.DISCONNECTED)

    def __createWidgets(self):
        # Printer connect widget
        self.printerConnectWidget = PrinterConnectWidget()
        self.printerConnectWidget.printerChanged.connect(self.switchPrinter)
        self.printerConnectWidget.connectRequested.connect(self.connectToPrinter)
        self.printerConnectWidget.disconnectRequested.connect(self.disconnectFromPrinter)
        self.printerConnectWidget.homeRequested.connect(self.home)

        # Temperature Controls Widget
        self.temperatureControlsWidget = TemperatureControlsWidget()
        self.temperatureControlsWidget.bedHeaterChanged.connect(self.setBedTemperature)
        self.temperatureControlsWidget.nozzleHeaterChanged.connect(self.setNozzleTemperature)

        # Manual widget
        self.manualWidget = ManualWidget()
        self.manualWidget.probe.connect(self.manualProbe)

        # Mesh widget
        self.meshWidget = MeshWidget()
        self.meshWidget.updateMesh.connect(self.updateMesh)

        # Tab widget
        self.tabWidget = QtWidgets.QTabWidget()
        self.tabWidget.addTab(self.manualWidget, 'Manual')
        self.tabWidget.addTab(self.meshWidget, 'Mesh')

    def __layoutWidgets(self):
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.printerConnectWidget)
        layout.addWidget(self.temperatureControlsWidget)
        layout.addWidget(self.tabWidget)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def __createMenus(self):
        # File menu
        self.fileMenu = QtWidgets.QMenu('File', self)
        self.exitAction = QtGui.QAction('Exit', self)
        self.exitAction.setStatusTip('Exit the application')
        self.exitAction.triggered.connect(self.close)
        self.fileMenu.addAction(self.exitAction)
        self.menuBar().addMenu(self.fileMenu)

        # Ports
        self.portsMenu = QtWidgets.QMenu('Ports', self)
        self.enumeratePortsAction = QtGui.QAction('Enumerate', self)
        self.enumeratePortsAction.setStatusTip('Reenumerate COM ports')
        self.enumeratePortsAction.triggered.connect(self.printerConnectWidget.enumeratePorts)
        self.portsMenu.addAction(self.enumeratePortsAction)
        self.menuBar().addMenu(self.portsMenu)

        self.settingsMenu = QtWidgets.QMenu('Settings', self)
        self.menuBar().addMenu(self.settingsMenu)

        self.helpMenu = QtWidgets.QMenu('Help', self)
        self.aboutAction = QtGui.QAction('About', self)
        self.aboutAction.triggered.connect(lambda : AboutDialog(DESCRIPTION).exec())
        self.helpMenu.addAction(self.aboutAction)
        self.aboutQtAction = QtGui.QAction('About Qt', self)
        self.aboutQtAction.triggered.connect(qApp.aboutQt)
        self.helpMenu.addAction(self.aboutQtAction)
        self.menuBar().addMenu(self.helpMenu)

    def __createStatusBar(self):
        self.setStatusBar(StatusBar())

    def __createDialogs(self):
        self.dialogs = {self.Dialog.INITIALIZING: CancellableStatusDialog(text='Initializing printer', parent=self),
                        self.Dialog.HOMING: CancellableStatusDialog(text='Homing', parent=self),
                        self.Dialog.PROBE: CancellableStatusDialog(text='Manually probing (x, y)', parent=self)}

        self.dialogs[self.Dialog.INITIALIZING].rejected.connect(self.disconnectFromPrinter)
        self.dialogs[self.Dialog.HOMING].rejected.connect(self._cancel)
        self.dialogs[self.Dialog.PROBE].rejected.connect(self._cancel)

    def __createTimers(self):
        self.temperatureJobPending = False
        self.temperatureTimer = QtCore.QTimer()
        self.temperatureTimer.setInterval(1000) # TODO: Make the interval configurable
        self.temperatureTimer.timeout.connect(self.getTemperatures)

    def _createId(self, base):
        self.currentId += 1
        return f'{base}-{self.currentId}'

    def connectToPrinter(self):
        assert self.printerInfo == self.printerConnectWidget.printerInfo()
        assert self.printerConnectWidget.connectionMode() in ConnectionMode

        # Create the printer and determine open arguments
        if self.printerConnectWidget.connectionMode() == ConnectionMode.MARLIN_2:
            self.printer = Marlin2Printer(self.printerConnectWidget.printerInfo(), parent=self)
            kwargs = {'port': self.printerConnectWidget.port()}
        elif self.printerConnectWidget.connectionMode() == ConnectionMode.MOONRAKER:
            self.printer = MoonrakerPrinter(self.printerConnectWidget.printerInfo(), parent=self)
            kwargs = {'host': self.printerConnectWidget.host()}

        # Make connections
        self.printerQtConnections.append(self.printer.errorOccurred.connect(self.reportPrinterError))
        self.printerQtConnections.append(self.printer.inited.connect(self._processInitResults))
        self.printerQtConnections.append(self.printer.homed.connect(self._finishHoming))
        self.printerQtConnections.append(self.printer.gotTemperatures.connect(self.updateTemperatures))
        self.printerQtConnections.append(self.printer.gotMeshCoordinates.connect(self._initializeMesh))
        self.printerQtConnections.append(self.printer.probed.connect(self._processProbe))

        # Open the printer
        self.printer.open(**kwargs)
        self.printerConnectWidget.setConnected()
        self.meshCoordinates = None

        # Set the temperature controls to off
        self.temperatureControlsWidget.resetButtons()

        # Start the temperature timer
        self.temperatureJobPending = False
        if not self.noTemperatureReporting:
            self.temperatureTimer.start()

        # Initialize the printer
        self.updateState(self.State.INITIALIZING)
        self.printer.init(self._createId('init'))
        self.dialogs[self.Dialog.INITIALIZING].show()

    def disconnectFromPrinter(self):
        assert(self.printerInfo == self.printerConnectWidget.printerInfo())

        # Stop the temperature timer
        self.temperatureJobPending = False
        self.temperatureTimer.stop()

        # Close the printer
        self.printerConnectWidget.setDisconnected()
        self.printer.close()
        self.meshCoordinates = None
        self.updateState(self.State.DISCONNECTED)

        # Break connections
        for qtConnection in self.printerQtConnections:
            self.printer.disconnect(qtConnection)
        self.printerQtConnections = []

        self.printer = None

    def switchPrinter(self):
        assert(self.printerInfo != self.printerConnectWidget.printerInfo())
        self.printerInfo = self.printerConnectWidget.printerInfo()

        try:
            self.manualWidget.setPrinter(self.printerInfo)
            self.meshWidget.resizeMesh(0, 0)
        except ValueError as valueError:
            self._fatalError(valueError.args[0])

    def updateState(self, state=None):
        if state is not None:
            self.state = state

        connected = self.printer is not None and self.printer.connected()
        busy = self.state != self.State.CONNECTED

        if not connected:
            self.printerConnectWidget.setDisconnected()
        elif busy:
            self.printerConnectWidget.setBusy()
        else:
            self.printerConnectWidget.setConnected()

        self.enumeratePortsAction.setEnabled(not connected)

        self.temperatureControlsWidget.setEnabled(connected and not busy)
        self.manualWidget.setEnabled(connected and not busy)
        self.meshWidget.setEnabled(connected and not busy)

        self.statusBar().setState(self.state)

    def getTemperatures(self):
        if not self.temperatureJobPending:
            self.temperatureJobPending = True
            self.printer.getTemperatures(self._createId('getTemperatures'))

    def updateTemperatures(self, id_, context, result):
        self.temperatureJobPending = False
        self.statusBar().setBedTemp(actual=result.bedActual, desired=result.bedDesired, power=result.bedPower)
        self.statusBar().setNozzleTemp(actual=result.toolActual, desired=result.toolDesired, power=result.toolPower)

    def _processInitResults(self, id_, context):
        for point in self.printerInfo.manualProbePoints:
            if not self.printer.isProbeable(x=point.x, y=point.y):
                self._fatalError(f'Manual probe point ({point.x}, {point.y}) is outside the probeable area.'
                                 f' Either the probe point coordinates are wrong or the printer\'s X or Y'
                                 f' axis bounds are set incorrectly.')

        self.printer.getMeshCoordinates(self._createId('getMeshCoordinates'))
        self.updateState(self.State.INITIALIZING_MESH)

    def _initializeMesh(self, id_, context, result):
        self.meshCoordinates = result.meshCoordinates
        corners = [self.meshCoordinates[0][0],
                   self.meshCoordinates[0][result.columnCount-1],
                   self.meshCoordinates[result.rowCount-1][0],
                   self.meshCoordinates[result.rowCount-1][result.columnCount-1]]

        for corner in corners:
            if not self.printer.isProbeable(x=corner.x, y=corner.y):
                self._fatalError(f'Mesh corner point ({corner.x}, {corner.y}) is outside the probeable area.'
                                 f' Either the mesh is misconfigured or the printer\'s X or Y'
                                 f' axis bounds are set incorrectly.')

        self.meshWidget.resizeMesh(result.rowCount,
                                   result.columnCount)
        self.updateState(self.State.CONNECTED)
        self.dialogs[self.Dialog.INITIALIZING].accept()

    def home(self):
        self.printer.home(self._createId('home'))
        self.updateState(self.State.HOMING)
        self.dialogs[self.Dialog.HOMING].show()

    def _finishHoming(self, id_, context):
        if not id_.startswith('home'):
            self._error('An error occurred while homing.')
        else:
            self.updateState(self.State.CONNECTED)
            self.dialogs[self.Dialog.HOMING].accept()

    def manualProbe(self, name, x, y):
        context={'type': self.State.MANUAL_PROBE,
                 'name': name}

        self.printer.probe(self._createId('probe'), context=context, x=x, y=y)
        self.dialogs[self.Dialog.PROBE].setText(f'Manually probing at ({x}, {y})')
        self.updateState(self.State.MANUAL_PROBE)
        self.dialogs[self.Dialog.PROBE].show()

    def updateMesh(self, row=0, column=0):
        if row == 0 and column == 0:
            self.meshWidget.clear()

        coordinate = self.meshCoordinates[row][column]
        self.printer.probe(self._createId('updateMesh'),
                           context = {'type': self.State.UPDATING_MESH,
                                      'row': row,
                                      'column': column},
                           x=coordinate.x,
                           y=coordinate.y)

        self.updateState(self.State.UPDATING_MESH)
        self.dialogs[self.Dialog.PROBE].setText(f'Probing mesh at row: {row}, column: {column} (x: {coordinate.x:.3f}, y: {coordinate.y:.3f})')
        self.dialogs[self.Dialog.PROBE].show()

    def _processProbe(self, id_, context, response):
        if 'type' not in context:
            self._error('Detected a printer response mismatch.')
        elif context['type'] == self.State.MANUAL_PROBE:
            assert(self.state == self.State.MANUAL_PROBE)
            self.manualWidget.reportProbe(context['name'], response)
            self.dialogs[self.Dialog.PROBE].accept()
            self.updateState(self.State.CONNECTED)
        else:
            assert(context['type'] == self.State.UPDATING_MESH and self.state == self.State.UPDATING_MESH)
            row = context['row']
            column = context['column']

            self.meshWidget.setPoint(row=row,
                                     column=column,
                                     z=response.z)

            column += 1
            if column >= len(self.meshCoordinates[0]):
                column = 0
                row += 1
                if row >= len(self.meshCoordinates):
                    row  = 0
            if row == 0 and column == 0:
                self.dialogs[self.Dialog.PROBE].accept()
                self.updateState(self.State.CONNECTED)
            else:
                self.updateMesh(row, column)

    def setBedTemperature(self, state, temp):
        self.printer.setBedTemperature(self._createId('setBedTemperature'), temperature=temp if state else 0)

    def setNozzleTemperature(self, state, temp):
        self.printer.setNozzleTemperature(self._createId('setNozzleTemperature'), temperature=temp if state else 0)

    def _cancel(self):
        """ Cancel operations that are safe to cancel """

        for dialog in self.dialogs.values():
            dialog.blockSignals(True)
            dialog.reject()
            dialog.blockSignals(False)

        self.printer.abort()
        self.updateState(self.State.CONNECTED)

    def reportPrinterError(self, type_, id_, context, message):
        self._error(message)

    def _fatalError(self, message):
        self.logger.critical(message)
        self.disconnectFromPrinter()
        for dialog in self.dialogs.values():
            dialog.blockSignals(True)
            dialog.reject()
            dialog.blockSignals(False)
        FatalErrorDialog(self, message)

    def _error(self, message):
        self.logger.error(message)
        self.disconnectFromPrinter()
        for dialog in self.dialogs.values():
            dialog.blockSignals(True)
            dialog.reject()
            dialog.blockSignals(False)
        ErrorDialog(self, message)

    def _warning(self, message):
        self.logger.warning(message)
        WarningDialog(self, message)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon((Common.baseDir() / 'Resources' / 'Icon-128x128.png').as_posix()))
    app.setApplicationName('Bed Leveler 5000')
    app.setApplicationVersion(Version.version())

    # Windows only, configure icon settings
    try:
        from ctypes import windll
        myappid = f'com.sandmmakers.bedleveler5000.{QtCore.QCoreApplication.applicationVersion()}'
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except ImportError:
        pass

    # Parse command line arguments
    parser = CommonArgumentParser(description=DESCRIPTION)
    parser.add_argument('--no-temperature-reporting', action='store_true', help='disable temperature reporting')
    args = parser.parse_args()

    # Configure logging
    Common.configureLogging(level=args.log_level, console=args.log_console, file=args.log_file)

    # Verify the printers directory exists
    if args.printers_dir is not None and not args.printers_dir.exists():
        FatalErrorDialog(None, f'Failed to find printer directory: {args.printers_dir}.')

    try:
        mainWindow = MainWindow(printersDir=args.printers_dir,
                                printer=args.printer,
                                host=args.host,
                                port=args.port,
                                noTemperatureReporting=args.no_temperature_reporting)
        mainWindow.show()
        sys.exit(app.exec())
    except KeyboardInterrupt:
        sys.exit(1)
    except Exception as exception:
        FatalErrorDialog(None, str(exception))
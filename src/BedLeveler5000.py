#!/usr/bin/env python3

from Connection import Connection
from ManualWidget import ManualWidget
from MeshWidget import MeshWidget
from TemperatureControlsWidget import TemperatureControlsWidget
from StatusBar import StatusBar
from Dialogs.HomingDialog import HomingDialog
from Dialogs.NoButtonStatusDialog import NoButtonStatusDialog
from Dialogs.ManualProbeDialog import ManualProbeDialog
from Dialogs.AboutDialog import AboutDialog
from Dialogs.WarningDialog import WarningDialog
from Dialogs.ErrorDialog import ErrorDialog
from Dialogs.FatalErrorDialog import FatalErrorDialog
from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets
from PySide6 import QtSerialPort
import argparse
from collections import namedtuple
from enum import IntEnum
from enum import StrEnum
import json
import logging
import pathlib
import sys

Point2D = namedtuple('Point2D', ['x', 'y'])

# Determine the effective base directory
BASE_DIR = pathlib.Path(sys._MEIPASS) if getattr(sys, 'frozen', False) else pathlib.Path(__file__).parent.parent

def configureLogging(level=None, console=False, file=None):
    LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    logger = logging.getLogger()
    logger.setLevel(99 if level is None else getattr(logging, level.upper()))
    formatter = logging.Formatter(LOGGING_FORMAT)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logger.level if console else 99)
    consoleHandler.setFormatter(formatter)
    logger.addHandler(consoleHandler)

    if file is not None:
        fileHandler = logging.FileHandler(file)
        fileHandler.setFormatter(formatter)
        logger.addHandler(fileHandler)

class MainWindow(QtWidgets.QMainWindow):
    class State(StrEnum):
        DISCONNECTED = 'Disconnected'
        GETTING_Z_PROBE_OFFSETS = 'Getting Z probe offsets'
        INITIAL_HOMING = 'Initial homing'
        INITIALIZING_MESH = 'Initializing mesh'
        CONNECTED = 'Connected'
        USER_HOMING = 'Homing'
        MANUAL_PROBE = 'Manually probing point'
        UPDATING_MESH = 'Updating mesh'

    def __init__(self, *args, printersDir, printer=None, port=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle(QtCore.QCoreApplication.applicationName())
        self.logger = logging.getLogger(QtCore.QCoreApplication.applicationName())

        self.connection = Connection(commonSignal=True)
        self.connection.received.connect(self._processResponse)

        self._createWidgets()
        self._layoutWidgets()
        self._createMenus()
        self._createStatusBar()
        self._createDialogs()
        self._createTimers()

        self.printersDir = printersDir
        self.loadPrinters(printer)

        self.enumeratePorts()
        if port is not None:
            portIndex = self.portComboBox.findText(port)
            if portIndex == -1:
                self._warning('Failed to find requested port.')
            else:
                self.portComboBox.setCurrentIndex(portIndex)

        self._updateState(self.State.DISCONNECTED)
        self.show()

    def loadPrinters(self, desiredPrinter=None):
        self.printerComboBox.blockSignals(True)

        self.printerComboBox.clear()

        for filePath in self.printersDir.glob('**/*.json'):
            with open(filePath, 'r') as file:
                printerInfo = json.load(file)
                printerInfo['filePath'] = filePath
                self.printerComboBox.addItem(printerInfo['displayName'], printerInfo)

        if self.printerComboBox.count() <= 0:
            self._fatalError('No printers found.')

        self.printerComboBox.blockSignals(False)

        index = 0 if desiredPrinter is None else self.printerComboBox.findText(desiredPrinter)
        if index == -1:
            self._warning('Failed to find requested printer.')
        else:
            self.printerComboBox.setCurrentIndex(index)

        # Ensure switchPrinter always gets called
        if index == 0:
            self.switchPrinter()

    def switchPrinter(self):
        try:
            self.printerInfo = self.printerComboBox.currentData()
            self.connection.setPrinter(self.printerInfo)
            self.manualWidget.setPrinter(self.printerInfo)
            self.meshWidget.resizeMesh(self.printerInfo['mesh']['rowCount'],
                                       self.printerInfo['mesh']['columnCount'])
        except ValueError as valueError:
            self._fatalError(valueError.args[0])

    def _createWidgets(self):
        # Connection widgets
        self.printerComboBox = QtWidgets.QComboBox()
        self.printerComboBox.currentIndexChanged.connect(self.switchPrinter)

        self.portComboBox = QtWidgets.QComboBox()
        self.connectButton = QtWidgets.QPushButton()
        self.homeButton = QtWidgets.QPushButton('Home')
        self.homeButton.clicked.connect(lambda : self.home(False))

        # Temperature Controls Widget
        self.temperatureControlsWidget = TemperatureControlsWidget()
        self.temperatureControlsWidget.bedHeaterChanged.connect(lambda state, temp: self.connection.sendM140('bedTemp', s=temp if state else 0))
        self.temperatureControlsWidget.nozzleHeaterChanged.connect(lambda state, temp: self.connection.sendM104('nozzleTemp', s=temp if state else 0))

        # Manual widget
        self.manualWidget = ManualWidget()
        self.manualWidget.probe.connect(lambda name, x, y: self.manualProbe(name, x, y)) # TODO: Is a lambda required here?

        # Mesh widget
        self.meshWidget = MeshWidget()
        self.meshWidget.updateMesh.connect(self.updateMesh)

        # Tab widget
        self.tabWidget = QtWidgets.QTabWidget()
        self.tabWidget.addTab(self.manualWidget, 'Manual')
        self.tabWidget.addTab(self.meshWidget, 'Mesh')

    def _layoutWidgets(self):
        # Connection layout
        connectionLayout = QtWidgets.QHBoxLayout()
        connectionLayout.addWidget(QtWidgets.QLabel('Printer:'))
        connectionLayout.addWidget(self.printerComboBox)
        connectionLayout.addWidget(QtWidgets.QLabel('Port:'))
        connectionLayout.addWidget(self.portComboBox)
        connectionLayout.addWidget(self.connectButton)
        connectionLayout.addStretch()
        connectionLayout.addWidget(self.homeButton)
        connectionGroupBox = QtWidgets.QGroupBox('Connection')
        connectionGroupBox.setLayout(connectionLayout)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(connectionGroupBox)
        layout.addWidget(self.temperatureControlsWidget)
        layout.addWidget(self.tabWidget)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def _createMenus(self):
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
        self.enumeratePortsAction.triggered.connect(self.enumeratePorts)
        self.portsMenu.addAction(self.enumeratePortsAction)
        self.menuBar().addMenu(self.portsMenu)

        self.settingsMenu = QtWidgets.QMenu('Settings', self)
        self.menuBar().addMenu(self.settingsMenu)

        self.helpMenu = QtWidgets.QMenu('Help', self)
        self.aboutAction = QtGui.QAction('About', self)
        self.aboutAction.triggered.connect(lambda : self.dialogs['about'].exec())
        self.helpMenu.addAction(self.aboutAction)
        self.aboutQtAction = QtGui.QAction('About Qt', self)
        self.aboutQtAction.triggered.connect(qApp.aboutQt)
        self.helpMenu.addAction(self.aboutQtAction)
        self.menuBar().addMenu(self.helpMenu)

    def _createStatusBar(self):
        self.setStatusBar(StatusBar())

    def _createDialogs(self):
        self.dialogs = {'homing': HomingDialog(),
                        'zProbeOffset': NoButtonStatusDialog(text='Getting probe offsets.'),
                        'initializingMesh': NoButtonStatusDialog(text='Initializing mesh.'),
                        'manualProbe': ManualProbeDialog(),
                        'updatingMesh': NoButtonStatusDialog(text='Updating mesh.'),
                        'about': AboutDialog()}

    def _createTimers(self):
        self.temperatureJobPending = False
        self.temperatureTimer = QtCore.QTimer()
        self.temperatureTimer.setInterval(1000) # TODO: Make the interval configurable
        self.temperatureTimer.timeout.connect(self.requestTemperature)

    def _processResponse(self, name, id_, context, response):
        if name in ('M104', 'M140'):
            return

        elif name == 'M105':
            assert(id_ == 'temp')
            self.temperatureJobPending -= 1
            self.statusBar().setBedTemp(response['bedActual'], response['bedDesired'])
            self.statusBar().setNozzleTemp(response['toolActual'], response['toolDesired'])

        else:
            match self.state:
                case self.State.DISCONNECTED:
                    return

                case self.State.GETTING_Z_PROBE_OFFSETS:
                    assert(id_ == 'zProbeOffsets')
                    self.zProbeOffsetX = response['x']
                    self.zProbeOffsetY = response['y']
                    self.dialogs['zProbeOffset'].accept()
                    self.home(True)

                case self.State.INITIAL_HOMING:
                    assert(id_ == 'homing')
                    self.dialogs['homing'].accept()
                    self.initMesh()

                case self.State.INITIALIZING_MESH:
                    if id_ == 'initMesh-RaiseZ':
                        self.connection.sendG42('initMesh-moveToMeshFrontLeftCoordinate', f = 3000, i = 0, j = 0)

                    elif id_ == 'initMesh-moveToMeshFrontLeftCoordinate':
                        self.connection.sendM114('initMesh-getRawMeshFrontLeftCoordinate')

                    elif id_ == 'initMesh-getRawMeshFrontLeftCoordinate':
                        self.rawMeshFrontLeftCoordinate = Point2D(response['x'], response['y'])
                        if self.rawMeshFrontLeftCoordinate == Point2D(0, 0):
                            self._error( 'The printer doesn\'t appear to have an automatic bed leveling mesh.\n' \
                                        f'Please perform automatic bed leveling and then try using {QtCore.QCoreApplication.applicationName()} again.')
                            return
                        self.connection.sendM400('initMesh-waitForMeshFrontLeftCoordinate')

                    elif id_ == 'initMesh-waitForMeshFrontLeftCoordinate':
                        self.connection.sendG42('initMesh-moveToMeshBackRightCoordinate', f = 3000,
                                                                                 i = self.printerInfo['mesh']['columnCount'] - 1,
                                                                                 j = self.printerInfo['mesh']['rowCount'] - 1)

                    elif id_ == 'initMesh-moveToMeshBackRightCoordinate':
                        self.connection.sendM400('initMesh-waitForMeshBackRightCoordinate')

                    elif id_ == 'initMesh-waitForMeshBackRightCoordinate':
                        self.connection.sendM114('initMesh-getRawMeshBackRightCoordinate')

                    elif id_ == 'initMesh-getRawMeshBackRightCoordinate':
                        self.rawMeshBackRightCoordinate = Point2D(response['x'], response['y'])

                        # Determine the mesh coordinates
                        xBase = self.rawMeshFrontLeftCoordinate.x
                        yBase = self.rawMeshFrontLeftCoordinate.y
                        xStep = (self.rawMeshBackRightCoordinate.x - self.rawMeshFrontLeftCoordinate.x) / (len(self.meshCoordinates[0]) - 1)
                        yStep = (self.rawMeshBackRightCoordinate.y - self.rawMeshFrontLeftCoordinate.y) / (len(self.meshCoordinates) - 1)
                        for row in range(self.printerInfo['mesh']['rowCount']):
                            y = yBase + row*yStep
                            for column in range(self.printerInfo['mesh']['columnCount']):
                                self.meshCoordinates[row][column] = Point2D(x = xBase + column*xStep,
                                                                            y = y)

                        self.dialogs['initializingMesh'].accept()
                        self._updateState(self.State.CONNECTED)

                    else:
                        print(f'Unknown id: {id_}')
                        assert(False)

                    self._updateState() # TODO: Determine if this is still needed

                case self.State.CONNECTED:
                    return

                case self.State.USER_HOMING:
                    assert(id_ == 'homing')
                    self.dialogs['homing'].accept()
                    self._updateState(self.State.CONNECTED)

                case self.State.MANUAL_PROBE:
                    if id_ == 'manualProbeMove':
                        self.connection.sendG30('manualProbeProbe', context=context, x=context['x'], y=context['y'])

                    elif id_ == 'manualProbeProbe':
                        self.manualWidget.reportProbe(context['name'], response)
                        self.dialogs['manualProbe'].accept()
                        self._updateState(self.State.CONNECTED)

                    else:
                        assert(False)

                case self.State.UPDATING_MESH:
                    assert(self.meshCoordinates is not None)
                    assert(id_ == 'updateMeshProbe' or id_ == 'updateMeshMove')

                    if id_ == 'updateMeshProbe':
                        # Update the mesh point
                        self.meshWidget.setPoint(row=context['row'], column=context['column'], offset=response['bed']['z'], z=response['position']['z'])

                        # Probe the next coordinate
                        context['column'] += 1
                        if context['column'] >= len(self.meshCoordinates[0]):
                            print(f'row done {context["row"]}{context["column"]}')
                            context['column'] = 0
                            context['row'] += 1
                            if context['row'] >= len(self.meshCoordinates):
                                print(f'mesh done {context["row"]}{context["column"]}')
                                self.dialogs['updatingMesh'].accept()
                                self._updateState(self.State.CONNECTED)
                                return

                    point = self.meshCoordinates[context['row']][context['column']]
                    self.connection.sendG30('updateMeshProbe', context=context, x=point.x, y=point.y)

                case _:
                    assert(False)

    @classmethod
    def _FloatToString(value):
        return f'{value}'

    def _updateState(self, state=None):
        if state is not None:
            self.state = state

        self.printerComboBox.setEnabled(not self.connection.connected())
        self.portComboBox.setEnabled(not self.connection.connected())

        self.temperatureControlsWidget.setEnabled(self.connection.connected())
        self.manualWidget.setEnabled(self.connection.connected())
        self.meshWidget.setEnabled(self.connection.connected())

        QtCore.QObject.disconnect(self.connectButton, None, None, None)
        if not self.connection.connected():
            self.connectButton.setText('Connect')
            self.connectButton.clicked.connect(lambda x: self._openSerialPort(self.portComboBox.currentText()))
        else:
            self.connectButton.setText('Disconnect')
            self.connectButton.clicked.connect(self._closeSerialPort)
        self.statusBar().setState(self.state)
        self.homeButton.setEnabled(self.connection.connected())

    def enumeratePorts(self):
        self.portComboBox.clear()
        serialPortInfoList = QtSerialPort.QSerialPortInfo.availablePorts()
        for serialPortInfo in serialPortInfoList:
            self.portComboBox.addItem(serialPortInfo.portName())

    def _openSerialPort(self, portName):
        try:
            # Open serial port
            self.connection.open(portName)

            # Start temperature monitoring
            self.temperatureTimer.start()
            self.requestTemperature()

            # Start the initialization sequence
            self.requestZProbeOffsets()

        except IOError as exception:
            print(f'Error: {exception}')

        self._updateState()

    def _closeSerialPort(self):
        self.connection.close()
        self.temperatureTimer.stop()
        self._updateState(self.State.DISCONNECTED)

    def requestTemperature(self):
        if self.temperatureJobPending <= 0:
            self.temperatureJobPending = 1
            self.connection.sendM105('temp')

    def requestZProbeOffsets(self):
        self.zProbeOffsetX = None
        self.zProbeOffsetY = None

        self.connection.sendM851('zProbeOffsets')
        self._updateState(self.State.GETTING_Z_PROBE_OFFSETS)
        self.dialogs['zProbeOffset'].show()

    def home(self, initializing):
        self.connection.sendG28('homing')
        self.dialogs['homing'].setAxes(x=True, y=True, z=True)

        self._updateState(self.State.INITIAL_HOMING if initializing else self.State.USER_HOMING)
        self.dialogs['homing'].show()

    def initMesh(self):
        self.rawMeshFrontLeftCoordinate = None
        self.rawMeshBackRightCoordinate = None
        self.meshCoordinates = [[None for column in range(self.printerInfo['mesh']['columnCount'])] for row in range(self.printerInfo['mesh']['rowCount'])]

        self.connection.sendG0('initMesh-RaiseZ', z=3)

        self._updateState(self.State.INITIALIZING_MESH)
        self.dialogs['initializingMesh'].show()

    def manualProbe(self, name, x, y):
        assert(self.connection.connected())

        context={'name': name,
                 'x': x,
                 'y': y}

        # Ensure the nozzle will not scrape the print surface
        self.connection.sendG0('manualProbeMove', context=context, z=3)

        self.dialogs['manualProbe'].setProbePoint(**context)
        self._updateState(self.State.MANUAL_PROBE)
        self.dialogs['manualProbe'].show()

    def updateMesh(self):
        assert(self.connection.connected())

        # Ensure the nozzle will not scrape the print surface
        self.connection.sendG0('updateMeshMove',
                               context={'row': 0,
                                        'column': 0},
                               z=3)

        self._updateState(self.State.UPDATING_MESH)
        self.dialogs['updatingMesh'].show()

    def _fatalError(self, message):
        self.logger.critical(message)
        self._closeSerialPort()
        for dialog in self.dialogs.values():
            dialog.reject()
        FatalErrorDialog(self, message)

    def _error(self, message):
        self.logger.error(message)
        self._closeSerialPort()
        for dialog in self.dialogs.values():
            dialog.reject()
        ErrorDialog(self, message)

    def _warning(self, message):
        self.logger.warning(message)
        WarningDialog(self, message)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon((BASE_DIR / 'Resources' / 'Icon-128x128.png').as_posix()))

    QtCore.QCoreApplication.setApplicationName('Bed Leveler 5000')
    QtCore.QCoreApplication.setApplicationVersion('0.1.3')

    # Windows only, configure icon settings
    try:
        from ctypes import windll
        myappid = f'com.sandmmakers.bedleveler5000.{QtCore.QCoreApplication.setApplicationVersion}'
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except ImportError:
        pass

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Utility for bed leveling')
    parser.add_argument('-v', '--version', action='version', version=QtCore.QCoreApplication.applicationVersion())
    parser.add_argument('--printers-dir', default=BASE_DIR / 'Printers', type=pathlib.Path, help='printer configuration directory')
    parser.add_argument('--printer', default=None, help='printer to use')
    parser.add_argument('--port', default=None, help='port to use')
    parser.add_argument('--log_level', choices=['debug', 'info', 'warning', 'error', 'critical'], default=None, help='logging level')
    parser.add_argument('--log_console', action='store_true', help='log to the console')
    parser.add_argument('--log_file', type=pathlib.Path, default=None, help='log file')

    args = parser.parse_args()

    # Configure logging
    configureLogging(level=args.log_level, console=args.log_console, file=args.log_file)

    # Verify the printers directory exists
    if args.printers_dir is not None and not args.printers_dir.exists():
        FatalErrorDialog(None, f'Failed to find printer directory: {args.printers_dir}.')

    mainWindow = MainWindow(printersDir=args.printers_dir, printer=args.printer, port=args.port)
    app.exec()
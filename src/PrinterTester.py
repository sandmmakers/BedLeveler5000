from Common.PrinterInfo import ConnectionMode
from Widgets.PrinterConnectWidget import PrinterConnectWidget
from Printers.Moonraker.MoonrakerPrinter import MoonrakerPrinter
from Printers.Marlin2.Marlin2Printer import Marlin2Printer
from Dialogs.AboutDialog import AboutDialog
from Common import Common
from Common import Version
from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets
from PySide6 import QtNetwork
import argparse
import pathlib
import signal
import sys

# Enable CTRL-C killing the application
signal.signal(signal.SIGINT, signal.SIG_DFL)

DESCRIPTION = 'Utlity for testing printer connections'

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, printersDir, *args, printer=None, host=None, port=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.nextId = 0

        # TODO: Call abort on exit

        self.qtConnections = []
        self.__createWidgets()
        self.__layoutWidgets()
        self.__createMenus()
        self.printerConnectWidget.loadPrinters(printersDir,
                                               desiredPrinter = printer,
                                               desiredHost = host,
                                               desiredPort = port)

    def __createWidgets(self):
        self.printerConnectWidget = PrinterConnectWidget(hasHomeButton=False)
        self.printerConnectWidget.connectRequested.connect(self.connectToPrinter)
        self.printerConnectWidget.disconnectRequested.connect(self.disconnectFromPrinter)

        # Controls group box
        self.controlsGroupBox = QtWidgets.QGroupBox('Controls')
        self.controlsGroupBox.setEnabled(False)

        # Init
        self.initButton = QtWidgets.QPushButton('Init')
        self.initButton.clicked.connect(self.startInit)

        # Home
        self.homeButton = QtWidgets.QPushButton('Home')
        self.homeButton.clicked.connect(self.startHome)

        # Get temperatures
        self.getTemperaturesButton = QtWidgets.QPushButton('GetTemps')
        self.getTemperaturesButton.clicked.connect(self.startGetTemperatures)

        # Get probe offsets
        self.getProbeOffsetsButton = QtWidgets.QPushButton('GetProbeOffsets')
        self.getProbeOffsetsButton.clicked.connect(self.startGetProbeOffsets)

        # Get current position
        self.getCurrentPositionButton = QtWidgets.QPushButton('GetCurrentPosition')
        self.getCurrentPositionButton.clicked.connect(self.startGetCurrentPosition)

        # Get mesh coordinates
        self.getMeshCoordinatesButton = QtWidgets.QPushButton('GetMeshCoordinates')
        self.getMeshCoordinatesButton.clicked.connect(self.startGetMeshCoordinates)

        # Abort
        self.abortButton = QtWidgets.QPushButton('Abort')
        self.abortButton.clicked.connect(self.abort)

        # Get bed temperature
        self.setBedTemperatureButton = QtWidgets.QPushButton('SetBedTemperature')
        self.setBedTemperatureButton.clicked.connect(self.startSetBedTemperature)
        self.bedTemperatureSpinBox = QtWidgets.QDoubleSpinBox()
        self.bedTemperatureSpinBox.setMinimum(0)
        self.bedTemperatureSpinBox.setMaximum(500)

        # Get nozzle temperature
        self.setNozzleTemperatureButton = QtWidgets.QPushButton('SetNozzleTemperature')
        self.setNozzleTemperatureButton.clicked.connect(self.startSetNozzleTemperature)
        self.nozzleTemperatureSpinBox = QtWidgets.QDoubleSpinBox()
        self.nozzleTemperatureSpinBox.setMinimum(0)
        self.nozzleTemperatureSpinBox.setMaximum(500)

        # Get default probe settings
        self.getDefaultProbeSampleCountButton = QtWidgets.QPushButton('GetDefaultProbeSampleCount')
        self.getDefaultProbeSampleCountButton.clicked.connect(self.startGetDefaultProbeSampleCount)
        self.getDefaultProbeZHeightButton = QtWidgets.QPushButton('GetDefaultProbeZHeight')
        self.getDefaultProbeZHeightButton.clicked.connect(self.startGetDefaultProbeZHeight)
        self.getDefaultProbeXYSpeedButton = QtWidgets.QPushButton('GetDefaultProbeXYSpeed')
        self.getDefaultProbeXYSpeedButton.clicked.connect(self.startGetDefaultProbeXYSpeed)

        # Get probe sample count
        self.getProbeSampleCountButton = QtWidgets.QPushButton('GetProbeSampleCount')
        self.getProbeSampleCountButton.clicked.connect(self.startGetProbeSampleCount)

        # Set probe sample count
        self.setProbeSampleCountButton = QtWidgets.QPushButton('SetProbeSampleCount')
        self.setProbeSampleCountButton.clicked.connect(lambda: self.printer.setProbeSampleCount(self.probeSampleCountSpinBox.value()))
        self.probeSampleCountSpinBox = QtWidgets.QSpinBox()
        self.probeSampleCountSpinBox.setValue(1)

        # Get probe Z height
        self.getProbeZHeightButton = QtWidgets.QPushButton('GetProbeZHeight')
        self.getProbeZHeightButton.clicked.connect(self.startGetProbeZHeight)

        # Set probe Z height
        self.setProbeZHeightButton = QtWidgets.QPushButton('SetProbeZHeight')
        self.setProbeZHeightButton.clicked.connect(lambda: self.printer.setProbeZHeight(self.probeZHeightSpinBox.value()))
        self.probeZHeightSpinBox = QtWidgets.QDoubleSpinBox()
        self.probeZHeightSpinBox.setValue(15)

        # Get probe XY speed
        self.getProbeXYSpeedButton = QtWidgets.QPushButton('GetProbeXYSpeed')
        self.getProbeXYSpeedButton.clicked.connect(self.startGetProbeXYSpeed)

        # Set probe XY speed
        self.setProbeXYSpeedButton = QtWidgets.QPushButton('SetProbeXYSpeed')
        self.setProbeXYSpeedButton.clicked.connect(lambda: self.printer.setProbeXYSpeed(self.probeXYSpeedSpinBox.value()))
        self.probeXYSpeedSpinBox = QtWidgets.QDoubleSpinBox()
        self.probeXYSpeedSpinBox.setMaximum(10000)
        self.probeXYSpeedSpinBox.setValue(5000)

        # Probe
        self.probeButton = QtWidgets.QPushButton("Probe")
        self.probeButton.clicked.connect(self.startProbe)
        self.probeXSpinBox = QtWidgets.QDoubleSpinBox()
        self.probeXSpinBox.setMinimum(0)
        self.probeXSpinBox.setMaximum(420)
        self.probeXSpinBox.setValue(0)
        self.probeYSpinBox = QtWidgets.QDoubleSpinBox()
        self.probeYSpinBox.setMinimum(0)
        self.probeYSpinBox.setMaximum(420)
        self.probeYSpinBox.setValue(0)

        # Move
        self.moveButton = QtWidgets.QPushButton('Move')
        self.moveButton.clicked.connect(self.startMove)
        self.moveXCheckBox = QtWidgets.QCheckBox()
        self.moveXCheckBox.setChecked(False)
        self.moveXSpinBox = QtWidgets.QDoubleSpinBox()
        self.moveXSpinBox.setMinimum(0)
        self.moveXSpinBox.setMaximum(500)
        self.moveYCheckBox = QtWidgets.QCheckBox()
        self.moveYCheckBox.setChecked(False)
        self.moveYSpinBox = QtWidgets.QDoubleSpinBox()
        self.moveYSpinBox.setMinimum(0)
        self.moveYSpinBox.setMaximum(500)
        self.moveZCheckBox = QtWidgets.QCheckBox()
        self.moveZCheckBox.setChecked(False)
        self.moveZSpinBox = QtWidgets.QDoubleSpinBox()
        self.moveZSpinBox.setMinimum(0)
        self.moveZSpinBox.setMaximum(500)
        self.moveFCheckBox = QtWidgets.QCheckBox()
        self.moveFCheckBox.setChecked(False)
        self.moveFSpinBox = QtWidgets.QDoubleSpinBox()
        self.moveFSpinBox.setMinimum(0)
        self.moveFSpinBox.setMaximum(10_000)
        self.moveWaitCheckBox = QtWidgets.QCheckBox('Wait')
        self.moveWaitCheckBox.setChecked(True)
        self.moveRelativeCheckBox = QtWidgets.QCheckBox('Relative')

        self.logTextEdit = QtWidgets.QTextEdit()
        font = self.logTextEdit.font()
        font.setFamily('Courier')
        self.logTextEdit.setFont(font)
        self.logTextEdit.setReadOnly(True)
        self.autoClearCheckBox = QtWidgets.QCheckBox('Auto clear')
        self.autoClearCheckBox.setChecked(True)
        self.clearButton = QtWidgets.QPushButton('Clear')
        self.clearButton.clicked.connect(self.clear)

    def __layoutWidgets(self):
        simpleLayout = QtWidgets.QHBoxLayout()
        simpleLayout.addWidget(self.initButton)
        simpleLayout.addWidget(self.homeButton)
        simpleLayout.addWidget(self.getTemperaturesButton)
        simpleLayout.addWidget(self.getProbeOffsetsButton)
        simpleLayout.addWidget(self.getCurrentPositionButton)
        simpleLayout.addWidget(self.getMeshCoordinatesButton)
        simpleLayout.addWidget(self.abortButton)
        simpleLayout.addStretch()

        temperatureLayout = QtWidgets.QHBoxLayout()
        temperatureLayout.addWidget(self.setBedTemperatureButton)
        temperatureLayout.addWidget(self.bedTemperatureSpinBox)
        temperatureLayout.addWidget(self.setNozzleTemperatureButton)
        temperatureLayout.addWidget(self.nozzleTemperatureSpinBox)
        temperatureLayout.addStretch()

        probeDefaultsLayout = QtWidgets.QHBoxLayout()
        probeDefaultsLayout.addWidget(self.getDefaultProbeSampleCountButton)
        probeDefaultsLayout.addWidget(self.getDefaultProbeZHeightButton)
        probeDefaultsLayout.addWidget(self.getDefaultProbeXYSpeedButton)
        probeDefaultsLayout.addStretch()

        probeSettingsLayout = QtWidgets.QHBoxLayout()
        probeSettingsLayout.addWidget(self.getProbeSampleCountButton)
        probeSettingsLayout.addWidget(self.setProbeSampleCountButton)
        probeSettingsLayout.addWidget(self.probeSampleCountSpinBox)
        probeSettingsLayout.addWidget(self.getProbeZHeightButton)
        probeSettingsLayout.addWidget(self.setProbeZHeightButton)
        probeSettingsLayout.addWidget(self.probeZHeightSpinBox)
        probeSettingsLayout.addWidget(self.getProbeXYSpeedButton)
        probeSettingsLayout.addWidget(self.setProbeXYSpeedButton)
        probeSettingsLayout.addWidget(self.probeXYSpeedSpinBox)

        probeLayout = QtWidgets.QHBoxLayout()
        probeLayout.addWidget(self.probeButton)
        probeLayout.addWidget(QtWidgets.QLabel('X:'))
        probeLayout.addWidget(self.probeXSpinBox)
        probeLayout.addWidget(QtWidgets.QLabel('Y:'))
        probeLayout.addWidget(self.probeYSpinBox)
        probeLayout.addStretch()

        moveLayout = QtWidgets.QHBoxLayout()
        moveLayout.addWidget(self.moveButton)
        moveLayout.addWidget(QtWidgets.QLabel('X:'))
        moveLayout.addWidget(self.moveXCheckBox)
        moveLayout.addWidget(self.moveXSpinBox)
        moveLayout.addWidget(QtWidgets.QLabel('Y:'))
        moveLayout.addWidget(self.moveYCheckBox)
        moveLayout.addWidget(self.moveYSpinBox)
        moveLayout.addWidget(QtWidgets.QLabel('Z:'))
        moveLayout.addWidget(self.moveZCheckBox)
        moveLayout.addWidget(self.moveZSpinBox)
        moveLayout.addWidget(QtWidgets.QLabel('F:'))
        moveLayout.addWidget(self.moveFCheckBox)
        moveLayout.addWidget(self.moveFSpinBox)
        moveLayout.addWidget(self.moveWaitCheckBox)
        moveLayout.addWidget(self.moveRelativeCheckBox)
        moveLayout.addStretch()

        controlsLayout = QtWidgets.QVBoxLayout()
        controlsLayout.addLayout(simpleLayout)
        controlsLayout.addLayout(temperatureLayout)
        controlsLayout.addLayout(probeDefaultsLayout)
        controlsLayout.addLayout(probeSettingsLayout)
        controlsLayout.addLayout(probeLayout)
        controlsLayout.addLayout(moveLayout)
        self.controlsGroupBox.setLayout(controlsLayout)

        clearLayout = QtWidgets.QHBoxLayout()
        clearLayout.addStretch()
        clearLayout.addWidget(self.autoClearCheckBox)
        clearLayout.addWidget(self.clearButton)
        clearLayout.addStretch()

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.printerConnectWidget)
        layout.addWidget(self.controlsGroupBox)
        layout.addWidget(self.logTextEdit)
        layout.addLayout(clearLayout)

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

    def connectToPrinter(self):
        if self.printerConnectWidget.connectionMode() == ConnectionMode.MARLIN_2:
            self.printer = Marlin2Printer(self.printerConnectWidget.printerInfo(), parent=self)
            kwargs = {'port': self.printerConnectWidget.port()}
        elif self.printerConnectWidget.connectionMode() == ConnectionMode.MOONRAKER:
            self.printer = MoonrakerPrinter(self.printerConnectWidget.printerInfo(), parent=self)
            kwargs = {'host': self.printerConnectWidget.host()}
        else:
            raise ValueError('Unsupported printer type detected.')

        self.qtConnections.append(self.printer.sent.connect(lambda commandType, id_, context, command: self.logTextEdit.append('Sent \'' + command + '\'')))
        self.qtConnections.append(self.printer.finished.connect(self.showFin))
        self.qtConnections.append(self.printer.errorOccurred.connect(self.showError))
        self.qtConnections.append(self.printer.homed.connect(lambda id_, context: self.logTextEdit.append(f'Homed ({id_}) : {context}')))
        self.qtConnections.append(self.printer.gotTemperatures.connect(lambda id_, context, result: self.logTextEdit.append(f'Got temperatures ({id_}) : {context} : {result}')))
        self.qtConnections.append(self.printer.gotProbeOffsets.connect(lambda id_, context, result: self.logTextEdit.append(f'Got probe offsets ({id_}) : {context} : {result}')))
        self.qtConnections.append(self.printer.gotCurrentPosition.connect(lambda id_, context, result: self.logTextEdit.append(f'Got current position ({id_}) : {context} : {result}')))
        self.qtConnections.append(self.printer.gotMeshCoordinates.connect(lambda id_, context, result: self.logTextEdit.append(f'Got mesh coordinates ({id_}) : {context} : {result}')))
        self.qtConnections.append(self.printer.bedTemperatureSet.connect(lambda id_, context: self.logTextEdit.append(f'Bed temperature set ({id_}) : {context}')))
        self.qtConnections.append(self.printer.nozzleTemperatureSet.connect(lambda id_, context: self.logTextEdit.append(f'Nozzle temperature set ({id_}) : {context}')))
        self.qtConnections.append(self.printer.gotDefaultProbeSampleCount.connect(lambda id_, context, result: self.logTextEdit.append(f'Got default probe sample count ({id_}) : {context} : {result}')))
        self.qtConnections.append(self.printer.gotDefaultProbeZHeight.connect(lambda id_, context, result: self.logTextEdit.append(f'Got default probe Z-height ({id_}) : {context} : {result}')))
        self.qtConnections.append(self.printer.gotDefaultProbeXYSpeed.connect(lambda id_, context, result: self.logTextEdit.append(f'Got default probe XY speed ({id_}) : {context} : {result}')))
        self.qtConnections.append(self.printer.probed.connect(lambda id_, context, result: self.logTextEdit.append(f'Probed ({id_}) : {context} : {result}')))
        self.qtConnections.append(self.printer.moved.connect(lambda id_, context: self.logTextEdit.append(f'Moved ({id_}) : {context}')))

        self.printer.open(**kwargs)

        self.printerConnectWidget.setConnected()
        self.controlsGroupBox.setEnabled(True)

    def disconnectFromPrinter(self):
        self.controlsGroupBox.setEnabled(False)
        self.printerConnectWidget.setDisconnected()
        self.printer.close()

        # Break connections
        for qtConnection in self.qtConnections:
            self.printer.disconnect(qtConnection)
        self.qtConnections = []

        self.printer = None

    def makeId(self, base):
        id_ = base + str(self.nextId)
        self.nextId += 1
        return id_

    def showFin(self, name, id_, context, error, result):
        self.logTextEdit.append('Finished:')
        self.logTextEdit.append(f'    Name: {name}')
        self.logTextEdit.append(f'    id_: {id_}')
        self.logTextEdit.append(f'    Context: {context}')
        self.logTextEdit.append(f'    Error: {error}')
        self.logTextEdit.append(f'    Reponse: {result}')

    def showError(self, name, id_, context, message):
        self.logTextEdit.append('Error:')
        self.logTextEdit.append(f'    Name: {name}')
        self.logTextEdit.append(f'    id_: {id_}')
        self.logTextEdit.append(f'    Context: {context}')
        self.logTextEdit.append(f'    Message: {message}')

    def start(self, name, **kwargs):
        if self.autoClearCheckBox.isChecked():
            self.logTextEdit.clear()

        getattr(self.printer, name)(self.makeId(name), **kwargs)

    def startInit(self):
        self.start('init')

    def startHome(self):
        self.start('home')

    def startGetTemperatures(self):
        self.start('getTemperatures')

    def startGetProbeOffsets(self):
        self.start('getProbeOffsets')

    def startGetCurrentPosition(self):
        self.start('getCurrentPosition')

    def startGetMeshCoordinates(self):
        self.start('getMeshCoordinates')

    def abort(self):
        if self.printer is not None:
            self.printer.abort()

    def startSetBedTemperature(self):
        self.start('setBedTemperature',
                   temperature=self.bedTemperatureSpinBox.value())

    def startSetNozzleTemperature(self):
        self.start('setNozzleTemperature',
                   temperature=self.nozzleTemperatureSpinBox.value())

    def startGetDefaultProbeSampleCount(self):
        self.start('getDefaultProbeSampleCount')

    def startGetDefaultProbeZHeight(self):
        self.start('getDefaultProbeZHeight')

    def startGetDefaultProbeXYSpeed(self):
        self.start('getDefaultProbeXYSpeed')

    def startGetProbeSampleCount(self):
        self.logTextEdit.append(f'Probe sample count: {self.printer.getProbeSampleCount()}')

    def startGetProbeZHeight(self):
        self.logTextEdit.append(f'Probe Z-height: {self.printer.getProbeZHeight()}')

    def startGetProbeXYSpeed(self):
        self.logTextEdit.append(f'Probe XY speed: {self.printer.getProbeXYSpeed()}')

    def startProbe(self):
        self.start('probe',
                   x=self.probeXSpinBox.value(),
                   y=self.probeYSpinBox.value())

    def startSetProbeSampleCount(self):
        self.start('setProbeSampleCount', count=self.probeSampleCountSpinBox.value())

    def startSetProbeZHeight(self):
        self.start('setProbeZHeight', height=self.probeZHeightSpinBox.value())

    def startSetProbeXYSpeed(self):
        self.start('setProbeXYSpeed', speed=self.probeXYSpeedSpinBox.value())

    def startMove(self):
        self.start('move',
                   x=self.moveXSpinBox.value() if self.moveXCheckBox.isChecked() else None,
                   y=self.moveYSpinBox.value() if self.moveYCheckBox.isChecked() else None,
                   z=self.moveZSpinBox.value() if self.moveZCheckBox.isChecked() else None,
                   f=self.moveFSpinBox.value() if self.moveFCheckBox.isChecked() else None,
                   wait=self.moveWaitCheckBox.isChecked(),
                   relative=self.moveRelativeCheckBox.isChecked())

    def clear(self):
        self.logTextEdit.clear()

if __name__ == '__main__':
    from Dialogs.FatalErrorDialog import FatalErrorDialog

    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName('Printer Tester')
    app.setApplicationVersion(Version.version())

    # Parse command line arguments
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-v', '--version', action='version', version=app.applicationVersion())
    parser.add_argument('--printers-dir', default=Common.baseDir() / 'Printers', type=pathlib.Path, help='printer information directory')
    parser.add_argument('--printer', default=None, help='printer to use')

    printerSpecificGroup = parser.add_mutually_exclusive_group()
    printerSpecificGroup.add_argument('--port', default=None, help='port to use for Marlin2 connection')
    printerSpecificGroup.add_argument('--host', default=None, help='host to use for Moonraker connection')

    parser.add_argument('--log-level', choices=['all', 'debug', 'info', 'warning', 'error', 'critical'], default=None, help='logging level')
    parser.add_argument('--log-console', action='store_true', help='log to the console')
    parser.add_argument('--log-file', type=pathlib.Path, default=None, help='log file')

    args = parser.parse_args()

    # Configure logging
    Common.configureLogging(level=args.log_level, console=args.log_console, file=args.log_file)

    # Verify the printers directory exists
    if args.printers_dir is not None and not args.printers_dir.exists():
        FatalErrorDialog(None, f'Failed to find printer directory: {args.printers_dir}.')

    mainWindow = MainWindow(args.printers_dir,
                            printer=args.printer,
                            host=args.host,
                            port=args.port)
    mainWindow.show()

    try:
       sys.exit(app.exec())
    except KeyboardInterrupt:
        sys.exit(1)
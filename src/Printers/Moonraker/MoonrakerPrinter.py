from Printers.CommandPrinter import CommandPrinter
from Printers.CommandPrinter import CommandType
from Printers.CommandPrinter import GetTemperaturesResult
from Printers.CommandPrinter import GetProbeOffsetsResult
from Printers.CommandPrinter import GetCurrentPositionResult
from Printers.CommandPrinter import GetMeshCoordinatesResult
from Printers.CommandPrinter import ProbeResult
from Common.Common import LOG_ALL

from PySide6 import QtCore
from PySide6 import QtNetwork
import json
import logging

class MoonrakerPrinter(CommandPrinter):
    def __init__(self, printerInfo, host=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.host = host
        self.networkAccessManager = QtNetwork.QNetworkAccessManager()

        self.isConnected = False
        self.machineSet = set()

    def _connected(self):
        return self.isConnected

    def _open(self, host=None):
        self.host = host if host is not None else self.host
        self.isConnected = True

    def _close(self):
        self.isConnected = False

    def _abort(self):
        for machine in self.machineSet:
            machine.abort()
        self.machineSet.clear()

    def _createMachine(self, machineClass, signalName, id_, context, *args, **kwargs):
        machine = machineClass(self.networkAccessManager, self.host, id_, context, parent=self, *args, **kwargs)
        machine.sent.connect(self._sent)
        machine.finished.connect(self._finished)
        machine.errorOccurred.connect(self._errorOccurred)

        machineSignal = getattr(machine, signalName)
        machineSignal.connect(getattr(self, signalName))
        self.machineSet.add(machine)
        machine.start()

    def _init(self, id_, *, context):
        self._createMachine(InitMachine, 'inited', id_, context)

    def _home(self, id_, *, context, x, y, z):
        self._createMachine(HomeMachine, 'homed', id_, context, x, y, z)

    def _getTemperatures(self, id_, *, context):
        self._createMachine(GetTemperaturesMachine, 'gotTemperatures', id_, context)

    def _getProbeOffsets(self, id_, *, context):
        self._createMachine(GetProbeOffsetsMachine, 'gotProbeOffsets', id_, context)

    def _getCurrentPosition(self, id_, *, context):
        self._createMachine(GetCurrentPositionMachine, 'gotCurrentPosition', id_, context)

    def _getMeshCoordinates(self, id_, *, context):
        self._createMachine(GetMeshCoordinatesMachine, 'gotMeshCoordinates', id_, context)

    def _setBedTemperature(self, id_, *, context, temperature):
        self._createMachine(SetBedTemperatureMachine, 'bedTemperatureSet', id_, context, temperature)

    def _setNozzleTemperature(self, id_, *, context, temperature):
        self._createMachine(SetNozzleTemperatureMachine, 'nozzleTemperatureSet', id_, context, temperature)

    def _getDefaultProbeSampleCount(self, id_, *, context):
        self._createMachine(GetDefaultProbeSampleCountMachine, 'gotDefaultProbeSampleCount', id_, context)

    def _getDefaultProbeZHeight(self, id_, *, context):
        self._createMachine(GetDefaultProbeZHeightMachine, 'gotDefaultProbeZHeight', id_, context)

    def _getDefaultProbeXYSpeed(self, id_, *, context):
        self._createMachine(GetDefaultProbeXYSpeedMachine, 'gotDefaultProbeXYSpeed', id_, context)

    def _probe(self, id_, *, context, x, y):
        self._createMachine(ProbeMachine, 'probed', id_, context, x, y, self._probeSampleCount, self._probeXYSpeed, self._probeZHeight)

    def _move(self, id_, *, context, x, y, z, e, f, wait, relative):
        self._createMachine(MoveMachine, 'moved', id_, context, x, y, z, e, f, wait, relative)

    def _sent(self, machine, command):
        self.sent.emit(machine.TYPE, machine.id_, machine.context, command)

    def _finished(self, machine, response):
        # Ignore responses for aborted machines
        if machine not in self.machineSet:
            return

        if isinstance(machine, InitMachine):
            self._probeSampleCount = machine.probeSampleCount
            self._probeZHeight = machine.probeZHeight
            self._probeXYSpeed = machine.probeXYSpeed

        self.machineSet.remove(machine)
        self.finished.emit(machine.TYPE, machine.id_, machine.context, machine.error, response)

    def _errorOccurred(self, machine, message):
        self.errorOccurred.emit(machine.TYPE, machine.id_, machine.context, message)

class MoonrakerMachine(QtCore.QObject):
    sent = QtCore.Signal(QtCore.QObject, str) # type, id, context, command
    finished = QtCore.Signal(QtCore.QObject, object) # machine, response
    errorOccurred = QtCore.Signal(QtCore.QObject, str) # machine, message

    def __init__(self, networkAccessManager, host, id_, context, parent=None):
        super().__init__(parent)

        # Get logger
        self.logger = logging.getLogger(self.__class__.__name__)

        self.networkAccessManager = networkAccessManager
        self.host = host
        self.id_ = id_
        self.context = context
        self.error = None
        self.setTransition(None)
        self.reply = None

    def setTransition(self, transition):
        self._transition = transition

    def abort(self):
        if self.reply is not None:
            self.reply.finished.disconnect()
            self.reply.abort()
            self.reply.deleteLater()
            self.reply = None

    def get(self, endpoint):
        assert(self.reply is None or self.reply.isFinished())

        command = f'http://{self.host}{endpoint}'
        self.logger.debug(f'Sending get: {command}')

        request = QtNetwork.QNetworkRequest(command)
        self.reply = self.networkAccessManager.get(request)
        self.reply.finished.connect(self.processReply)
        self.sent.emit(self, command)

    def getGCode(self, gcode):
        self.get(f'/printer/gcode/script?script={gcode}')

    def processReply(self):
        assert(self.sender() == self.reply)

        replyBuffer = self.reply.readAll()
        self.logger.log(LOG_ALL, f'Received: {replyBuffer}')

        # TODO: Add error handling on conversion and parsing
        replyJson = json.loads(str(replyBuffer, 'ascii'))
        self.logger.debug(f'Received: {replyJson}')

        errorStatus = self.reply.error()
        self.reply.deleteLater()
        self.reply = None

        # Handle REST errors
        if errorStatus != QtNetwork.QNetworkReply.NoError:
            self.errorOccurred.emit(self, 'Rest error occured.')
            return

        # Check for protocol error
        elif 'error' in replyJson:
            self.errorOccured.emit(self.NAME, self.id_, self.context, replyJson['error'])

        else: # Move to next state
            self._transition(replyJson['result'])

    def finish(self, signal, result=None):
        if result is None:
            signal.emit(self.id_, self.context)
        else:
            signal.emit(self.id_, self.context, result)
        self.finished.emit(self, result)

    def reportError(self, message):
        self.error = message
        self.errorOccurred.emit(self, message)
        self.finished.emit(self, message)

class InitMachine(MoonrakerMachine):
    TYPE = CommandType.INIT
    inited = QtCore.Signal(str, dict)

    def __init__(self, networkAccessManager, host, id_, context, parent=None):
        super().__init__(networkAccessManager, host, id_, context, parent)

        self.probeSampleCount = None
        self.probeZHeight = None
        self.probeXYSpeed = None

    def start(self):
        self.setTransition(self._enterGetConfigFile)
        self.getGCode('G28')

    def _enterGetConfigFile(self, replyJson):
        if replyJson != 'ok':
            self.reportError('Init (home) failed.')
        else:
            self.setTransition(self._enterDone)
            self.get('/printer/objects/query?configfile')

    def _enterDone(self, replyJson):
        try:
            config = replyJson['status']['configfile']['config']
            probe = config['probe']
            bedMesh = config['bed_mesh']

            self.probeSampleCount = int(probe['samples'])
            self.probeZHeight = float(bedMesh['horizontal_move_z']) + 10
            self.probeXYSpeed = float(bedMesh['speed'])
        except Exception:
            self.reportError('Init (configfile) failed.')
        else:
            self.finish(self.inited)

class HomeMachine(MoonrakerMachine):
    TYPE = CommandType.HOME
    homed = QtCore.Signal(str, dict)

    def __init__(self, networkAccessManager, host, id_, context, x, y, z, parent=None):
        super().__init__(networkAccessManager, host, id_, context, parent)
        self.x = x
        self.y = y
        self.z = z

    def start(self):
        self.setTransition(self._enterDone)

        if self.x is None and self.y is None and self.z is None:
            parts = ''
        else:
            xPart = ' X' if self.x else ''
            yPart = ' Y' if self.y else ''
            zPart = ' Z' if self.z else ''
            parts = xPart + yPart + zPart

        self.getGCode('G28' + parts)

    def _enterDone(self, replyJson):
        if replyJson != 'ok':
            self.reportError('Home failed.')
        else:
            self.finish(self.homed)

class GetTemperaturesMachine(MoonrakerMachine):
    TYPE = CommandType.GET_TEMPERATURES
    gotTemperatures = QtCore.Signal(str, dict, GetTemperaturesResult)

    def __init__(self, networkAccessManager, host, id_, context, parent=None):
        super().__init__(networkAccessManager, host, id_, context, parent)

    def start(self):
        self.setTransition(self._enterDone)
        self.get('/printer/objects/query?heater_bed&extruder')

    def _enterDone(self, replyJson):
        tool = replyJson['status']['extruder']
        bed = replyJson['status']['heater_bed']
        result = GetTemperaturesResult(toolActual = float(tool['temperature']),
                                       toolDesired = float(tool['target']),
                                       toolPower = float(tool['power']),
                                       bedActual = float(bed['temperature']),
                                       bedDesired = float(bed['target']),
                                       bedPower = float(bed['power']))

        self.finish(self.gotTemperatures, result)

class GetProbeOffsetsMachine(MoonrakerMachine):
    TYPE = CommandType.GET_PROBE_OFFSETS
    gotProbeOffsets = QtCore.Signal(str, dict, GetProbeOffsetsResult)

    def __init__(self, networkAccessManager, host, id_, context, parent=None):
        super().__init__(networkAccessManager, host, id_, context, parent)

    def start(self):
        self.setTransition(self._enterDone)
        self.get('/printer/objects/query?probe')

    def _enterDone(self, replyJson):
        probe = replyJson['status']['probe']

        result = GetProbeOffsetsResult(xOffset = float(probe['x_offset']),
                                       yOffset = float(probe['y_offset']),
                                       zOffset = float(probe['z_offset']))

        self.finish(self.gotProbeOffsets, result)

class GetCurrentPositionMachine(MoonrakerMachine):
    TYPE = CommandType.GET_CURRENT_POSITION
    gotCurrentPosition = QtCore.Signal(str, dict, GetCurrentPositionResult)

    def __init__(self, networkAccessManager, host, id_, context, parent=None):
        super().__init__(networkAccessManager, host, id_, context, parent)

    def start(self):
        self.setTransition(self._enterDone)
        self.get('/printer/objects/query?gcode_move')

    def _enterDone(self, replyJson):
        position = replyJson['status']['gcode_move']['gcode_position']

        result = GetCurrentPositionResult(x = float(position[0]),
                                          y = float(position[1]),
                                          z = float(position[2]),
                                          e = float(position[3]))

        self.finish(self.gotCurrentPosition, result)

class GetMeshCoordinatesMachine(MoonrakerMachine):
    TYPE = CommandType.GET_MESH_COORDINATES
    gotMeshCoordinates = QtCore.Signal(str, dict, GetMeshCoordinatesResult)

    def __init__(self, networkAccessManager, host, id_, context, parent=None):
        super().__init__(networkAccessManager, host, id_, context, parent)

    def start(self):
        self.setTransition(self._enterDone)
        self.get('/printer/objects/query?bed_mesh')

    def _enterDone(self, replyJson):
        bed_mesh = replyJson['status']['bed_mesh']
        profile_name = bed_mesh['profile_name']
        profile = bed_mesh['profiles'][profile_name]['mesh_params']

        self.finish(self.gotMeshCoordinates, CommandPrinter.calculateMeshCoordinates(rowCount = int(profile['y_count']),
                                                                                     columnCount = int(profile['x_count']),
                                                                                     minX = float(profile['min_x']),
                                                                                     maxX = float(profile['max_x']),
                                                                                     minY = float(profile['min_y']),
                                                                                     maxY = float(profile['max_y'])))

class SetBedTemperatureMachine(MoonrakerMachine):
    TYPE = CommandType.SET_BED_TEMPERATURE
    bedTemperatureSet = QtCore.Signal(str, dict)

    def __init__(self, networkAccessManager, host, id_, context, temp, parent=None):
        super().__init__(networkAccessManager, host, id_, context, parent=None)
        self.temp = temp

    def start(self):
        self.setTransition(self._enterDone)
        self.getGCode(f'M140 S{self.temp}')

    def _enterDone(self, replyJson):
        if replyJson != 'ok':
            self.reportError('Set bed temperature failed.')
        else:
            self.finish(self.bedTemperatureSet)

class SetNozzleTemperatureMachine(MoonrakerMachine):
    TYPE = CommandType.SET_NOZZLE_TEMPERATURE
    nozzleTemperatureSet = QtCore.Signal(str, dict)

    def __init__(self, networkAccessManager, host, id_, context, temp, parent=None):
        super().__init__(networkAccessManager, host, id_, context, parent)
        self.temp = temp

    def start(self):
        self.setTransition(self._enterDone)
        self.getGCode(f'M104 S{self.temp}')

    def _enterDone(self, replyJson):
        if replyJson != 'ok':
            self.reportError('Set nozzle temperature failed.')
        else:
            self.finish(self.nozzleTemperatureSet)

class GetDefaultProbeSampleCountMachine(MoonrakerMachine):
    TYPE = CommandType.GET_DEFAULT_PROBE_SAMPLE_COUNT
    gotDefaultProbeSampleCount = QtCore.Signal(str, dict, int)

    def __init__(self, networkAccessManager, host, id_, context, parent=None):
        super().__init__(networkAccessManager, host, id_, context, parent)

    def start(self):
        self.setTransition(self._enterDone)
        self.get('/printer/objects/query?configfile')

    def _enterDone(self, replyJson):
        probe = replyJson['status']['configfile']['config']['probe']
        self.finish(self.gotDefaultProbeSampleCount, int(probe['samples']))

class GetDefaultProbeZHeightMachine(MoonrakerMachine):
    TYPE = CommandType.GET_DEFAULT_PROBE_Z_HEIGHT
    gotDefaultProbeZHeight = QtCore.Signal(str, dict, float)

    def __init__(self, networkAccessManager, host, id_, context, parent=None):
        super().__init__(networkAccessManager, host, id_, context, parent)

    def start(self):
        self.setTransition(self._enterDone)
        self.get('/printer/objects/query?configfile')

    def _enterDone(self, replyJson):
        bedMesh = replyJson['status']['configfile']['config']['bed_mesh']
        self.finish(self.gotDefaultProbeZHeight, float(bedMesh['horizontal_move_z']))

class GetDefaultProbeXYSpeedMachine(MoonrakerMachine):
    TYPE = CommandType.GET_DEFAULT_PROBE_XY_SPEED
    gotDefaultProbeXYSpeed = QtCore.Signal(str, dict, float)

    def __init__(self, networkAccessManager, host, id_, context, parent=None):
        super().__init__(networkAccessManager, host, id_, context, parent)

    def start(self):
        self.setTransition(self._enterDone)
        self.get('/printer/objects/query?configfile')

    def _enterDone(self, replyJson):
        bedMesh = replyJson['status']['configfile']['config']['bed_mesh']
        self.finish(self.gotDefaultProbeXYSpeed, float(bedMesh['speed']))

class ProbeMachine(MoonrakerMachine):
    TYPE = CommandType.PROBE
    probed = QtCore.Signal(str, dict, ProbeResult)

    def __init__(self, networkAccessManager, host, id_, context, x, y, sampleCount, xySpeed, probeHeight, parent=None):
        super().__init__(networkAccessManager, host, id_, context, parent)

        assert(sampleCount is not None)
        assert(xySpeed is not None)
        assert(probeHeight is not None)

        self.x = x
        self.y = y
        self.sampleCount = sampleCount
        self.xySpeed = xySpeed
        self.probeHeight = probeHeight
        self.xOffset = None
        self.yOffset = None

    def start(self):
        self.setTransition(self._enterRaise)
        self.get('/printer/objects/query?probe')

    def _enterRaise(self, replyJson):
        try:
            probe = replyJson['status']['probe']
            self.xOffset = float(probe['x_offset'])
            self.yOffset = float(probe['y_offset'])
        except:
            self.reportError('Probe (query) failed.')
        else:
            self.setTransition(self._enterWaitForRaise)
            self.getGCode(f'G0 Z{self.probeHeight}')

    def _enterWaitForRaise(self, replyJson):
        if replyJson != 'ok':
            self.reportError('Probe (raise) failed.')
        else:
            self.setTransition(self._enterMove)
            self.getGCode(f'M400')

    def _enterMove(self, replyJson):
        self.setTransition(self._enterWaitForMove)
        self.getGCode(f'G0 X{self.x - self.xOffset} Y{self.y - self.yOffset} F{60*self.xySpeed}')

    def _enterWaitForMove(self, replyJson):
        if replyJson != 'ok':
            self.reportError('Probe (move) failed.')
        else:
            self.setTransition(self._enterProbe)
            self.getGCode(f'M400')

    def _enterProbe(self, replyJson):
        if replyJson != 'ok':
            self.reportError('Probe (wait for move) failed.')
        else:
            self.setTransition(self._enterGetResult)
            self.getGCode(f'PROBE SAMPLES={self.sampleCount}') # TODO: Add more configuration parameters (see https://www.klipper3d.org/G-Codes.html#additional-commands)

    def _enterGetResult(self, replyJson):
        if replyJson != 'ok':
            self.reportError('Probe (probe) failed.')
        else:
            self.setTransition(self._enterDone)
            self.get('/printer/objects/query?probe')

    def _enterDone(self, replyJson):
        probe = replyJson['status']['probe']
        result = ProbeResult(x=self.x, y=self.y, z=probe['last_z_result'])

        self.finish(self.probed, result)

class MoveMachine(MoonrakerMachine):
    TYPE = CommandType.MOVE
    moved = QtCore.Signal(str, dict)

    def __init__(self, networkAccessManager, host, id_, context, x, y, z, e, f, wait, relative, parent=None):
        super().__init__(networkAccessManager, host, id_, context, parent)
        self.x = x
        self.y = y
        self.z = z
        self.e = e
        self.f = f
        self.wait = wait
        self.relative = relative

    def start(self):
        self.setTransition(self._enterMove)
        self.getGCode('G91' if self.relative else 'G90')

    def _enterMove(self, replyJson):
        if replyJson != 'ok':
            self.reportError('Move (mode) failed.')
        else:
            self.setTransition(self._enterWait if self.wait else self._enterDone)

            xPart = f' X{self.x}' if self.x is not None else ''
            yPart = f' Y{self.y}' if self.y is not None else ''
            zPart = f' Z{self.z}' if self.z is not None else ''
            ePart = f' E{self.e}' if self.e is not None else ''
            fPart = f' F{self.f}' if self.f is not None else ''
            self.getGCode('G0' + xPart + yPart + zPart + ePart + fPart)

    def _enterWait(self, replyJson):
        if replyJson != 'ok':
            self.reportError('Move (move) failed.')
        else:
            self.setTransition(self._enterDone)
            self.getGCode('M400')

    def _enterDone(self, replyJson):
        if replyJson != 'ok':
            self.reportError('Move failed.')
        else:
            self.finish(self.moved)
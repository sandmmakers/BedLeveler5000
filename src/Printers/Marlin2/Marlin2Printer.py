from ..CommandPrinter import CommandPrinter
from ..CommandPrinter import CommandType
from ..CommandPrinter import GetTemperaturesResult
from ..CommandPrinter import GetProbeOffsetsResult
from ..CommandPrinter import GetCurrentPositionResult
from ..CommandPrinter import GetBoundsResult
from ..CommandPrinter import GetMeshCoordinatesResult
from ..CommandPrinter import ProbeResult
from .CommandConnection import CommandConnection

from PySide6 import QtCore
from PySide6 import QtNetwork
import logging
import statistics

class Marlin2Printer(CommandPrinter):
    # Hardcoded default value since Marlin 2 doesn't support querying for them
    DEFAULT_PROBE_SAMPLE_COUNT = 1
    DEFAULT_PROBE_XY_SPEED = 5000
    DEFAULT_PROBE_Z_HEIGHT = 10

    def __init__(self, printerInfo, port=None, *args,  **kwargs):
        super().__init__(*args, **kwargs)

        self.port = port
        self.commandConnection = CommandConnection(printerInfo=printerInfo)

        self.machineSet = set()

    def _connected(self):
        return self.commandConnection.connected()

    def _open(self, port=None):
        self.port = port if port is not None else self.port
        self.commandConnection.open(self.port)

    def _close(self):
        self.commandConnection.close()

    def abort(self):
        for machine in self.machineSet:
            machine.abort()
        self.machineSet.clear()

    def _createMachine(self, machineClass, signalName, id_, context, *args, **kwargs):
        machine = machineClass(self.commandConnection, id_, context, *args, **kwargs)
        machine.sent.connect(self._sent)
        machine.finished.connect(self._finished)
        machine.errorOccurred.connect(self._errorOccurred)

        if machineClass != InitMachine:
            machineSignal = getattr(machine, signalName)
            machineSignal.connect(getattr(self, signalName))
        else:
            machine.inited.connect(self._inited)

        self.machineSet.add(machine)
        logging.debug(f'Starting {machineClass} with id: {id_}, context: {context}')
        machine.start()

    def _inited(self, id_, context):
        machine = self.sender()

        # Probe offsets
        self._probeXOffset = machine.probeXOffset
        self._probeYOffset = machine.probeYOffset
        self._probeZOffset = machine.probeZOffset

        # Travel bounds
        self._travelBoundsMinX = machine.travelBoundsMinX
        self._travelBoundsMaxX = machine.travelBoundsMaxX
        self._travelBoundsMinY = machine.travelBoundsMinY
        self._travelBoundsMaxY = machine.travelBoundsMaxY
        self._travelBoundsMinZ = machine.travelBoundsMinZ
        self._travelBoundsMaxZ = machine.travelBoundsMaxZ

        self.inited.emit(id_, context)

    def _init(self, id_, *, context):
        self._probeSampleCount = self.DEFAULT_PROBE_SAMPLE_COUNT
        self._probeZHeight = self.DEFAULT_PROBE_Z_HEIGHT
        self._probeXYSpeed = self.DEFAULT_PROBE_XY_SPEED
        self._createMachine(InitMachine, 'inited', id_, context)

    def _home(self, id_, *, context, x, y, z):
        self._createMachine(HomeMachine, 'homed', id_, context, x, y, z)

    def _getTemperatures(self, id_, *, context):
        self._createMachine(GetTemperaturesMachine, 'gotTemperatures', id_, context)

    def _getProbeOffsets(self, id_, *, context):
        self._createMachine(GetProbeOffsetsMachine, 'gotProbeOffsets', id_, context)

    def _getCurrentPosition(self, id_, *, context):
        self._createMachine(GetCurrentPositionMachine, 'gotCurrentPosition', id_, context)

    def _getTravelBounds(self, id_, *, context):
        self._createMachine(GetTravelBoundsMachine, 'gotTravelBounds', id_, context)

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
        self.machineSet.remove(machine)
        self.finished.emit(machine.TYPE, machine.id_, machine.context, machine.error, response)

    def _errorOccurred(self, machine, message):
        self.errorOccurred.emit(machine.TYPE, machine.id_, machine.context, message)

class Marlin2Machine(QtCore.QObject):
    sent = QtCore.Signal(QtCore.QObject, str) # machine, command
    finished = QtCore.Signal(QtCore.QObject, object) # machine, response
    errorOccurred = QtCore.Signal(QtCore.QObject, str) # machine, message

    def __init__(self, commandConnection, id_, context, parent=None):
        super().__init__(parent)

        self.commandConnection = commandConnection

        self.id_ = id_
        self.context = context
        self.error = None
        self.setTransition(None)
        self.command = None

    def setTransition(self, transition):
        self._transition = transition

    def abort(self):
        if self.command is not None:
            self.command.finished.disconnect()
            self.command.errorOccurred.disconnect()
            self.command.deleteLater()
            self.command = None

    def processReply(self, command):
        assert(command == self.command)

        error = self.command.error
        self.command.deleteLater()
        self.command = None

        # Handle errors
        if error is not None:
            self.error = error
            self.errorOccurred.emit(self, error)
        else: # Move to next state
            self._transition(command.result)

    def setCommand(self, command):
        self.command = command
        self.sent.emit(self, command.request)
        self.command.finished.connect(self.processReply)

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

    @staticmethod
    def stringIsInteger(value):
        try:
            float(value)
        except ValueError:
            return False
        else:
            return float(value).is_integer()

class InitMachine(Marlin2Machine):
    TYPE = CommandType.INIT
    inited = QtCore.Signal(str, dict)

    def __init__(self, commandConnection, id_, context, parent=None):
        super().__init__(commandConnection, id_, context, parent)

    def start(self):
        self.setTransition(self._enterGetProbeOffsets)
        self.setCommand(self.commandConnection.sendG28())

    def _enterGetProbeOffsets(self, reply):
        self.setTransition(self._enterGetTravelBounds)
        self.setCommand(self.commandConnection.sendM851())

    def _enterGetTravelBounds(self, reply):
        self.probeXOffset = reply['x']
        self.probeYOffset = reply['y']
        self.probeZOffset = reply['z']

        self.setTransition(self._enterAbsolutePositioning)
        self.setCommand(self.commandConnection.sendM211())

    def _enterAbsolutePositioning(self, reply):
        self.travelBoundsMinX = reply['minX']
        self.travelBoundsMaxX = reply['maxX']
        self.travelBoundsMinY = reply['minY']
        self.travelBoundsMaxY = reply['maxY']
        self.travelBoundsMinZ = reply['minZ']
        self.travelBoundsMaxZ = reply['maxZ']

        self.setTransition(self._enterDone)
        self.setCommand(self.commandConnection.sendG90())

    def _enterDone(self, reply):
        self.finish(self.inited)

class HomeMachine(Marlin2Machine):
    TYPE = CommandType.HOME
    homed = QtCore.Signal(str, dict)

    def __init__(self, commandConnection, id_, context, x, y, z, parent=None):
        super().__init__(commandConnection, id_, context, parent)
        self.x = x
        self.y = y
        self.z = z

    def start(self):
        self.setTransition(self._enterDone)
        self.setCommand(self.commandConnection.sendG28(x=self.x, y=self.y, z=self.z))

    def _enterDone(self, reply):
        self.finish(self.homed)

class GetTemperaturesMachine(Marlin2Machine):
    TYPE = CommandType.GET_TEMPERATURES
    gotTemperatures = QtCore.Signal(str, dict, GetTemperaturesResult)

    def __init__(self, commandConnection, id_, context, parent=None):
        super().__init__(commandConnection, id_, context, parent)

    def start(self):
        self.setTransition(self._enterDone)
        self.setCommand(self.commandConnection.sendM105())

    def _enterDone(self, reply):
        self.finish(self.gotTemperatures, GetTemperaturesResult(toolActual = reply['toolActual'],
                                                                toolDesired = reply['toolDesired'],
                                                                toolPower = reply['toolPower'] / 127,
                                                                bedActual = reply['bedActual'],
                                                                bedDesired = reply['bedDesired'],
                                                                bedPower = reply['bedPower'] / 127))

class GetProbeOffsetsMachine(Marlin2Machine):
    TYPE = CommandType.GET_PROBE_OFFSETS
    gotProbeOffsets = QtCore.Signal(str, dict, GetProbeOffsetsResult)

    def __init__(self, commandConnection, id_, context, parent=None):
        super().__init__(commandConnection, id_, context, parent)

    def start(self):
        self.setTransition(self._enterDone)
        self.setCommand(self.commandConnection.sendM851())

    def _enterDone(self, reply):
        self.finish(self.gotProbeOffsets, GetProbeOffsetsResult(xOffset = reply['x'],
                                                                yOffset = reply['y'],
                                                                zOffset = reply['z']))

class GetCurrentPositionMachine(Marlin2Machine):
    TYPE = CommandType.GET_CURRENT_POSITION
    gotCurrentPosition = QtCore.Signal(str, dict, GetCurrentPositionResult)

    def __init__(self, commandConnection, id_, context, parent=None):
        super().__init__(commandConnection, id_, context, parent)

    def start(self):
        self.setTransition(self._enterDone)
        self.setCommand(self.commandConnection.sendM114())

    def _enterDone(self, reply):
        self.finish(self.gotCurrentPosition, GetCurrentPositionResult(x = reply['x'],
                                                                      y = reply['y'],
                                                                      z = reply['z'],
                                                                      e = reply['e']))

class GetTravelBoundsMachine(Marlin2Machine):
    TYPE = CommandType.GET_TRAVEL_BOUNDS
    gotTravelBounds = QtCore.Signal(str, dict, GetBoundsResult)

    def __init__(self, commandConnection, id_, context, parent=None):
        super().__init__(commandConnection, id_, context, parent)

    def start(self):
        self.setTransition(self._enterDone)
        self.setCommand(self.commandConnection.sendM211())

    def _enterDone(self, reply):
        self.finish(self.gotTravelBounds, GetBoundsResult(minX = reply['minX'],
                                                          maxX = reply['maxX'],
                                                          minY = reply['minY'],
                                                          maxY = reply['maxY'],
                                                          minZ = reply['minZ'],
                                                          maxZ = reply['maxZ']))

class GetMeshCoordinatesMachine(Marlin2Machine):
    TYPE = CommandType.GET_MESH_COORDINATES
    gotMeshCoordinates = QtCore.Signal(str, dict, GetMeshCoordinatesResult)

    def __init__(self, commandConnection, id_, context, parent=None):
        super().__init__(commandConnection, id_, context, parent)
        self.xCount = None
        self.yCount = 0
        self.frontLeftX = None
        self.frontLeftY = None
        self.speed = 5000

    def start(self):
        self.setTransition(self._enterGetMeshSize)
        self.setCommand(self.commandConnection.sendM420(v=True))

    def _enterGetMeshSize(self, reply):
        """ Currently only supports bilinear bed leveling. """

        # Determine xCount and yCount
        foundBilinear = False
        for line in reply['response']:
            # Skip echo lines
            if line.startswith('echo:'):
                continue
            elif not foundBilinear:
                if 'Bilinear Leveling Grid:' in line:
                    foundBilinear = True
                else:
                    self.reportError('Detected an unexpected line.')
                    return
            else:
                tokens = line.split()
                if len(tokens) == 0 and \
                   foundBilinear and \
                   self.xCount is not None and \
                   self.yCount is not None:
                    break

                if len(tokens) > 0:
                    if self.stringIsInteger(tokens[0]):
                        if self.xCount is None:
                            if not self.stringIsInteger(tokens[-1]) or int(tokens[-1]) != len(tokens) - 1:
                                self.reportError('Detected an unexpected line.')
                                return
                            self.xCount = len(tokens)
                        else:
                            if len(tokens) - 1 != self.xCount or int(tokens[0]) != self.yCount:
                                self.reportError('Detected an unexpected line.')
                                return
                            self.yCount += 1

        if foundBilinear == False:
            self.reportError('No mesh found. Please perform automatic bed leveling and try again.')
        elif self.xCount is None or self.yCount == 0:
            self.reportError('Failed to parse the M420 output.')
        else:
            self.setTransition(self._enterMoveToFrontLeftPosition)
            self.setCommand(self.commandConnection.sendG0(z=20))

    def _enterMoveToFrontLeftPosition(self, reply):
        self.setTransition(self._enterWaitForFrontLeft)
        self.setCommand(self.commandConnection.sendG42(i=0, j=0, f=self.speed))

    def _enterWaitForFrontLeft(self, reply):
        self.setTransition(self._enterGetFrontLeftPosition)
        self.setCommand(self.commandConnection.sendM400())

    def _enterGetFrontLeftPosition(self, reply):
        self.setTransition(self._enterMoveToBackRightPosition)
        self.setCommand(self.commandConnection.sendM114())

    def _enterMoveToBackRightPosition(self, reply):
        try:
            self.frontLeftX = reply['x']
            self.frontLeftY = reply['y']
        except:
            self.reportError('Failed to parse result of M114 command.')
            return

        self.setTransition(self._enterWaitForBackRight)
        self.setCommand(self.commandConnection.sendG42(i=self.xCount-1, j=self.yCount-1, f=self.speed))

    def _enterWaitForBackRight(self, reply):
        self.setTransition(self._enterGetBackRightPosition)
        self.setCommand(self.commandConnection.sendM400())

    def _enterGetBackRightPosition(self, reply):
        self.setTransition(self._enterDone)
        self.setCommand(self.commandConnection.sendM114())

    def _enterDone(self, reply):
        try:
            backRightX = float(reply['x'])
            backRightY = float(reply['y'])
        except:
            self.reportError('Failed to parse result of M114 command.')
            return

        self.finish(self.gotMeshCoordinates, CommandPrinter.calculateMeshCoordinates(rowCount = self.yCount,
                                                                                     columnCount = self.xCount,
                                                                                     minX = self.frontLeftX,
                                                                                     minY = self.frontLeftY,
                                                                                     maxX = backRightX,
                                                                                     maxY = backRightY))

class SetBedTemperatureMachine(Marlin2Machine):
    TYPE = CommandType.SET_BED_TEMPERATURE
    bedTemperatureSet = QtCore.Signal(str, dict)

    def __init__(self, commandConnection, id_, context, temp, parent=None):
        super().__init__(commandConnection, id_, context, parent)
        self.temp = temp

    def start(self):
        self.setTransition(self._enterDone)
        self.setCommand(self.commandConnection.sendM140(s=self.temp))

    def _enterDone(self, reply):
        self.finish(self.bedTemperatureSet)

class SetNozzleTemperatureMachine(Marlin2Machine):
    TYPE = CommandType.SET_NOZZLE_TEMPERATURE
    nozzleTemperatureSet = QtCore.Signal(str, dict)

    def __init__(self, commandConnection, id_, context, temp, parent=None):
        super().__init__(commandConnection, id_, context, parent)
        self.temp = temp

    def start(self):
        self.setTransition(self._enterDone)
        self.setCommand(self.commandConnection.sendM104(s=self.temp))

    def _enterDone(self, reply):
        self.finish(self.nozzleTemperatureSet)

class GetDefaultProbeSampleCountMachine(Marlin2Machine):
    TYPE = CommandType.GET_DEFAULT_PROBE_SAMPLE_COUNT
    gotDefaultProbeSampleCount = QtCore.Signal(str, dict, int)

    def __init__(self, commandConnection, id_, context, parent=None):
        super().__init__(commandConnection, id_, context, parent)

    def start(self):
        self.finish(self.gotDefaultProbeSampleCount, Marlin2Printer.DEFAULT_PROBE_SAMPLE_COUNT)

class GetDefaultProbeZHeightMachine(Marlin2Machine):
    TYPE = CommandType.GET_DEFAULT_PROBE_Z_HEIGHT
    gotDefaultProbeZHeight = QtCore.Signal(str, dict, float)

    def __init__(self, commandConnection, id_, context, parent=None):
        super().__init__(commandConnection, id_, context, parent)

    def start(self):
        self.finish(self.gotDefaultProbeZHeight, Marlin2Printer.DEFAULT_PROBE_Z_HEIGHT)

class GetDefaultProbeXYSpeedMachine(Marlin2Machine):
    TYPE = CommandType.GET_DEFAULT_PROBE_XY_SPEED
    gotDefaultProbeXYSpeed = QtCore.Signal(str, dict, float)

    def __init__(self, commandConnection, id_, context, parent=None):
        super().__init__(commandConnection, id_, context, parent)

    def start(self):
        self.finish(self.gotDefaultProbeXYSpeed, Marlin2Printer.DEFAULT_PROBE_XY_SPEED)

class ProbeMachine(Marlin2Machine):
    """ Probe samples are averaged. """

    TYPE = CommandType.PROBE
    probed = QtCore.Signal(str, dict, ProbeResult)

    def __init__(self, commandConnection, id_, context, x, y, sampleCount, xySpeed, probeHeight, parent=None):
        super().__init__(commandConnection, id_, context, parent)
        self.x = x
        self.y = y
        self.sampleCount = sampleCount
        self.xySpeed = xySpeed
        self.probeHeight = probeHeight
        self.sampleList = []
        self.xOffset = None
        self.yOffset = None

        assert(self.sampleCount >= 1)
        assert(self.probeHeight >= 0.0)

    def start(self):
        self.setTransition(self._enterMove)
        self.setCommand(self.commandConnection.sendM851())

    def _enterMove(self, reply):
        if self.xOffset is None or self.yOffset is None:
            try:
                self.xOffset = float(reply['x'])
                self.yOffset = float(reply['y'])
            except:
                self.reportError('Failed to parse output of M851 command.')
                return

        self.setTransition(self._enterProbe)
        self.setCommand(self.commandConnection.sendG0(x=self.x - self.xOffset, y=self.y - self.yOffset, z=self.probeHeight, f=self.xySpeed))

    def _enterProbe(self, reply):
        self.setTransition(self._enterDone)
        self.setCommand(self.commandConnection.sendG30(e=True, x=self.x, y=self.y))

    def _enterDone(self, reply):
        try:
            self.sampleList.append(reply['bed']['z'])
        except:
            self.reportError('Failed to process output of G30 command.')
        else:
            if len(self.sampleList) < self.sampleCount:
                self._enterMove(None)
            else:
                result = ProbeResult(x=self.x, y=self.y, z=statistics.mean(self.sampleList))
                self.finish(self.probed, result)

class MoveMachine(Marlin2Machine):
    TYPE = CommandType.MOVE
    moved = QtCore.Signal(str, dict)

    def __init__(self, commandConnection, id_, context, x, y, z, e, f, wait, relative, parent=None):
        super().__init__(commandConnection, id_, context, parent)
        self.x = x
        self.y = y
        self.z = z
        self.e = e
        self.f = f
        self.wait = wait
        self.relative = relative

    def start(self):
        self.setTransition(self._enterMove)
        if self.relative:
            self.setCommand(self.commandConnection.sendG91())
        else:
            self.setCommand(self.commandConnection.sendG90())

    def _enterMove(self, reply):
        self.setTransition(self._enterWait if self.wait else self._enterDone)
        self.setCommand(self.commandConnection.sendG0(x=self.x, y=self.y, z=self.z, e=self.e, f=self.f))

    def _enterWait(self, reply):
        self.setTransition(self._enterDone)
        self.setCommand(self.commandConnection.sendM400())

    def _enterDone(self, reply):
        self.finish(self.moved)
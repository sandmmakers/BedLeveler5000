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
from typing import NamedTuple

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

        logging.debug(f'Starting {machineClass} with id: {id_}, context: {context}')
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

    class ConfigSection(NamedTuple):
        name: str
        data: dict

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

        # Check for protocol error
        if 'error' in replyJson and 'message' in replyJson['error']:
            message = replyJson['error']['message']
            self.error = message
            logging.error(f'Error {replyJson}')
            self.errorOccurred.emit(self, message)
            self.finished.emit(self, message)

        # Handle REST errors
        elif errorStatus != QtNetwork.QNetworkReply.NoError:
            message = f'Rest error occured ({errorStatus}).'
            logging.error(message)
            self.errorOccurred.emit(self, message)
            return

        else: # Move to next state
            logging.debug(f'Entering {self._transition.__qualname__}' \
                          f' Id: {self.id_}' \
                          f' Context: {self.context}' \
                          f' Reply: {replyJson}')

            try:
                self._transition(replyJson['result'])
            except ValueError as exception:
                message = str(exception)
                self.error = message
                logging.error(message)
                self.errorOccurred.emit(self, message)
                self.finished.emit(self, message)

    def finish(self, signal, result=None):
        if result is None:
            signal.emit(self.id_, self.context)
        else:
            signal.emit(self.id_, self.context, result)
        self.finished.emit(self, result)

    @staticmethod
    def _fieldsToString(fieldList):
        return '[\'' + '\'][\''.join(fieldList) + '\']'

    @classmethod
    def _getField(cls, input_, fieldList, type_=None):
        foundFieldList = []
        result = input_

        for field in fieldList:
            foundFieldList.append(field)
            result = result.get(field)
            if result is None:
                fields = cls._fieldsToString(foundFieldList)
                raise ValueError(f'Failed to find field: {fields}.')

        if type_ is None:
            return result

        try:
            return type_(result)
        except Exception as exception:
            fieldsString = cls._fieldsToString(foundFieldList)
            raise ValueError(f'Falied to convert {fieldsString} to {type_.__qualname__}.')

    @staticmethod
    def _safeConvert(type_, value):
        try:
            return type_(value)
        except:
            return None

    @staticmethod
    def _verifyOk(reply, message):
        if reply != 'ok':
            raise ValueError(message)

    @classmethod
    def _getConfig(cls, replyJson):
        configPath = ['status', 'configfile', 'config']
        return cls._getField(replyJson, configPath)

    @classmethod
    def _getConfigSection(cls, config, sectionName):
        section = config.get(sectionName)
        if section is None:
            raise ValueError(f'{cls.__name__[:-len("Machine")]} failed, \'{sectionName}\' section not found in \'printer.cfg\'.')
        return cls.ConfigSection(sectionName, section)

    @classmethod
    def _getConfigSectionValue(cls, section, valueName, type_=None, default=None):
        value = section.data.get(valueName, default)
        if value is None:
            raise ValueError(f'{cls.__name__[:-len("Machine")]} failed, \'{valueName}\' field not found in \'{section.name}\' section of \'printer.cfg\'.')
        if type_ is not None:
            value = cls._safeConvert(type_, value)
            if value is None:
                raise ValueError(f'{cls.__name__[:-len("Machine")]} failed, invalid value for \'{section.name}:{valueName}\' field in \'printer.cfg\'.')
        return value

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
        self._verifyOk(replyJson, 'Homing failed during initialization.')
        self.setTransition(self._enterDone)
        self.get('/printer/objects/query?configfile')

    def _enterDone(self, replyJson):
        # Get sections
        config = self._getConfig(replyJson)
        probe = self._getConfigSection(config, 'probe')
        bedMesh = self._getConfigSection(config, 'bed_mesh')

        # Get probe sample count
        self.probeSampleCount = self._getConfigSectionValue(probe, 'samples', int, default=1)

        # Get probe z-height
        self.probeZHeight = self._getConfigSectionValue(bedMesh, 'horizontal_move_z', float, default=5)
        self.probeZHeight += 10.0 # Add 10.0 for safety

        # Get probe XY speed
        self.probeXYSpeed = self._getConfigSectionValue(bedMesh, 'speed', float, 50)

        # Done
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
        self._verifyOk(replyJson, 'Homing failed.')
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
        extruderPath = ['status', 'extruder']
        heaterBedPath = ['status', 'heater_bed']
        result = GetTemperaturesResult(toolActual = self._getField(replyJson, extruderPath + ['temperature'], type_=float),
                                       toolDesired = self._getField(replyJson, extruderPath + ['target'], type_=float),
                                       toolPower = self._getField(replyJson, extruderPath + ['power'], type_=float),
                                       bedActual = self._getField(replyJson, heaterBedPath + ['temperature'], type_=float),
                                       bedDesired = self._getField(replyJson, heaterBedPath + ['target'], type_=float),
                                       bedPower = self._getField(replyJson, heaterBedPath + ['power'], type_=float))

        self.finish(self.gotTemperatures, result)

class GetProbeOffsetsMachine(MoonrakerMachine):
    TYPE = CommandType.GET_PROBE_OFFSETS
    gotProbeOffsets = QtCore.Signal(str, dict, GetProbeOffsetsResult)

    def __init__(self, networkAccessManager, host, id_, context, parent=None):
        super().__init__(networkAccessManager, host, id_, context, parent)

    def start(self):
        self.setTransition(self._enterDone)
        self.get('/printer/objects/query?configfile')

    def _enterDone(self, replyJson):
        config = self._getConfig(replyJson)
        probe = self._getConfigSection(config, 'probe')

        xOffset = self._getConfigSectionValue(probe, 'x_offset', float, default=0.0)
        yOffset = self._getConfigSectionValue(probe, 'y_offset', float, default=0.0)
        zOffset = self._getConfigSectionValue(probe, 'z_offset', float)

        # Finish
        self.finish(self.gotProbeOffsets,
                    GetProbeOffsetsResult(xOffset = xOffset,
                                          yOffset = yOffset,
                                          zOffset = zOffset))

class GetCurrentPositionMachine(MoonrakerMachine):
    TYPE = CommandType.GET_CURRENT_POSITION
    gotCurrentPosition = QtCore.Signal(str, dict, GetCurrentPositionResult)

    def __init__(self, networkAccessManager, host, id_, context, parent=None):
        super().__init__(networkAccessManager, host, id_, context, parent)

    def start(self):
        self.setTransition(self._enterDone)
        self.get('/printer/objects/query?gcode_move')

    def _enterDone(self, replyJson):
        positionPath = ['status', 'gcode_move', 'gcode_position']
        positionLength = 4
        position = self._getField(replyJson, positionPath)
        names = ['X', 'Y', 'Z', 'E']
        values = [None] * positionLength

        # Verify position length
        if len(position) != positionLength:
            raise ValueError(f'Get current position failed, {self._fieldsToString(positionPath)} has the wrong number of values.' \
                             f' Found {len(position)} but expected {positionLength}.')

        # Convert each value
        for index in range(len(names)):
            values[index] = self._safeConvert(float, position[index])
            if values[index] is None:
                raise ValueError(f'Get current position failed, invalid value found for the {names[index]}-axis.')

        self.finish(self.gotCurrentPosition,
                    GetCurrentPositionResult(x = values[0],
                                             y = values[1],
                                             z = values[2],
                                             e = values[3]))

class GetMeshCoordinatesMachine(MoonrakerMachine):
    TYPE = CommandType.GET_MESH_COORDINATES
    gotMeshCoordinates = QtCore.Signal(str, dict, GetMeshCoordinatesResult)

    def __init__(self, networkAccessManager, host, id_, context, parent=None):
        super().__init__(networkAccessManager, host, id_, context, parent)

    def start(self):
        self.setTransition(self._enterDone)
        self.get('/printer/objects/query?configfile')

    def _enterDone(self, replyJson):
        def getValuePair(type_, name, bedMesh):
            values = bedMesh.data.get(name)
            if values is None:
                raise ValueError(f'Get mesh coordinates failed, \'{name}\' field not found in \'{bedMesh.name}\' section of \'printer.cfg\'.')

            values = values.split(',')
            for index in range(len(values)):
                values[index] = self._safeConvert(type_, values[index].strip())

            if len(values) != 2 or None in values:
                raise ValueError('Get mesh coordinates failed, invalid value for \'{bedMesh.name}:{name}\' field in \'printer.cfg\'.')

            return values

        config = self._getConfig(replyJson)
        bedMesh = self._getConfigSection(config, 'bed_mesh')

        minX, minY = getValuePair(float, 'mesh_min', bedMesh)
        maxX, maxY = getValuePair(float, 'mesh_max', bedMesh)
        columnCount, rowCount = getValuePair(int, 'probe_count', bedMesh)

        self.finish(self.gotMeshCoordinates,
                    CommandPrinter.calculateMeshCoordinates(rowCount = rowCount,
                                                            columnCount = columnCount,
                                                            minX = minX,
                                                            maxX = maxX,
                                                            minY = minY,
                                                            maxY = maxY))

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
        self._verifyOk(replyJson, 'Set bed temperature failed.')
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
        self._verifyOk(replyJson, 'Set nozzle temperature failed.')
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
        config = self._getConfig(replyJson)
        probe = self._getConfigSection(config, 'probe')
        probeSampleCount = self._getConfigSectionValue(probe, 'samples', int, default=1)

        self.finish(self.gotDefaultProbeSampleCount, probeSampleCount)

class GetDefaultProbeZHeightMachine(MoonrakerMachine):
    TYPE = CommandType.GET_DEFAULT_PROBE_Z_HEIGHT
    gotDefaultProbeZHeight = QtCore.Signal(str, dict, float)

    def __init__(self, networkAccessManager, host, id_, context, parent=None):
        super().__init__(networkAccessManager, host, id_, context, parent)

    def start(self):
        self.setTransition(self._enterDone)
        self.get('/printer/objects/query?configfile')

    def _enterDone(self, replyJson):
        config = self._getConfig(replyJson)
        bedMesh = self._getConfigSection(config, 'bed_mesh')
        probeZHeight = self._getConfigSectionValue(bedMesh, 'horizontal_move_z', float, default=5)

        self.finish(self.gotDefaultProbeZHeight, probeZHeight)

class GetDefaultProbeXYSpeedMachine(MoonrakerMachine):
    TYPE = CommandType.GET_DEFAULT_PROBE_XY_SPEED
    gotDefaultProbeXYSpeed = QtCore.Signal(str, dict, float)

    def __init__(self, networkAccessManager, host, id_, context, parent=None):
        super().__init__(networkAccessManager, host, id_, context, parent)

    def start(self):
        self.setTransition(self._enterDone)
        self.get('/printer/objects/query?configfile')

    def _enterDone(self, replyJson):
        config = self._getConfig(replyJson)
        bedMesh = self._getConfigSection(config, 'bed_mesh')
        probeXYSpeed = self._getConfigSectionValue(bedMesh, 'speed', float, 50)

        self.finish(self.gotDefaultProbeXYSpeed, probeXYSpeed)

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
        self.get('/printer/objects/query?configfile')

    def _enterRaise(self, replyJson):
        config = self._getConfig(replyJson)
        probe = self._getConfigSection(config, 'probe')

        self.xOffset = self._getConfigSectionValue(probe, 'x_offset', float, default=0.0)
        self.yOffset = self._getConfigSectionValue(probe, 'y_offset', float, default=0.0)

        self.setTransition(self._enterWaitForRaise)
        self.getGCode(f'G0 Z{self.probeHeight}')

    def _enterWaitForRaise(self, replyJson):
        self._verifyOk(replyJson, 'Probe failed while raising the toolhead.')
        self.setTransition(self._enterMove)
        self.getGCode(f'M400')

    def _enterMove(self, replyJson):
        self._verifyOk(replyJson, 'Probe failed waiting for the toolhead to rise.')
        self.setTransition(self._enterWaitForMove)
        self.getGCode(f'G0 X{self.x - self.xOffset} Y{self.y - self.yOffset} F{60*self.xySpeed}')

    def _enterWaitForMove(self, replyJson):
        self._verifyOk(replyJson, 'Probe failed while moving toolhead.')
        self.setTransition(self._enterProbe)
        self.getGCode(f'M400')

    def _enterProbe(self, replyJson):
        self._verifyOk(replyJson, 'Probe failed waiting for the toolhead to move.')
        self.setTransition(self._enterGetResult)
        self.getGCode(f'PROBE SAMPLES={self.sampleCount}') # TODO: Add more configuration parameters (see https://www.klipper3d.org/G-Codes.html#additional-commands)

    def _enterGetResult(self, replyJson):
        self._verifyOk(replyJson, 'Probe failed while probing.')
        self.setTransition(self._enterDone)
        self.get('/printer/objects/query?probe')

    def _enterDone(self, replyJson):
        z = self._getField(replyJson, ['status', 'probe', 'last_z_result'], type_=float)
        self.finish(self.probed,
                    ProbeResult(x = self.x,
                                y = self.y,
                                z = z))

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
        self._verifyOk(replyJson, f'Move failed while switching to {"relative" if self.relative else "absolute"} moves.')

        self.setTransition(self._enterWait if self.wait else self._enterDone)

        xPart = f' X{self.x}' if self.x is not None else ''
        yPart = f' Y{self.y}' if self.y is not None else ''
        zPart = f' Z{self.z}' if self.z is not None else ''
        ePart = f' E{self.e}' if self.e is not None else ''
        fPart = f' F{self.f}' if self.f is not None else ''
        self.getGCode('G0' + xPart + yPart + zPart + ePart + fPart)

    def _enterWait(self, replyJson):
        self._verifyOk(replyJson, f'Move failed while moving.')
        self.setTransition(self._enterDone)
        self.getGCode('M400')

    def _enterDone(self, replyJson):
        self._verifyOk(replyJson, f'Moved failed while waiting for move to finish.')
        self.finish(self.moved)
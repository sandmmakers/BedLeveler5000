from .Printer import Printer
from Common.Points import Point2F
from Common.LoggedFunction import loggedFunction
from PySide6 import QtCore
import abc
import enum
import logging
from typing import NamedTuple

class CommandType(enum.StrEnum):
    INIT = 'Init'
    HOME = 'home'
    GET_TEMPERATURES = 'getTemperatures'
    GET_PROBE_OFFSETS = 'getProbeOffsets'
    GET_CURRENT_POSITION = 'getCurrentPosition'
    GET_MESH_COORDINATES = 'getMeshCoordinates'
    SET_BED_TEMPERATURE = 'setBedTemperature'
    SET_NOZZLE_TEMPERATURE = 'setNozzleTemperature'
    GET_DEFAULT_PROBE_SAMPLE_COUNT = 'getDefaultProbeSampleCount'
    GET_DEFAULT_PROBE_Z_HEIGHT = 'getDefaultProbeZHeight'
    GET_DEFAULT_PROBE_XY_SPEED = 'getDefaultProbeXYSpeed'
    PROBE = 'probe'
    MOVE = 'move'

class GetTemperaturesResult(NamedTuple):
    toolActual: float
    toolDesired: float
    toolPower: float
    bedActual: float
    bedDesired: float
    bedPower: float

class GetProbeOffsetsResult(NamedTuple):
    xOffset: float
    yOffset: float
    zOffset: float

class ProbeResult(NamedTuple):
    x: float
    y: float
    z: float

class GetCurrentPositionResult(NamedTuple):
    x: float
    y: float
    z: float
    e: float

class GetMeshCoordinatesResult(NamedTuple):
    rowCount: int
    columnCount: int
    minX: float
    maxX: float
    minY: float
    maxY: float
    meshCoordinates: list[list[Point2F]]

class CommandPrinter(Printer):
    __metaclass__ = abc.ABCMeta

    sent = QtCore.Signal(CommandType, str, dict, str) # type, id, context, command)
    finished = QtCore.Signal(CommandType, str, dict, bool, object) # type, id, context, error, result
    errorOccurred = QtCore.Signal(CommandType, str, dict, str) # type, id, context, error message

    inited = QtCore.Signal(str, dict) # id, context
    homed = QtCore.Signal(str, dict) # id, context
    gotTemperatures = QtCore.Signal(str, dict, GetTemperaturesResult) # id, context, result
    gotProbeOffsets = QtCore.Signal(str, dict, GetProbeOffsetsResult) # id, context, result
    gotCurrentPosition = QtCore.Signal(str, dict, GetCurrentPositionResult) # id, context, result
    gotMeshCoordinates = QtCore.Signal(str, dict, GetMeshCoordinatesResult) # id, context, result
    bedTemperatureSet = QtCore.Signal(str, dict) # id, context
    nozzleTemperatureSet = QtCore.Signal(str, dict) # id, context
    gotDefaultProbeSampleCount = QtCore.Signal(str, dict, int) # id, context, result
    gotDefaultProbeZHeight = QtCore.Signal(str, dict, float) # id, context, result
    gotDefaultProbeXYSpeed = QtCore.Signal(str, dict, float) # id, context, result
    probed = QtCore.Signal(str, dict, ProbeResult) # id, context, result
    moved = QtCore.Signal(str, dict) # id, context

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Get logger
        self.logger = logging.getLogger(self.__class__.__name__)

        # Defaults
        self._probeSampleCount = None
        self._probeXYSpeed = None
        self._probeZHeight = None

    @loggedFunction
    def abort(self):
        self._abort()

    @abc.abstractmethod
    def _abort(self):
        raise NotImplementedError

    # Settings
    @loggedFunction
    def getProbeSampleCount(self):
        self.logger.info(f'Opened {self._serialPort.portName()}')
        return self._probeSampleCount

    @loggedFunction
    def getProbeZHeight(self):
        return self._probeZHeight

    @loggedFunction
    def getProbeXYSpeed(self):
        return self._probeXYSpeed

    @loggedFunction
    def setProbeSampleCount(self, count):
        self._probeSampleCount = count

    @loggedFunction
    def setProbeZHeight(self, height):
        self._probeZHeight = height

    @loggedFunction
    def setProbeXYSpeed(self, speed):
        self._probeXYSpeed = speed

    # Init
    @loggedFunction
    def init(self, id_, *, context=None):
        """ Resets default values for probe settings. """
        self._init(id_=id_, context=context)

    @abc.abstractmethod
    def _init(self, id_, *, context):
        raise NotImplementedError

    # Home
    @loggedFunction
    def home(self, id_, *, context=None, x=False, y=False, z=False):
        self._home(id_=id_, context=context, x=x, y=y, z=z)

    @abc.abstractmethod
    def _home(self, id_, *, context, x, y, z):
        raise NotImplementedError

    # Get temperatures
    @loggedFunction
    def getTemperatures(self, id_, *, context=None):
        self._getTemperatures(id_=id_, context=context)

    @abc.abstractmethod
    def _getTemperatures(self, id_, *, context):
        raise NotImplementedError

    # Get probe offsets
    @loggedFunction
    def getProbeOffsets(self, id_, *, context=None):
        self._getProbeOffsets(id_=id_, context=context)

    @abc.abstractmethod
    def _getProbeOffsets(self, id_, *, context):
        raise NotImplementedError

    # Get current position
    @loggedFunction
    def getCurrentPosition(self, id_, *, context=None):
        self._getCurrentPosition(id_=id_, context=context)

    @abc.abstractmethod
    def _getCurrentPosition(self, id_, *, context):
        raise NotImplementedError

    # Get mesh coordinates
    @loggedFunction
    def getMeshCoordinates(self, id_, *, context=None):
        self._getMeshCoordinates(id_=id_, context=context)

    @abc.abstractmethod
    def _getMeshCoordinates(self, id_, *, context):
        raise NotImplementedError

    # Set bed temperature
    @loggedFunction
    def setBedTemperature(self, id_, *, context=None, temperature):
        self._setBedTemperature(id_=id_, context=context, temperature=temperature)

    @abc.abstractmethod
    def _setBedTemperature(self, id_, *, context, temperature):
        raise NotImplementedError

    # Set nozzle temperature
    @loggedFunction
    def setNozzleTemperature(self, id_, *, context=None, temperature):
        self._setNozzleTemperature(id_=id_, context=context, temperature=temperature)

    @abc.abstractmethod
    def _setNozzleTemperature(self, id_, *, context, temperature):
        raise NotImplementedError

    # Get default probe sample count
    @loggedFunction
    def getDefaultProbeSampleCount(self, id_, *, context=None):
        self._getDefaultProbeSampleCount(id_=id_, context=context)

    @abc.abstractmethod
    def _getDefaultProbeSampleCount(self, id_, *, context=None):
        raise NotImplementedError

    # Get default probe Z height
    @loggedFunction
    def getDefaultProbeZHeight(self, id_, *, context=None):
        self._getDefaultProbeZHeight(id_=id_, context=context)

    @abc.abstractmethod
    def _getDefaultProbeZHeight(self, id_, *, context=None):
        raise NotImplementedError

    # Get default probe XY speed
    @loggedFunction
    def getDefaultProbeXYSpeed(self, id_, *, context=None):
        self._getDefaultProbeXYSpeed(id_=id_, context=context)

    @abc.abstractmethod
    def _getDefaultProbeXYSpeed(self, id_, *, context=None):
        raise NotImplementedError

    # Probe
    @loggedFunction
    def probe(self, id_, *, context=None, x, y):
        self._probe(id_=id_, context=context, x=x, y=y)

    @abc.abstractmethod
    def _probe(self, id_, *, context, x, y):
        raise NotImplementedError

    # Move
    @loggedFunction
    def move(self, id_, *, context=None, x=None, y=None, z=None, e=None, f=None, wait=True, relative=False):
        self._move(id_=id_, context=context, x=x, y=y, z=z, e=e, f=f, wait=wait, relative=relative)

    @abc.abstractmethod
    def _move(self, id_, *, context, x, y, z, e, f, wait, relative):
        raise NotImplementedError

    @staticmethod
    @loggedFunction(level='debug')
    def calculateMeshCoordinates(*, rowCount, columnCount, minX, maxX, minY, maxY):
        meshCoordinates = [[None for column in range(columnCount)] for row in range(rowCount)]

        xBase = minX
        yBase = minY
        xStep = (maxX - minX) / (columnCount - 1)
        yStep = (maxY - minY) / (rowCount - 1)
        for row in range(rowCount):
            y = yBase + row*yStep
            for column in range(columnCount):
                meshCoordinates[row][column] = Point2F(x = xBase + column*xStep,
                                                       y = y)

        return GetMeshCoordinatesResult(rowCount = rowCount,
                                        columnCount = columnCount,
                                        minX = minX,
                                        maxX = maxX,
                                        minY = minY,
                                        maxY = maxY,
                                        meshCoordinates = meshCoordinates)
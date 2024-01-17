#!/usr/bin/env python

from PySide6 import QtSerialPort
from collections import OrderedDict
import dataclasses
import enum
import json

CURRENT_PRINTER_INFO_VERSION = 3
PRINTER_INFO_FILE_FILTER = 'Printer Info Files (*.json);;All files (*.*)'

@enum.verify(enum.UNIQUE)
class ConnectionMode(enum.StrEnum):
    MARLIN_2 = 'Marlin2'
    MOONRAKER = 'Moonraker'

@enum.verify(enum.UNIQUE)
class ScrewType(enum.Enum):
    CW_M2       = ('CW-M2',       True,  True,  0.4)
    CCW_M2      = ('CCW-M2',      False, True,  0.4)
    CW_M3_0_35  = ('CW-M3-0.35',  True,  False, 0.35)
    CCW_M3_0_35 = ('CCW-M3-0.35', False, False, 0.35)
    CW_M3       = ('CW-M3',       True,  True,  0.5)
    CCW_M3      = ('CCW-M3',      False, True,  0.5)
    CW_M4_0_5   = ('CW-M4-0.5',   True,  False, 0.5)
    CCW_M4_0_5  = ('CCW-M4-0.5',  False, False, 0.5)
    CW_M4       = ('CW-M4',       True,  True,  0.7)
    CCW_M4      = ('CCW-M4',      False, True,  0.7)
    CW_M5_0_5   = ('CW-M5-0.5',   True,  False, 0.5)
    CCW_M5_0_5  = ('CCW-M5-0.5',  False, False, 0.5)
    CW_M5       = ('CW-M5',       True,  True,  0.8)
    CCW_M5      = ('CCW-M5',      False, True,  0.8)
    CW_M6_0_75  = ('CW-M6-0.75',  True,  False, 0.75)
    CCW_M6_0_75 = ('CCW-M6-0.75', False, False, 0.75)
    CW_M6       = ('CW-M6',       True,  True,  1.0)
    CCW_M6      = ('CCW-M6',      False, True,  1.0)
    CW_M7       = ('CW-M7',       True,  True,  1.0)
    CCW_M7      = ('CCW-M7',      False, True,  1.0)

    def __new__(cls, value, clockwise, coarse, pitch):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.clockwise = clockwise
        obj.coarse = coarse
        obj.pitch = pitch
        return obj

    @classmethod
    def fromValue(cls, value):
        for value_ in ScrewType:
            if value_.value == value:
                return value
        raise ValueError('Unknown enum value')

@enum.verify(enum.UNIQUE)
class BaudRate(enum.IntEnum):
    BAUD_1200 = 1_200
    BAUD_2400 = 2_400
    BAUD_4800 = 4_800
    BAUD_9600 = 9_600
    BAUD_19200 = 19_200
    BAUD_38400 = 38_400
    BAUD_57600 = 57_600
    BAUD_115200 = 115_200
    BAUD_250000 = 250_000

CONNECTION_MODE_MAP = OrderedDict([(str(ConnectionMode.MARLIN_2), ConnectionMode.MARLIN_2),
                                   (str(ConnectionMode.MOONRAKER), ConnectionMode.MOONRAKER)])

BAUD_RATE_MAP = OrderedDict([('1200', BaudRate.BAUD_1200),
                             ('2400', BaudRate.BAUD_2400),
                             ('4800', BaudRate.BAUD_4800),
                             ('9600', BaudRate.BAUD_9600),
                             ('19200', BaudRate.BAUD_19200),
                             ('38400', BaudRate.BAUD_38400),
                             ('57600', BaudRate.BAUD_57600),
                             ('115200', BaudRate.BAUD_115200),
                             ('250000', BaudRate.BAUD_250000)])

DATA_BITS_MAP = OrderedDict([('5', QtSerialPort.QSerialPort.Data5),
                             ('6', QtSerialPort.QSerialPort.Data6),
                             ('7', QtSerialPort.QSerialPort.Data7),
                             ('8', QtSerialPort.QSerialPort.Data8)])

PARITY_MAP = OrderedDict([('No', QtSerialPort.QSerialPort.NoParity),
                          ('Even', QtSerialPort.QSerialPort.EvenParity),
                          ('Odd', QtSerialPort.QSerialPort.OddParity),
                          ('Space', QtSerialPort.QSerialPort.SpaceParity),
                          ('Mark', QtSerialPort.QSerialPort.MarkParity)])

STOP_BITS_MAP = OrderedDict([('1', QtSerialPort.QSerialPort.OneStop),
                             ('1.5', QtSerialPort.QSerialPort.OneAndHalfStop),
                             ('2', QtSerialPort.QSerialPort.TwoStop)])

FLOW_CONTROL_MAP = OrderedDict([('No', QtSerialPort.QSerialPort.NoFlowControl),
                                ('Hardware', QtSerialPort.QSerialPort.HardwareControl),
                                ('Software', QtSerialPort.QSerialPort.SoftwareControl)])

@dataclasses.dataclass
class Marlin2Connection:
    baudRate: BaudRate = BaudRate.BAUD_115200
    dataBits: QtSerialPort.QSerialPort.DataBits = QtSerialPort.QSerialPort.Data8
    parity: QtSerialPort.QSerialPort.Parity = QtSerialPort.QSerialPort.NoParity
    stopBits: QtSerialPort.QSerialPort.StopBits = QtSerialPort.QSerialPort.OneStop
    flowControl: QtSerialPort.QSerialPort.FlowControl = QtSerialPort.QSerialPort.NoFlowControl

@dataclasses.dataclass
class MoonrakerConnection:
    pass

@dataclasses.dataclass
class GridProbePoint:
    name: str = None
    fixed: bool = None
    row: int = None
    column: int = None
    x: float = None
    y: float = None

@dataclasses.dataclass
class _PrinterInfo:
    version: int = CURRENT_PRINTER_INFO_VERSION
    displayName: str = ''
    connectionMode: ConnectionMode = None
    connection: Marlin2Connection|MoonrakerConnection = None
    screwType: ScrewType = None
    manualProbePoints: list[GridProbePoint] = dataclasses.field(default_factory=list)

    def load(self, filePath):
        with open(filePath, 'r') as file:
            data = json.load(file)

            if 'version' not in data or data['version'] != CURRENT_PRINTER_INFO_VERSION:
                    raise IOError(f'Outdated or corrupt printer info file detected: {filePath}.')

            self.displayName = data['displayName']

            self.connectionMode = data['connectionMode']
            connection = data['connection']
            if self.connectionMode == ConnectionMode.MARLIN_2:
                self.connection = Marlin2Connection()
                self.connection.baudRate = BAUD_RATE_MAP[connection['baudRate']]
                self.connection.dataBits = DATA_BITS_MAP[connection['dataBits']]
                self.connection.parity = PARITY_MAP[connection['parity']]
                self.connection.stopBits = STOP_BITS_MAP[connection['stopBits']]
                self.connection.flowControl = FLOW_CONTROL_MAP[connection['flowControl']]
            else:
                self.connection = MoonrakerConnection()

            self.screwType = ScrewType.fromValue(data['screwType'])
            self.manualProbePoints.clear()
            for point in data['manualProbePoints']:
                self.manualProbePoints.append(GridProbePoint(point['name'],
                                                             point['fixed'],
                                                             point['row'],
                                                             point['column'],
                                                             point['x'],
                                                             point['y']))

    def asJson(self):
        def valueToKey(_dict, value):
            return list(_dict.keys())[list(_dict.values()).index(value)]

        manualProbePoints = []
        for point in self.manualProbePoints:
            manualProbePoints.append({
                                         'name': point.name,
                                         'fixed': point.fixed,
                                         'row': point.row,
                                         'column': point.column,
                                         'x': point.x,
                                         'y': point.y
                                     })

        if self.connectionMode == ConnectionMode.MARLIN_2:
            connection = {
                             'baudRate': valueToKey(BAUD_RATE_MAP, self.connection.baudRate),
                             'dataBits': valueToKey(DATA_BITS_MAP, self.connection.dataBits),
                             'parity': valueToKey(PARITY_MAP, self.connection.parity),
                             'stopBits': valueToKey(STOP_BITS_MAP, self.connection.stopBits),
                             'flowControl': valueToKey(FLOW_CONTROL_MAP, self.connection.flowControl)
                         }
        else:
            connection = {}

        data = {
                   'version': CURRENT_PRINTER_INFO_VERSION,
                   'displayName': self.displayName,
                   'connectionMode': self.connectionMode,
                   'connection': connection,
                   'screwType': self.screwType.value,
                   'manualProbePoints': manualProbePoints
               }

        return data

def fromFile(filePath):
    printerInfo = _PrinterInfo()
    printerInfo.load(filePath)
    return printerInfo

def default(connectionMode):
    printerInfo = _PrinterInfo()
    printerInfo.connectionMode = connectionMode
    if connectionMode == ConnectionMode.MARLIN_2:
        printerInfo.connection = Marlin2Connection()
    elif connectionMode == ConnectionMode.MOONRAKER:
        printerInfo.connection = MoonrakerConnection()
    else:
        raise ValueError('Detected an unsupported connection mode.')

    printerInfo.screwType = ScrewType.CW_M4
    return printerInfo

if __name__ == '__main__':
    from Common import Common
    import pathlib

    def testFile(path):
        printerInfo = fromFile(path)
        printerInfoJson = printerInfo.asJson()

        with open(path, 'r') as file:
            rawJson = json.load(file)

        print(printerInfoJson)
        print(rawJson)
        assert(printerInfoJson == rawJson)

    print(default(ConnectionMode.MARLIN_2).asJson())
    print(default(ConnectionMode.MOONRAKER).asJson())

    testFile(Common.printersDir() / 'ElegooNeptune3Plus.json')
    testFile(Common.printersDir() / 'ElegooNeptune3Max.json')
    testFile(Common.printersDir() / 'ElegooNeptune4Max.json')
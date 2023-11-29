#!/usr/bin/env python

from PySide6 import QtSerialPort
from collections import OrderedDict
import dataclasses
from enum import StrEnum
import json

CURRENT_PRINTER_INFO_VERSION = 2
PRINTER_INFO_FILE_FILTER = 'Printer Info Files (*.json);;All files (*.*)'

class ConnectionMode(StrEnum):
    MARLIN_2 = 'Marlin2'
    MOONRAKER = 'Moonraker'

CONNECTION_MODE_MAP = OrderedDict([(str(ConnectionMode.MARLIN_2), ConnectionMode.MARLIN_2),
                                   (str(ConnectionMode.MOONRAKER), ConnectionMode.MOONRAKER)])

BAUD_RATE_MAP = OrderedDict([('1200', QtSerialPort.QSerialPort.Baud1200),
                             ('2400', QtSerialPort.QSerialPort.Baud2400),
                             ('4800', QtSerialPort.QSerialPort.Baud4800),
                             ('9600', QtSerialPort.QSerialPort.Baud9600),
                             ('19200', QtSerialPort.QSerialPort.Baud19200),
                             ('38400', QtSerialPort.QSerialPort.Baud38400),
                             ('57600', QtSerialPort.QSerialPort.Baud57600),
                             ('115200', QtSerialPort.QSerialPort.Baud115200)])

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
    baudRate: QtSerialPort.QSerialPort.BaudRate = QtSerialPort.QSerialPort.Baud115200
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

            self.manualProbePoints.clear()
            for point in data['manualProbePoints']:
                self.manualProbePoints.append(GridProbePoint(point['name'],
                                                             int(point['row']),
                                                             int(point['column']),
                                                             float(point['x']),
                                                             float(point['y'])))

    def asJson(self):
        def valueToKey(_dict, value):
            return list(_dict.keys())[list(_dict.values()).index(value)]

        manualProbePoints = []
        for point in self.manualProbePoints:
            manualProbePoints.append({
                                         'name': point.name,
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
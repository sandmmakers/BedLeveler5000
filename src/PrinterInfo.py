from PySide6 import QtSerialPort
from collections import OrderedDict
import dataclasses
from enum import StrEnum
import json

PRINTER_INFO_FILE_FILTER = 'Printer Info Files (*.json);;All files (*.*)'

class GCodeFlavor(StrEnum):
    MARLIN_2 = 'Marlin 2'

G_CODE_FLAVOR_MAP = OrderedDict([(str(GCodeFlavor.MARLIN_2), GCodeFlavor.MARLIN_2)])

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
class Connection:
    gCodeFlavor: GCodeFlavor = GCodeFlavor.MARLIN_2
    baudRate: QtSerialPort.QSerialPort.BaudRate = QtSerialPort.QSerialPort.Baud115200
    dataBits: QtSerialPort.QSerialPort.DataBits = QtSerialPort.QSerialPort.Data8
    parity: QtSerialPort.QSerialPort.Parity = QtSerialPort.QSerialPort.NoParity
    stopBits: QtSerialPort.QSerialPort.StopBits = QtSerialPort.QSerialPort.OneStop
    flowControl: QtSerialPort.QSerialPort.FlowControl = QtSerialPort.QSerialPort.NoFlowControl

@dataclasses.dataclass
class Mesh:
    columnCount: int = 2
    rowCount: int = 2

@dataclasses.dataclass
class GridProbePoint:
    name: str = None
    row: int = None
    column: int = None
    x: float = None
    y: float = None

@dataclasses.dataclass
class PrinterInfo:
    displayName: str = ''
    connection: Connection = dataclasses.field(default_factory=Connection)
    mesh: Mesh = dataclasses.field(default_factory=Mesh)
    manualProbePoints: list = dataclasses.field(default_factory=list)

    def clear(self):
        self.displayName = ''
        self.connection  = Connection()
        self.mesh = Mesh()
        self.manualProbePoints = []

    @staticmethod
    def fromFile(filePath):
        printerInfo = PrinterInfo()
        printerInfo.load(filePath)
        return printerInfo

    def load(self, filePath):
        with open(filePath, 'r') as file:
            data = json.load(file)

            self.displayName = data['displayName']

            connection = data['connection']
            self.connection.gCodeFlavor = G_CODE_FLAVOR_MAP[connection['gCodeFlavor']]
            self.connection.baudRate = BAUD_RATE_MAP[connection['baudRate']]
            self.connection.dataBits = DATA_BITS_MAP[connection['dataBits']]
            self.connection.parity = PARITY_MAP[connection['parity']]
            self.connection.stopBits = STOP_BITS_MAP[connection['stopBits']]
            self.connection.flowControl = FLOW_CONTROL_MAP[connection['flowControl']]

            mesh = data['mesh']
            self.mesh.columnCount = int(mesh['columnCount'])
            self.mesh.rowCount = int(mesh['rowCount'])

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

        data = {
                   'displayName': self.displayName,
                   'connection': {
                                     'gCodeFlavor': valueToKey(G_CODE_FLAVOR_MAP, self.connection.gCodeFlavor),
                                     'baudRate': valueToKey(BAUD_RATE_MAP, self.connection.baudRate),
                                     'dataBits': valueToKey(DATA_BITS_MAP, self.connection.dataBits),
                                     'parity': valueToKey(PARITY_MAP, self.connection.parity),
                                     'stopBits': valueToKey(STOP_BITS_MAP, self.connection.stopBits),
                                     'flowControl': valueToKey(FLOW_CONTROL_MAP, self.connection.flowControl)
                                 },
                   'mesh': {
                               'columnCount': self.mesh.columnCount,
                               'rowCount': self.mesh.rowCount
                           },
                   'manualProbePoints': manualProbePoints
               }

        return data

if __name__ == '__main__':
    printerInfo = PrinterInfo()
    printerInfo.load('Printers/ElegooNeptune3Max.json')

    assert(GridProbePoint().name is None)
    print(printerInfo)
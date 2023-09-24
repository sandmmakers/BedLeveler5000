#!/usr/bin/env python3

from Commands.CommandG0 import CommandG0
from Commands.CommandG28 import CommandG28
from Commands.CommandG30 import CommandG30
from Commands.CommandG42 import CommandG42
from Commands.CommandM104 import CommandM104
from Commands.CommandM105 import CommandM105
from Commands.CommandM114 import CommandM114
from Commands.CommandM118 import CommandM118
from Commands.CommandM140 import CommandM140
from Commands.CommandM400 import CommandM400
from Commands.CommandM851 import CommandM851
from Commands.GCodeError import GCodeError
from PySide6 import QtCore
from PySide6 import QtSerialPort
import logging
import queue
import math

class Connection(QtCore.QObject):
    received = QtCore.Signal(str, str, dict, dict)
    receivedG0 = QtCore.Signal(str, dict, dict)
    receivedG28 = QtCore.Signal(str, dict, dict)
    receivedG30 = QtCore.Signal(str, dict, dict)
    receivedG42 = QtCore.Signal(str, dict, dict)
    receivedM104 = QtCore.Signal(str, dict, dict)
    receivedM105 = QtCore.Signal(str, dict, dict)
    receivedM114 = QtCore.Signal(str, dict, dict)
    receivedM118 = QtCore.Signal(str, dict, dict)
    receivedM140 = QtCore.Signal(str, dict, dict)
    receivedM400 = QtCore.Signal(str, dict, dict)
    receivedM851 = QtCore.Signal(str, dict, dict)

    def __init__(self, *args, commonSignal=False, separateSignals=False, **kwargs):
        super().__init__(*args, **kwargs)

        # Get logger
        self.logger = logging.getLogger(self.__class__.__name__)

        # Signal configuration
        self.commonSignal = commonSignal
        self.separateSignals = separateSignals

        # Serial port
        self.serialPort = QtSerialPort.QSerialPort()
        self.serialPort.readyRead.connect(self._readData)
        self.serialPort.errorOccurred.connect(self._handleSerialPortError)

        self.readBuffer = b''
        self.readLines = []
        self.jobQueue = queue.Queue()

        self.signalMap = {}
        self.signalMap[CommandG0.NAME] = self.receivedG0
        self.signalMap[CommandG28.NAME] = self.receivedG28
        self.signalMap[CommandG30.NAME] = self.receivedG30
        self.signalMap[CommandG42.NAME] = self.receivedG42
        self.signalMap[CommandM104.NAME] = self.receivedM104
        self.signalMap[CommandM105.NAME] = self.receivedM105
        self.signalMap[CommandM114.NAME] = self.receivedM114
        self.signalMap[CommandM118.NAME] = self.receivedM118
        self.signalMap[CommandM140.NAME] = self.receivedM140
        self.signalMap[CommandM400.NAME] = self.receivedM400
        self.signalMap[CommandM851.NAME] = self.receivedM851

    def _handleSerialPortError(self, errorCode):
        match errorCode:
            case QtSerialPort.QSerialPort.SerialPortError.NoError:
                return
            case QtSerialPort.QSerialPort.SerialPortError.DeviceNotFoundError:
                message = 'An error occured while attempting to open a non-existing device.'
            case QtSerialPort.QSerialPort.SerialPortError.PermissionError:
                message = 'An error occurred while attempting to open an already opened device by another process or a user not having enough permission and credentials to open.'
            case QtSerialPort.QSerialPort.SerialPortError.OpenError:
                message = 'An error occurred while attempting to open an already opened device in this object.'
            case QtSerialPort.QSerialPort.SerialPortError.NotOpenError:
                message = 'This error occurs when an operation is executed that can only be successfully performed if the device is open.'
            case QtSerialPort.QSerialPort.SerialPortError.WriteError:
                message = 'An I/O error occurred while writing data.'
            case QtSerialPort.QSerialPort.SerialPortError.ReadError:
                message = 'An I/O error occurred while reading data.'
            case QtSerialPort.QSerialPort.SerialPortError.ResourceError:
                message = 'An I/O error occurred when a resource becomes unavailable, e.g. when the device is unexpectedly removed from the system.'
            case QtSerialPort.QSerialPort.SerialPortError.UnsupportedOperationError:
                message = 'The requested device operation is not supported or prohibited by the running operating system.'
            case QtSerialPort.QSerialPort.SerialPortError.TimeoutError:
                message = 'A timeout error occurred.'
            case QtSerialPort.QSerialPort.SerialPortError.UnknownError:
                message = 'An unknown error occured.'
            case _:
                message = 'An unidentified error occured.'

        self._error(f'Serial port error: {message}')

    def connected(self):
        return self.serialPort.isOpen()

    def pendingCount(self):
        return self.jobQueue.qsize()

    def open(self, portName, *, clear=True):
        assert(not self.serialPort.isOpen())

        baudRate = QtSerialPort.QSerialPort.Baud115200
        dataBits = QtSerialPort.QSerialPort.Data8
        parity = QtSerialPort.QSerialPort.NoParity
        stopBits = QtSerialPort.QSerialPort.OneStop
        flowControl = QtSerialPort.QSerialPort.NoFlowControl

        self.serialPort.setPortName(portName)
        self.serialPort.setBaudRate(baudRate)
        self.serialPort.setDataBits(dataBits)
        self.serialPort.setParity(parity)
        self.serialPort.setStopBits(stopBits)
        self.serialPort.setFlowControl(flowControl)

        if not self.serialPort.open(QtCore.QIODevice.ReadWrite):
            self._error(f'Failed to open {portName}.')

        if clear and not self.serialPort.clear():
            self._error(f'Failed to clear {portName}.')

        self.logger.info(f'Opened {self.serialPort.portName()}')

    def close(self):
        assert(self.serialPort.isOpen())

        self.serialPort.close()
        self.logger.info(f'Closed {self.serialPort.portName()}')

    def _readData(self):
        self.readBuffer += self.serialPort.readAll()

        # Log the read buffer
        self.logger.debug(f'Read buffer: ')
        for batch in range(int(math.ceil(self.readBuffer.length() / 16))):
            startIndex = 16 * batch
            stopIndex = min(startIndex + 16, self.readBuffer.length())
            message = f'[0x{startIndex:02X}]:'
            for currentIndex in range(startIndex, stopIndex):
                message += f' {self.readBuffer[currentIndex].hex().upper()}'
            self.logger.debug(message)

        while (index := self.readBuffer.indexOf(b'\n')) > -1:
            # Extract line
            try:
                line = str(self.readBuffer[:index], 'ascii') # TODO: Verify the correct encoding
            except:
                self.logger.warn(f'Detected bad bytes: {self.readBuffer.data().hex()}.')
                self.readBuffer.clear()
                continue

            self.readBuffer = self.readBuffer[index+1:]

            self.logger.debug(f'Line: {line}')

            # Skip echo lines
            if line.startswith('echo:'):
                continue

            self.readLines.append(line)

            # Received full response
            if line.startswith('ok'):
                assert(not self.jobQueue.empty())
                command = self.jobQueue.get()

                self.logger.info(f'Processing command - {command}')

                if len(self.readLines) != command.LINE_COUNT:
                    message = f'Incorrect number of response lines detected for command: {command.NAME} ({command.id}) - {len(self.readLines)} {command.LINE_COUNT}.'
                    for line in self.readLines:
                        message += line
                    self._error(message)
                else:
                    # Log the response lines
                    for line in self.readLines[0:command.LINE_COUNT]:
                        self.logger.info(f'Response: "{line}"')

                    response = command.parseResponse(self.readLines[0:command.LINE_COUNT])

                    if self.commonSignal:
                        self.received.emit(command.NAME, command.id, command.context, response)
                    if self.separateSignals:
                        self.signalMap[command.NAME].emit(command.id, command.context, response)

                self.readLines.clear()

    def _sendCommand(self, command):
        self.logger.info(f'Sending command - {command}')
        self.jobQueue.put(command)
        self.serialPort.write((command.request + '\n').encode())

    def sendG0(self, id_, *, context=None, **kwargs):
        self._sendCommand(CommandG0(id_, context=context, **kwargs))

    def sendG28(self, id_, *, context=None, **kwargs):
        self._sendCommand(CommandG28(id_, context=context, **kwargs))

    def sendG30(self, id_, *, context=None, **kwargs):
        self._sendCommand(CommandG30(id_, context=context, **kwargs))

    def sendG42(self, id_, *, context=None, **kwargs):
        self._sendCommand(CommandG42(id_, context=context, **kwargs))

    def sendM104(self, id_, *, context=None, **kwargs):
        self._sendCommand(CommandM104(id_, context=context, **kwargs))

    def sendM105(self, id_, *, context=None, **kwargs):
        self._sendCommand(CommandM105(id_, context=context, **kwargs))

    def sendM114(self, id_, *, context=None, **kwargs):
        self._sendCommand(CommandM114(id_, context=context, **kwargs))

    def sendM118(self, id_, *, context=None, **kwargs):
        self._sendCommand(CommandM118(id_, context=context, **kwargs))

    def sendM140(self, id_, *, context=None, **kwargs):
        self._sendCommand(CommandM140(id_, context=context, **kwargs))

    def sendM400(self, id_, *, context=None, **kwargs):
        self._sendCommand(CommandM400(id_, context=context, **kwargs))

    def sendM851(self, id_, *, context=None, **kwargs):
        self._sendCommand(CommandM851(id_, context=context, **kwargs))

    def _error(self, message):
        self.logger.error(message)
        raise IOError(message)

if __name__ == '__main__':
    # Main only imports
    import sys
    from PySide6 import QtCore
    from PySide6 import QtWidgets

    app = QtWidgets.QApplication(sys.argv)

    connection = Connection(commonSignal=True, separateSignals=True)
    connection.received.connect(lambda type_, id_, context, response: print(f'Received common {type_} ({id_}): {context} <> {response}'))
    connection.receivedG0.connect(lambda id_, context, response: print(f'Received G0 ({id_}): {context} <> {response}'))
    connection.receivedG28.connect(lambda id_, context, response: print(f'Received G28 ({id_}): {context} <> {response}'))
    connection.receivedG30.connect(lambda id_, context, response: print(f'Received G30 ({id_}): {context} <> {response}'))
    connection.receivedG42.connect(lambda id_, context, response: print(f'Received G42 ({id_}): {context} <> {response}'))
    connection.receivedM104.connect(lambda id_, context, response: print(f'Received M104 ({id_}): {context} <> {response}'))
    connection.receivedM105.connect(lambda id_, context, response: print(f'Received M105 ({id_}): {context} <> {response}'))
    connection.receivedM114.connect(lambda id_, context, response: print(f'Received M114 ({id_}): {context} <> {response}'))
    connection.receivedM118.connect(lambda id_, context, response: print(f'Received M118 ({id_}): {context} <> {response}'))
    connection.receivedM140.connect(lambda id_, context, response: print(f'Received M140 ({id_}): {context} <> {response}'))
    connection.receivedM400.connect(lambda id_, context, response: print(f'Received M400 ({id_}): {context} <> {response}'))
    connection.receivedM851.connect(lambda id_, context, response: print(f'Received M851 ({id_}): {context} <> {response}'))

    connection.open('COM4')

    #connection.sendG28('0')
    #connection.sendG0('1', z=5.2)
    #connection.sendG30('2', x=37.5, y=37.5)
    #connection.sendM104('3', s=2)
    #connection.sendM105('4')
    #connection.sendM851('5')
    #connection.sendG42('6', f=1000, i=1, j=0)
    #connection.sendM114('7', context={'a': 2})
    #connection.sendM140('8', s=0)

    #connection.sendG0('t1', x=10, y=10)
    #connection.sendG0('t2', x=300, y=300)
    #connection.sendM400('t3')
    #connection.sendM114('t4', context={'a': 2})
    connection.sendM118('M118_Test', string='Steve    ')

    widget = QtWidgets.QWidget()
    widget.show()

    sys.exit(app.exec())
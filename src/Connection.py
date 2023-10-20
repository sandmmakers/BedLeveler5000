#!/usr/bin/env python

from PrinterInfo import PrinterInfo
from PySide6 import QtCore
from PySide6 import QtSerialPort
import logging
import math

class Connection(QtCore.QObject):
    def __init__(self, printerInfo=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Get logger
        self.logger = logging.getLogger(self.__class__.__name__)

        # Serial port
        self.serialPort = QtSerialPort.QSerialPort()
        self.serialPort.readyRead.connect(self._readData)
        self.serialPort.errorOccurred.connect(self._handleSerialPortError)

        self.readBuffer = b''

        if printerInfo is not None:
            self.setPrinter(printerInfo)

    def setPrinter(self, printerInfo):
        assert(not self.serialPort.isOpen())

        self.serialPort.setBaudRate(printerInfo.connection.baudRate)
        self.serialPort.setDataBits(printerInfo.connection.dataBits)
        self.serialPort.setParity(printerInfo.connection.parity)
        self.serialPort.setStopBits(printerInfo.connection.stopBits)
        self.serialPort.setFlowControl(printerInfo.connection.flowControl)

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

    def open(self, portName, *, clear=True):
        assert(not self.serialPort.isOpen())

        self.serialPort.setPortName(portName)

        if not self.serialPort.open(QtCore.QIODevice.ReadWrite):
            self._error(f'Failed to open {portName}.')

        if clear and not self.serialPort.clear():
            self._error(f'Failed to clear {portName}.')

        self.logger.info(f'Opened {self.serialPort.portName()}')

    def close(self):
        if self.serialPort.isOpen():
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

            self._processLine(line)

    def _error(self, message):
        self.logger.error(message)
        raise IOError(message)

if __name__ == '__main__':
    # Main only imports
    import sys
    from PySide6 import QtCore
    from PySide6 import QtWidgets

    class TestConnection(Connection):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def sendCommand(self, command):
            self.logger.info(command)
            self.serialPort.write((command + '\n').encode())

        def _processLine(self, line):
            print(f'Processing: {line}')

    app = QtWidgets.QApplication(sys.argv)

    # Configure logging
    logging.basicConfig(level = logging.DEBUG)
    logger = logging.getLogger()

    connection = TestConnection(printerInfo = PrinterInfo())

    connection.open('COM4')

    connection.sendCommand('M114')

    widget = QtWidgets.QWidget()
    widget.show()

    sys.exit(app.exec())
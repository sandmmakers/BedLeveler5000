from .GCodeError import GCodeError
from .CommandBase import CommandBase
from . import Converter

class CommandM851(CommandBase):
    NAME = 'M851'

    def __init__(self, *, x=None, y=None, z=None):
        self.x = x
        self.y = y
        self.z = z

        xPart = '' if self.x is None else Converter.floatToStr(self.x, prefix=' X')
        yPart = '' if self.y is None else Converter.floatToStr(self.y, prefix=' Y')
        zPart = '' if self.z is None else Converter.floatToStr(self.z, prefix=' Z')

        super().__init__(self.NAME + xPart + yPart + zPart)

    def _processLine(self, line):
        # Line 0: '  M851 X<FLOAT> Y<FLOAT> Z<FLOAT> ; (mm)'
        #            |    |        |        |        | +--------- Units
        #            |    |        |        |        +----------- Comment
        #            |    |        |        +-------------------- Z offset
        #            |    |        +----------------------------- Y offset
        #            |    +-------------------------------------- X offset
        #            +------------------------------------------- G-code command name
        # Line 1: ok

        if self.result is None:
            tokens = CommandBase.tokenize(line, 6)

            if tokens[0] != 'M851' or \
               not tokens[1].startswith('X') or \
               not tokens[2].startswith('Y') or \
               not tokens[3].startswith('Z') or \
               tokens[4] != ';' or \
               tokens[5] != '(mm)':
                raise GCodeError(f'Unable to parse response: [{line}].')

            try:
                self.result = {'x': float(tokens[1][1:]),
                               'y': float(tokens[2][1:]),
                               'z': float(tokens[3][1:])}

            except ValueError:
                raise GCodeError(f'Incorrect numeric data type found in response: [{line}].')
        else:
            self.verifyOkResponseLine(line)
            return True

        return False
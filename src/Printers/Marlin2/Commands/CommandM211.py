from .GCodeError import GCodeError
from .CommandBase import CommandBase
from . import Converter

class CommandM211(CommandBase):
    NAME = 'M211'

    def __init__(self, *, s=None):
        self.s = s

        sPart = '' if self.s is None else f' S{self.s}'

        super().__init__(self.NAME + sPart)

    def _processLine(self, line):
        # Setting:
        # Line 0: 'ok'

        # Querying:
        # Line 0: '  M211 S1 ; ON'
        # Line 1: '  Min:  X0.00 Y-6.00 Z0.00   Max:  X430.00 Y430.00 Z500.00'
        # Line 2: 'ok'

        if self.s is None:
            tokens = line.strip().split()

            if self.result is None:
                if len(tokens) < 2 or     \
                   tokens[0] != 'M211' or \
                   len(tokens[1]) != 2 or \
                   tokens[1][0] != 'S' or \
                   tokens[1][1] not in ['0', '1']:
                    raise GCodeError(f'Unable to parse response: [{line}].')

                self.result = {'on': (tokens[1][1] == '1')}
                return False

            elif 'minX' not in self.result:
                if len(tokens) != 8 or              \
                   tokens[0] != 'Min:' or           \
                   not tokens[1].startswith('X') or \
                   not tokens[2].startswith('Y') or \
                   not tokens[3].startswith('Z') or \
                   tokens[4] != 'Max:' or           \
                   not tokens[5].startswith('X') or \
                   not tokens[6].startswith('Y') or \
                   not tokens[7].startswith('Z'):
                    raise GCodeError(f'Unable to parse response: [{line}].')

                try:
                    self.result['minX'] = float(tokens[1][1:])
                    self.result['minY'] = float(tokens[2][1:])
                    self.result['minZ'] = float(tokens[3][1:])
                    self.result['maxX'] = float(tokens[5][1:])
                    self.result['maxY'] = float(tokens[6][1:])
                    self.result['maxZ'] = float(tokens[7][1:])
                except ValueError:
                    raise GCodeError(f'Incorrect numeric data type found in response: [{line}].')

                return False

        self.verifyOkResponseLine(line)
        return True
from .GCodeError import GCodeError
from abc import ABC, abstractmethod

class CommandBase(ABC):
    @classmethod
    @property
    @abstractmethod
    def LINE_COUNT(cls):
        raise NotImplementedError

    def __init__(self, id_, request, context=None):
        self.id = id_
        self.request = request
        self.context = context

    def __str__(self):
        return f'Id: {self.id} Request: {self.request}'

    def verifyLineCount(self, lines):
        if len(lines) != self.LINE_COUNT:
            lineString = 'line' + {'' if self.LINE_COUNT == 1 else 's'}
            raise GCodeError(f'Expected {self.LINE_COUNT} {lineString}, but detected {len(lines)}.')

    @staticmethod
    def verifyOkResponseLine(line):
        if line != 'ok':
            raise GCodeError(f'Expected \'ok\' but detected \'{line}\'.')

    @staticmethod
    def tokenize(line, count, *, replace=' '):
        tokens = line.replace(replace, ' ').split()

        if len(tokens) != count:
            raise GCodeError(f'Incorrect number of tokens in response: [{line}].')
        return tokens

    @staticmethod
    def parseBedResponseLine(line):
        tokens = CommandBase.tokenize(line, 7)

        if tokens[0] != 'Bed' or \
           tokens[1] != 'X:' or  \
           tokens[3] != 'Y:' or  \
           tokens[5] != 'Z:':
            raise GCodeError(f'Unable to parse response: [{line}].')

        try:
            return {'x': float(tokens[2]),
                    'y': float(tokens[4]),
                    'z': float(tokens[6])}
        except ValueError:
            raise GCodeError(f'Incorrect numeric data type found in response: [{line}].')

    @staticmethod
    def parsePositionResponseLine(line):
        tokens = CommandBase.tokenize(line, 15, replace=':')

        if tokens[0] != 'X' or \
           tokens[2] != 'Y' or \
           tokens[4] != 'Z' or \
           tokens[6] != 'E' or \
           tokens[8] != 'Count' or \
           tokens[9] != 'X' or \
           tokens[11] != 'Y' or \
           tokens[13] != 'Z':
            raise GCodeError(f'Unable to parse response: [{line}].')

        try:
            return {'x': float(tokens[1]),
                    'y': float(tokens[3]),
                    'z': float(tokens[5]),
                    'e': float(tokens[7]),
                    'count': {'x': int(tokens[10]),
                              'y': int(tokens[12]),
                              'z': int(tokens[14])}}
        except ValueError:
            raise GCodeError(f'Incorrect numeric data type found in response: [{line}].')
from .GCodeError import GCodeError
from .CommandBase import CommandBase

class CommandM105(CommandBase):
    NAME = 'M105'

    def __init__(self, *, r=False, t=None):
        self.r = r
        self.t = t

        rPart = ' R' if self.r else ''
        tPart = f' T{self.t}' if self.t is not None else ''

        super().__init__(self.NAME + rPart + tPart)

    def __duplicateCheck(self, name: str, values: list[float|None]):
        if not isinstance(values, list):
            values = [values]
        if any(value is not None for value in values):
            raise ValueError(f'Found duplicate \'{name}\' token.')

    def _processLine(self, line: str):
        # Line 0: 'ok T:<FLOAT> /<FLOAT> B:<FLOAT> /<FLOAT> @:<FLOAT> B@:<FLOAT>'
        #          |  |         |        |         |        |         +----------- Bed power
        #          |  |         |        |         |        +--------------------- Tool power
        #          |  |         |        |         +------------------------------ Bed temp (desired)
        #          |  |         |        +---------------------------------------- Bed temp (actual)
        #          |  |         +------------------------------------------------- Tool temp (desired)
        #          |  +----------------------------------------------------------- Tool temp (actual)
        #          +-------------------------------------------------------------- ok

        if self.isMetadata(line) or self.isAutoReport(line):
            return False

        bedTempActual = None
        bedTempDesired = None
        bedPower = None

        toolTempActual = None
        toolTempDesired = None
        toolPower = None

        tool0TempActual = None
        tool0TempDesired = None
        tool0Power = None

        try:
            tokens = line.split()

            if tokens[0] != 'ok':
                raise ValueError(f'Line does not start with \'ok\'.')

            index = 1
            while index < len(tokens):
                name, tempActualPower = tokens[index].split(':')
                if '/' in name:
                    raise ValueError(f'Unexpected field name: {name}.')
                tempActualPower = float(tempActualPower)
                index += 1

                tempDesired = None
                if index < len(tokens) and tokens[index].startswith('/'):
                    if '@' in name:
                        raise ValueError('Found unexpected desired value.')
                    tempDesired = float(tokens[index][1:])
                    index += 1

                if name == '@':
                    self.__duplicateCheck(name, toolPower)
                    toolPower = tempActualPower
                elif name == '@0':
                    self.__duplicateCheck(name, tool0Power)
                    tool0Power = tempActualPower
                elif name == 'B@':
                    self.__duplicateCheck(name, bedPower)
                    bedPower = tempActualPower
                elif name == 'T':
                    self.__duplicateCheck(name, [toolTempActual, toolTempDesired])
                    toolTempActual = tempActualPower
                    toolTempDesired = tempDesired
                elif name == 'T0':
                    self.__duplicateCheck(name, [tool0TempActual, tool0TempDesired])
                    tool0TempActual = tempActualPower
                    tool0TempDesired = tempDesired
                elif name == 'B':
                    self.__duplicateCheck(name, [bedTempActual, bedTempDesired])
                    bedTempActual = tempActualPower
                    bedTempDesired = tempDesired

            if toolTempActual is None:
                toolTempActual = tool0TempActual
            if toolTempDesired is None:
                toolTempDesired = tool0TempDesired
            if toolPower is None:
                toolPower = tool0Power

            self.result = {'toolActual':  toolTempActual,
                           'toolDesired': toolTempDesired,
                           'bedActual':   bedTempActual,
                           'bedDesired':  bedTempDesired,
                           'toolPower':   toolPower,
                           'bedPower':    bedPower}
            for key, value in self.result.items():
                if value is None:
                    raise ValueError(f'Required value \'{key}\' is missing.')
        except (IndexError, ValueError) as exception:
            raise GCodeError(f'Unable to parse response: [{line}].') from exception

        return True
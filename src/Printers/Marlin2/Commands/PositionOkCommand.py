from .CommandBase import CommandBase

class PositionOkCommand(CommandBase):
    IGNORE_LINES = ['Taring probe'] # Observed with a Neptune 3 Pro

    def _processLine(self, line):
        # Line 0: position
        # Line 1: ok

        # Check for ignore lines
        if self.isMetadata(line) or \
           line in self.IGNORE_LINES:
            return False

        if self.isTemperatureAutoReport(line):
            self.result = None
        elif self.isPositionAutoReport(line):
            self.result = self.parsePositionResponseLine(line)
        else:
            self.verifyOkResponseLine(line)
            return True

        return False
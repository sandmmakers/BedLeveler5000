from .CommandBase import CommandBase
from . import Converter

class OkCommand(CommandBase):
    def _processLine(self, line):
        # Line 0: ok

        if self.isMetadata(line) or self.isAutoReport(line):
            return False

        self.verifyOkResponseLine(line)
        return True
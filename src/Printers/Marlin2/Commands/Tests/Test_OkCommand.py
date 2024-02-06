from Printers.Marlin2.Commands.OkCommand import OkCommand
from Printers.Marlin2.Commands.GCodeError import GCodeError
import pytest

REQUEST = ''
ECHO_LINE = 'echo: something'
COMMENT_LINE = '// something'
TEMPERATURE_AUTO_REPORT = ' T:25.00 /0.00 B:25.00 /0.00 @:0 B@:0'
POSITION_AUTO_REPORT = 'X:100.00 Y:100.00 Z:0.00 E:0.00 Count X:8000 Y:8000 Z:0'

@pytest.fixture
def okCommand():
    return OkCommand(REQUEST)

def test_Init(okCommand):
    assert(okCommand.request == REQUEST)
    assert(okCommand.error is None)
    assert(okCommand.result is None)

def test_Ok(okCommand):
    assert(okCommand._processLine('ok'))
    assert(okCommand.request == REQUEST)
    assert(okCommand.error is None)
    assert(okCommand.result is None)

def test_BadOk(okCommand):
    with pytest.raises(GCodeError):
        okCommand._processLine('bad')
    assert(okCommand.request == REQUEST)
    assert(okCommand.error is None)
    assert(okCommand.result is None)

def test_AdvancedOk(okCommand):
    assert(okCommand._processLine('ok P0 B0'))
    assert(okCommand.request == REQUEST)
    assert(okCommand.error is None)
    assert(okCommand.result is None)

def test_MetaAndAutoReports(okCommand):
    assert(not okCommand._processLine(ECHO_LINE))
    assert(not okCommand._processLine(COMMENT_LINE))
    assert(not okCommand.processLine(POSITION_AUTO_REPORT))
    assert(not okCommand.processLine(TEMPERATURE_AUTO_REPORT))

    assert(okCommand._processLine('ok'))
    assert(okCommand.request == REQUEST)
    assert(okCommand.error is None)
    assert(okCommand.result is None)
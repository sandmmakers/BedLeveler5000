from Printers.Marlin2.Commands.CommandM114 import CommandM114
from Printers.Marlin2.Commands.GCodeError import GCodeError
from dataclasses import dataclass, field
from typing import Union
import pytest

@dataclass(frozen=True)
class TestPoint:
    __test__ = False
    lines: [str]
    d: bool = field(default=False)
    e: bool = field(default=False)
    r: bool = field(default=False)
    expected: dict = field(default=None)

testPoints = [
    TestPoint(lines = ['X:100.00 Y:100.00 Z:0.00 E:124.00 Count X:8000 Y:8000 Z:0',
                       'ok P15 B3'],
              expected = {'x': 100.00,
                          'y': 100.00,
                          'z': 0.00,
                          'e': 124.00,
                          'count': {'x': 8000,
                                    'y': 8000,
                                    'z': 0}}),

    #SENT: 'M114 D'
    #RECV: 'X:100.00 Y:100.00 Z:0.00 E:124.00 Count X:8000 Y:8000 Z:0'
    #RECV: ''
    #RECV: 'Logical: X: 100.000 Y: 100.000 Z: 0.000'
    #RECV: 'Raw:     X: 100.000 Y: 100.000 Z: 0.000'
    #RECV: 'Leveled: X: 100.000 Y: 100.000 Z: 0.000'
    #RECV: 'UnLevel: X: 100.000 Y: 100.000 Z: 0.000'
    #RECV: 'Stepper: X:8000 Y:8000 Z:0 E:62000'
    #RECV: 'FromStp: X: 100.000 Y: 100.000 Z: 0.000 E: 124.000'
    #RECV: 'Diff:    X: 0.000 Y: 0.000 Z: 0.000 E: 0.000'
    #RECV: 'ok P15 B3'
    #
    #SENT: 'M114 E'
    #RECV: 'Count E:62000'
    #RECV: 'ok P15 B3'
    ]

def createCommandM114(testPoint):
    return CommandM114(d = testPoint.d,
                       e = testPoint.e,
                       r = testPoint.r,)

@pytest.mark.parametrize('testPoint', testPoints)
def test_VerifyCorrect(testPoint):
    commandM114 = createCommandM114(testPoint)
    for index, line in enumerate(testPoint.lines):
        result = commandM114._processLine(line)
        isLast = index == len(testPoint.lines) - 1
        assert(isLast == result)
    assert(commandM114.result == testPoint.expected)
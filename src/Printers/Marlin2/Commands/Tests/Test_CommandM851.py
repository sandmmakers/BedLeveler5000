from Printers.Marlin2.Commands.CommandM851 import CommandM851
from Printers.Marlin2.Commands.GCodeError import GCodeError
from dataclasses import dataclass, field
from typing import Union
import pytest

@dataclass(frozen=True)
class TestPoint:
    __test__ = False
    lines: [str]
    x: Union[None, float] = field(default=None)
    y: Union[None, float] = field(default=None)
    z: Union[None, float] = field(default=None)
    expected: dict = field(default=None)

testPoints = [
    TestPoint(lines = ['  M851 X1 Y2.00 Z3.50 ; (mm)',
                       'ok P15 B3'],
              expected = {'x': 1.00,
                          'y': 2.00,
                          'z': 3.50}),
    TestPoint(lines = ['Probe Offset X-40.00 Y-5.00 Z0.00',
                       'ok'],
              expected = {'x': -40.0,
                          'y': -5.00,
                          'z': 0.00})

    #SENT: 'M851 X0'
    #RECV: 'ok P15 B3'

    #SENT: 'M851 X1'
    #RECV: '?X must be 0 (NOZZLE_AS_PROBE).'
    #RECV: 'ok P15 B3'
    ]

def createCommandM851(testPoint):
    return CommandM851(x = testPoint.x,
                       y = testPoint.y,
                       z = testPoint.z)

@pytest.mark.parametrize('testPoint', testPoints)
def test_VerifyCorrect(testPoint):
    commandM851 = createCommandM851(testPoint)
    for index, line in enumerate(testPoint.lines):
        result = commandM851._processLine(line)
        isLast = index == len(testPoint.lines) - 1
        assert(isLast == result)
    assert(commandM851.result == testPoint.expected)
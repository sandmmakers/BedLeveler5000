from Printers.Marlin2.Commands.CommandG30 import CommandG30
from Printers.Marlin2.Commands.GCodeError import GCodeError
from dataclasses import dataclass, field
from typing import Union
import pytest

@dataclass(frozen=True)
class TestPoint:
    __test__ = False
    lines: [str]
    c: bool = field(default=False)
    e: bool = field(default=False)
    x: Union[None, float] = field(default=None)
    y: Union[None, float] = field(default=None)
    expected: dict = field(default=None)

testPoints = [
    TestPoint(lines = ['echo:busy: processing',
                       'echo:busy: processing',
                       'echo:busy: processing',
                       'Bed X: 100.00 Y: 200.00 Z: 1.00',
                       'X:110.00 Y:220.00 Z:0.00 E:124.00 Count X:8000 Y:9000 Z:2',
                       'ok P15 B3'],
              expected = {'bed': {'x': 100.00,
                                  'y': 200.00,
                                  'z':   1.00},
                          'position': {'x': 110.00,
                                       'y': 220.00,
                                       'z':   0.00,
                                       'e': 124.00,
                                       'count': {'x': 8000,
                                                 'y': 9000,
                                                 'z': 2}}}),

    #SENT: 'G30 X-42'
    #RECV: 'ok'

    #SENT: 'G30 X-42'
    #RECV: 'Z Probe Past Bed'
    #RECV: 'ok P15 B3'

    TestPoint(lines = ['echo:busy: processing',
                       'Taring probe',
                       'Taring probe',
                       'echo:busy: processing',
                       'echo:busy: processing',
                       'echo:busy: processing',
                       'Bed X: 100.00 Y: 100.00 Z: 0.00',
                       'X:100.00 Y:100.00 Z:0.00 E:0.00 Count X:8000 Y:8000 Z:0',
                       'ok P15 B3'],
              expected = {'bed': {'x': 100.00,
                                  'y': 100.00,
                                  'z':   0.00},
                          'position': {'x': 100.00,
                                       'y': 100.00,
                                       'z':   0.00,
                                       'e':   0.00,
                                       'count': {'x': 8000,
                                                 'y': 8000,
                                                 'z': 0}}}),

    TestPoint(lines = ['Bed X:100.00 Y:100.00 Z:0.000',
                       'X:100.00 Y:100.00 Z:0.00 E:0.00 Count X:8000 Y:8000 Z:0',
                       'ok P15 B3'],
              expected = {'bed': {'x': 100.00,
                                  'y': 100.00,
                                  'z':   0.00},
                          'position': {'x': 100.00,
                                       'y': 100.00,
                                       'z':   0.00,
                                       'e':   0.00,
                                       'count': {'x': 8000,
                                                 'y': 8000,
                                                 'z': 0}}})
    ]

def createCommandG30(testPoint):
    return CommandG30(c = testPoint.c,
                      e = testPoint.e,
                      x = testPoint.x,
                      y = testPoint.y)

@pytest.mark.parametrize('testPoint', testPoints)
def test_VerifyCorrect(testPoint):
    commandG30 = createCommandG30(testPoint)
    for index, line in enumerate(testPoint.lines):
        result = commandG30._processLine(line)
        isLast = index == len(testPoint.lines) - 1
        assert(isLast == result)
    assert(commandG30.result == testPoint.expected)
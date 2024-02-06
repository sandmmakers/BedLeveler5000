from Printers.Marlin2.Commands.CommandG28 import CommandG28
from Printers.Marlin2.Commands.GCodeError import GCodeError
from dataclasses import dataclass, field
from typing import Union
import pytest

@dataclass(frozen=True)
class TestPoint:
    __test__ = False
    lines: [str]
    l: bool = field(default=False)
    o: bool = field(default=False)
    r: Union[None, float] = field(default=None)
    x: bool = field(default=False)
    y: bool = field(default=False)
    z: bool = field(default=False)
    expected: dict = field(default=None)

testPoints = [
    TestPoint(lines = ['echo:busy: processing',
                       'echo:busy: processing',
                       'echo:busy: processing',
                       'echo:busy: processing',
                       'echo:busy: processing',
                       'echo:busy: processing',
                       'echo:busy: processing',
                       'echo:busy: processing',
                       'X:100.00 Y:200.00 Z:0.00 E:124.00 Count X:8000 Y:9000 Z:2',
                       'ok P15 B3'],
              expected = {'x': 100.00,
                          'y': 200.00,
                          'z': 0.00,
                          'e': 124.00,
                          'count': {'x': 8000,
                                    'y': 9000,
                                    'z': 2}}),

    # TODO:
    #SENT: 'G28 L R32 O'
    #RECV: 'ok P15 B3'

    TestPoint(lines = ['echo:busy: processing',
                       'echo:busy: processing',
                       'Taring probe',
                       'echo:busy: processing',
                       'echo:busy: processing',
                       'echo:busy: processing',
                       'echo:busy: processing',
                       'X:100.00 Y:200.00 Z:0.00 E:124.00 Count X:8000 Y:9000 Z:2',
                       'ok P15 B3'],
              expected = {'x': 100.00,
                          'y': 200.00,
                          'z': 0.00,
                          'e': 124.00,
                          'count': {'x': 8000,
                                    'y': 9000,
                                    'z': 2}}),
    ]

def createCommandG28(testPoint):
    return CommandG28(l = testPoint.l,
                     o = testPoint.o,
                     r = testPoint.r,
                     x = testPoint.x,
                     y = testPoint.y,
                     z = testPoint.z)

@pytest.mark.parametrize('testPoint', testPoints)
def test_VerifyCorrect(testPoint):
    commandG28 = createCommandG28(testPoint)
    for index, line in enumerate(testPoint.lines):
        result = commandG28._processLine(line)
        isLast = index == len(testPoint.lines) - 1
        assert(isLast == result)
    assert(commandG28.result == testPoint.expected)
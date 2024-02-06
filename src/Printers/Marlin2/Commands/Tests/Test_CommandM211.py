from Printers.Marlin2.Commands.CommandM211 import CommandM211
from Printers.Marlin2.Commands.GCodeError import GCodeError
from dataclasses import dataclass
from typing import Union
import pytest

@dataclass(frozen=True)
class TestPoint:
    __test__ = False
    s: Union[int, None]
    lines: [str]
    expected: dict

testPoints = [
    # Stanard set
    TestPoint(s = 0,
              lines = ['ok'],
              expected = None),
    TestPoint(s = 1,
              lines = ['ok'],
              expected = None),

    # Standard set with advanced OK
    TestPoint(s = 0,
              lines = ['ok P15 B3'],
              expected = None),
    TestPoint(s = 1,
              lines = ['ok P15 B3'],
              expected = None),

    # Ender set
    TestPoint(s = 0,
              lines = ['echo:Soft endstops: ON  Min:  X0.00 Y0.00 Z0.00   Max:  X235.00 Y235.00 Z250.00',
                       'ok'],
              expected = None),
    TestPoint(s = 1,
              lines = ['echo:Soft endstops: ON  Min:  X1.23 Y4.56 Z7.89   Max:  X235.00 Y235.00 Z250.00',
                       'ok'],
              expected = None),

    # Standard query
    TestPoint(s = None,
              lines = ['  M211 S1 ; ON',
                       '  Min:  X0.00 Y-6.00 Z0.00   Max:  X430.00 Y430.00 Z500.00',
                       'ok'],
              expected = {
                'on': True,
                'minX': 0.0,
                'minY': -6.0,
                'minZ': 0.0,
                'maxX': 430.0,
                'maxY': 430.0,
                'maxZ': 500.0}
              ),

    # Ender query
    TestPoint(s = None,
              lines = ['echo:Soft endstops: ON  Min:  X0.00 Y1.23 Z0.00   Max:  X235.00 Y235.00 Z250.00',
                       'ok'],
              expected = {
                'on': True,
                'minX': 0.0,
                'minY': 1.23,
                'minZ': 0.0,
                'maxX': 235.0,
                'maxY': 235.0,
                'maxZ': 250.0}
              )
    ]

@pytest.mark.parametrize('testPoint', testPoints)
def test_VerifyCorrect(testPoint):
    commandM211 = CommandM211(s=testPoint.s)
    for index, line in enumerate(testPoint.lines):
        result = commandM211._processLine(line)
        isLast = index == len(testPoint.lines) - 1
        assert(isLast == result)
    assert(commandM211.result == testPoint.expected)
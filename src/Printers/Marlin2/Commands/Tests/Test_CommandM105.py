from Printers.Marlin2.Commands.CommandM105 import CommandM105
from Printers.Marlin2.Commands.GCodeError import GCodeError
from dataclasses import dataclass, field
from typing import Union
import pytest

@dataclass(frozen=True)
class TestPoint:
    __test__ = False
    lines: [str]
    r: bool = field(default=False)
    t: Union[None, int] = field(default=None)
    expected: dict = field(default=None)

ValidTestPoints = [
    # Basic
    TestPoint(lines = ['ok T:127.97 /12.00 B:25.00 /0.00 @:12.2 B@:21.2'],
              expected = {'toolActual': 127.97,
                          'toolDesired': 12.00,
                          'bedActual':   25.00,
                          'bedDesired':   0.00,
                          'toolPower':   12.20,
                          'bedPower':    21.20}),

    # Basic plus individual tools
    TestPoint(lines = ['ok T:245.00 /245.00 B:70.01 /70.00 T0:245.00 /245.00 T1:18.83 /0.00 @:58 B@:52 @0:58 @1:0'],
              expected = {'toolActual':  245.00,
                          'toolDesired': 245.00,
                          'bedActual':    70.01,
                          'bedDesired':   70.00,
                          'toolPower':    58.00,
                          'bedPower':     52.00}),

    # No current tool
    TestPoint(lines = ['ok B:70.01 /70.00 T0:245.00 /245.00 T1:18.83 /0.00 B@:52 @0:58 @1:0'],
              expected = {'toolActual':  245.00,
                          'toolDesired': 245.00,
                          'bedActual':    70.01,
                          'bedDesired':   70.00,
                          'toolPower':    58.00,
                          'bedPower':     52.00}),

    # Basic plus individual tools and others
    TestPoint(lines = ['ok T:245.00 /245.00 B:70.01 /70.00 T0:245.00 /245.00 T1:18.83 /0.00 X:25.11 /36.00 A:38.55 /0.00 @:58 B@:52 @0:58 @1:0 FAN0@:123 FAN1@:234 HBR@:0'],
              expected = {'toolActual':  245.00,
                          'toolDesired': 245.00,
                          'bedActual':    70.01,
                          'bedDesired':   70.00,
                          'toolPower':    58.00,
                          'bedPower':     52.00})]

def createCommandM105(testPoint):
    return CommandM105(r = testPoint.r,
                       t = testPoint.t)

@pytest.mark.parametrize('testPoint', ValidTestPoints)
def test_VerifyCorrect(testPoint):
    commandM105 = createCommandM105(testPoint)
    for index, line in enumerate(testPoint.lines):
        result = commandM105._processLine(line)
        isLast = index == len(testPoint.lines) - 1
        assert(isLast == result)
    assert(commandM105.result == testPoint.expected)

AssertingTestPoints = [
    # Empty
    TestPoint(lines = ['']),

    # Missing 'ok'
    TestPoint(lines = ['/123 T:127.97 /12.00 B:25.00 /0.00 @:12.2 B@:21.2']),

    # Extra '\' token
    TestPoint(lines = ['ok /123 T:127.97 /12.00 B:25.00 /0.00 @:12.2 B@:21.2']),

    # Extra '\' token in middle
    TestPoint(lines = ['ok T:127.97 /12.00 B:25.00 /0.00 /123 @:12.2 B@:21.2']),

    # Missing temp
    TestPoint(lines = ['ok B:25.00 /0.00 /123 @:12.2 B@:21.2']),

     # Extra temp
    TestPoint(lines = ['ok T:127.97 /12.00 T:127.97 /12.00 B:25.00 /0.00 @:12.2 B@:21.2']),

     # Temp missing desired
    TestPoint(lines = ['ok T:127.97 B:25.00 /0.00 @:12.2 B@:21.2']),

     # Bed missing desired
    TestPoint(lines = ['ok T:127.97 /12.00 B:25.00 @:12.2 B@:21.2'])]

@pytest.mark.parametrize('testPoint', AssertingTestPoints)
def test_VerifyIncorrect(testPoint):
    commandM105 = createCommandM105(testPoint)
    for index, line in enumerate(testPoint.lines):
        with pytest.raises(GCodeError):
            commandM105._processLine(line)
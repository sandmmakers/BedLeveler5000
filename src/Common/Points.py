from typing import NamedTuple

class Point2(NamedTuple):
    x: int
    y: int

class NamedPoint2(NamedTuple):
    name: str
    x: int
    y: int

class Point2F(NamedTuple):
    x: float
    y: float

class NamedPoint2F(NamedTuple):
    name: str
    x: float
    y: float

class Point3(NamedTuple):
    x: int
    y: int
    z: int

class NamedPoint3(NamedTuple):
    name: str
    x: int
    y: int
    z: int

class Point3F(NamedTuple):
    x: float
    y: float
    z: float

class NamedPoint3F(NamedTuple):
    name: str
    x: float
    y: float
    z: float
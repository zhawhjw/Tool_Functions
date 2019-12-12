import math


def p(x, y):
    return [x + y, x + y]


def a(x, y):
    return math.copysign(x, y), math.acos(x)

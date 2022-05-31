# -*- coding: utf-8 -*-
# This follows the PhysicsDriver concepts and solves with an implicit time scheme tau \partial y / \partial t + a y = x + b, where a, b and tau are parameters, x can be set as a input scalar and t is the time.
from __future__ import print_function, division

from c3po.PhysicsDriver import PhysicsDriver


class PhysicsScalarTransient(PhysicsDriver):
    def __init__(self):
        PhysicsDriver.__init__(self)
        self._result = 0.
        self._resultOld = 0.
        self._a = 0.
        self._b = 0.
        self._tau = 0.
        self._x = 0.
        self._time = 0.
        self._dt = 0.
        self._stationaryMode = False
        self._savedState = {}

    def setOption(self, a, b, tau):
        self._a = a
        self._b = b
        self._tau = tau

    def initialize(self):
        self._result = 0.
        self._resultOld = 0.
        self._x = 0.
        self._time = 0.
        self._dt = 0.
        self._savedState = {}
        return True

    def terminate(self):
        pass

    def presentTime(self):
        return self._time

    def computeTimeStep(self):
        return (0.2, False)

    def initTimeStep(self, dt):
        self._dt = dt
        return True

    def solveTimeStep(self):
        if self._dt > 0:
            self._result = ((self._x + self._b) + self._resultOld * self._tau / self._dt) / (self._tau / self._dt + self._a)
        else:
            self._result = ((self._x + self._b) / self._a)
        return True

    def setStationaryMode(self, stationaryMode):
        self._stationaryMode = stationaryMode

    def getStationaryMode(self):
        return self._stationaryMode

    def validateTimeStep(self):
        self._time += self._dt
        self._resultOld = self._result

    def abortTimeStep(self):
        self._dt = 0.

    def isStationary(self):
        if self._a == 0.:
            raise ValueError("Undefined steady state.")
        if (self._x + self._b) == 0.:
            return abs(self._result) < 1.E-6
        return abs(self._result / ((self._x + self._b) / self._a) - 1.) < 1.E-6

    def resetTime(self, time_):
        self._time = time_

    def save(self, label, method):
        if method != "INTERNAL":
            raise ValueError("Unknown saving method")
        self._savedState[label] = [self._result, self._resultOld, self._a, self._b ,self._tau, self._x, self._time, self._stationaryMode]

    def restore(self, label, method):
        if method != "INTERNAL":
            raise ValueError("Unknown saving method")
        self._result            = self._savedState[label][0]
        self._resultOld         = self._savedState[label][1]
        self._a                 = self._savedState[label][2]
        self._b                 = self._savedState[label][3]
        self._tau               = self._savedState[label][4]
        self._x                 = self._savedState[label][5]
        self._time              = self._savedState[label][6]
        self._stationaryMode    = self._savedState[label][7]

    def forget(self, label, method):
        if method != "INTERNAL":
            raise ValueError("Unknown saving method")
        try:
            self._savedState[label]
        except:
            pass

    def getOutputDoubleValue(self, name):
        if name == "y":
            return self._result
        else:
            raise Exception("physicsScalar.getOutputDoubleValue Only y output available (found {}).".format(name))

    def setInputDoubleValue(self, name, value):
        if name == "x":
            self._x = value

    def getInputValuesNames(self):
        return ["x"]

    def getOutputValuesNames(self):
        return ["y"]

# -*- coding: utf-8 -*-
# This follows the PhysicsDriver concepts and returns y = a + b*x where a and b are parameters and x can be set as a input scalar.
from __future__ import print_function, division

from c3po.PhysicsDriver import PhysicsDriver

class WorkerDriver(PhysicsDriver):
    def __init__(self):
        PhysicsDriver.__init__(self)
        self._result = 0.
        self._inputDouble = 0.
        self._inputInt = 0.
        self._inputString = 0.
        self._time = 0.
        self._dt = 0.
        self._stationaryMode = False
        self._savedState = {}

    def initialize(self):
        self._result = 0.
        self._inputDouble = 0.
        self._inputInt = 0.
        self._inputString = 0.
        self._time = 0.
        self._dt = 0.
        self._stationaryMode = False
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
        self._result = (self._time + self._dt) * self._inputDouble
        return True

    def setStationaryMode(self, stationaryMode):
        self._stationaryMode = stationaryMode

    def getStationaryMode(self):
        return self._stationaryMode

    def validateTimeStep(self):
        self._time += self._dt

    def abortTimeStep(self):
        self._dt = 0.

    def isStationary(self):
        return True

    def resetTime(self, time_):
        self._time = time_

    def iterateTimeStep(self):
        """! See PhysicsDriver.iterateTimeStep(). """
        status = self.solveTimeStep()
        return status, True

    def save(self, label, method):
        if method != "INTERNAL":
            raise ValueError("Unknown saving method")
        self._savedState[label] = [self._result, self._inputDouble, self._inputInt, self._inputString, self._time, self._stationaryMode]

    def restore(self, label, method):
        if method != "INTERNAL":
            raise ValueError("Unknown saving method")
        self._result = self._savedState[label][0]
        self._inputDouble = self._savedState[label][1]
        self._inputInt = self._savedState[label][2]
        self._inputString = self._savedState[label][3]
        self._time = self._savedState[label][4]
        self._stationaryMode = self._savedState[label][5]

    def forget(self, label, method):
        if method != "INTERNAL":
            raise ValueError("Unknown saving method")
        try:
            self._savedState[label]
        except:
            pass

    def setInputDoubleValue(self, name, value):
        if name == "inputDouble":
            self._inputDouble = value

    def setInputIntValue(self, name, value):
        if name == "inputInt":
            self._inputInt = value

    def setInputStringValue(self, name, value):
        if name == "inputString":
            self._inputString = value

    def getInputValuesNames(self):
        return ["inputDouble", "inputInt", "inputString"]

    def getOutputValuesNames(self):
        return ["outputDouble", "outputInt", "outputString", "result"]

    def getValueType(self, name):
        if name.endswith("Double") or name == "result":
            return "Double"
        if name.endswith("Int"):
            return "Int"
        if name.endswith("String"):
            return "String"
        raise Exception("unknown value")

    def getValueUnit(self, name):
        return "totoUnit"

    def getOutputDoubleValue(self, name):
        if name == "outputDouble":
            return self._inputDouble
        elif name == "result":
            return self._result
        raise Exception("unknown value")

    def getOutputIntValue(self, name):
        if name == "outputInt":
            return self._inputInt
        raise Exception("unknown value")

    def getOutputStringValue(self, name):
        if name == "outputString":
            return self._inputString
        raise Exception("unknown value")
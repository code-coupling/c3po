# -*- coding: utf-8 -*-
# This follows the PhysicsDriver concepts and returns y = a + b*x where a and b are parameters and x can be set as a input scalar.
from __future__ import print_function, division

from c3po.PhysicsDriver import PhysicsDriver


class PhysicsScalar(PhysicsDriver):
    def __init__(self):
        PhysicsDriver.__init__(self)
        self.result_ = 0.
        self.a_ = 0.
        self.b_ = 0.
        self.x_ = 0.
        self._stationaryMode = False

    def setOption(self, a, b):
        self.a_ = a
        self.b_ = b

    def initialize(self):
        return True

    def terminate(self):
        pass

    def initTimeStep(self, dt):
        return True

    def solveTimeStep(self):
        self.result_ = self.a_ + self.b_ * self.x_
        return True

    def setStationaryMode(self, stationaryMode):
        self._stationaryMode = stationaryMode

    def getStationaryMode(self):
        return self._stationaryMode

    def abortTimeStep(self):
        pass

    def validateTimeStep(self):
        pass

    def getOutputDoubleValue(self, name):
        if name == "y":
            return self.result_
        else:
            raise Exception("PhysicsScalar.getOutputDoubleValue Only y output available.")

    def setInputDoubleValue(self, name, value):
        if name == "x":
            self.x_ = value

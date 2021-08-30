# -*- coding: utf-8 -*-
# This follows the PhysicsDriver concepts and returns y = a*(1+t) + b*x where a and b are parameters, x can be set as a input scalar and t is the present time.
from __future__ import print_function, division

from c3po.PhysicsDriver import PhysicsDriver


class PhysicsScalarTransient(PhysicsDriver):
    def __init__(self):
        PhysicsDriver.__init__(self)
        self.result_ = 0.
        self.a_ = 0.
        self.b_ = 0.
        self.x_ = 0.
        self.t_ = 0.
        self.dt_ = 0.
        self._stationaryMode = False

    def setOption(self, a, b):
        self.a_ = a
        self.b_ = b

    def initialize(self):
        self.result_ = 0.
        self.a_ = 0.
        self.b_ = 0.
        self.x_ = 0.
        self.t_ = 0.
        self.dt_ = 0.
        return True

    def terminate(self):
        pass

    def presentTime(self):
        return self.t_

    def computeTimeStep(self):
        return (0.3, self.t_ >= 1.)

    def initTimeStep(self, dt):
        self.dt_ = dt
        return True

    def solveTimeStep(self):
        self.result_ = self.a_ * (1 + self.t_) + self.b_ * self.x_
        print("result =", self.a_, "*", (1 + self.t_), "+", self.b_, "*", self.x_)
        return True

    def setStationaryMode(self, stationaryMode):
        self._stationaryMode = stationaryMode

    def getStationaryMode(self):
        return self._stationaryMode

    def validateTimeStep(self):
        self.t_ += self.dt_

    def abortTimeStep(self):
        self.dt_ = 0.

    def resetTime(self, time_):
        self.t_ = time_

    def getOutputDoubleValue(self, name):
        if name == "y":
            return self.result_
        else:
            raise Exception("physicsScalar.getOutputDoubleValue Only y output available.")

    def setInputDoubleValue(self, name, value):
        if name == "x":
            self.x_ = value

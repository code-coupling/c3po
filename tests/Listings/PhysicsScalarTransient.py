# -*- coding: utf-8 -*-
# This follows the PhysicsDriver concepts and returns y = a*(1+t) + b*x where a and b are parameters, x can be set as a input scalar and t is the present time.
from __future__ import print_function, division

from C3PO.PhysicsDriver import PhysicsDriver


class PhysicsScalarTransient(PhysicsDriver):
    def __init__(self):
        PhysicsDriver.__init__(self)
        self.result_ = 0.
        self.a_ = 0.
        self.b_ = 0.
        self.x_ = 0.
        self.t_ = 0.
        self.dt_ = 0.

    def setOption(self, a, b):
        self.a_ = a
        self.b_ = b

    # Initialize the object.
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

    # Solve next time-step problem. Solves a steady state if dt < 0.
    def solveTimeStep(self):
        self.result_ = self.a_ * (1 + self.t_) + self.b_ * self.x_
        print("result =", self.a_, "*", (1 + self.t_), "+", self.b_, "*", self.x_)
        return True

    def validateTimeStep(self):
        self.t_ += self.dt_

    # Abort previous time-step solving.
    def abortTimeStep(self):
        self.dt_ = 0.

    # Return an output scalar
    def getValue(self, name):
        if name == "y":
            return self.result_
        else:
            raise Exception("physicsScalar.getValue Only y output available.")

    # Import an input scalar. No return.
    def setValue(self, name, value):
        if name == "x":
            self.x_ = value

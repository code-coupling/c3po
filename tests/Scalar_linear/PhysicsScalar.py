# -*- coding: utf-8 -*-
# This follows the PhysicsDriver concepts and returns y = a + b*x where a and b are parameters and x can be set as a input scalar.
from __future__ import print_function, division

from C3PO.PhysicsDriver import PhysicsDriver


class PhysicsScalar(PhysicsDriver):
    def __init__(self):
        PhysicsDriver.__init__(self)
        self.result_ = 0.
        self.a_ = 0.
        self.b_ = 0.
        self.x_ = 0.

    def setOption(self, a, b):
        self.a_ = a
        self.b_ = b

    # Initialize the object.
    def initialize(self):
        return True

    def terminate(self):
        pass

    def initTimeStep(self, dt):
        return True

    # Solve next time-step problem. Solves a steady state if dt < 0.
    def solveTimeStep(self):
        self.result_ = self.a_ + self.b_ * self.x_
        return True

    # Abort previous time-step solving.
    def abortTimeStep(self):
        pass

    # Return an output scalar
    def getValue(self, name):
        if name == "y":
            return self.result_
        else:
            raise Exception("PhysicsScalar.getValue Only y output available.")

    # Import an input scalar. No return.
    def setValue(self, name, value):
        if name == "x":
            self.x_ = value

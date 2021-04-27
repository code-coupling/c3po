# -*- coding: utf-8 -*-
# This follows the PhysicsDriver concepts and returns y = (a*x + b)/||a*x + b||  where a and b are given (matrix and vector) and x can be set as a scalar inputs.
from __future__ import print_function, division
import numpy as np

from c3po.PhysicsDriver import PhysicsDriver


class PhysicsMatrix(PhysicsDriver):
    def __init__(self):
        PhysicsDriver.__init__(self)
        self.taille_ = 4
        self.A_ = np.zeros(shape=(self.taille_, self.taille_))
        self.b_ = np.zeros(shape=(self.taille_))

        self.result_ = np.zeros(shape=(self.taille_))
        self.vp_ = 0.
        self.x_ = np.zeros(shape=(self.taille_))

    # Initialize the object.
    def initialize(self):
        self.A_[0, 0] = 2.
        self.A_[0, 1] = 3.
        self.A_[0, 2] = -5.
        self.A_[0, 3] = 7.

        self.A_[1, 0] = 4.
        self.A_[1, 1] = 13.
        self.A_[1, 2] = -8.
        self.A_[1, 3] = -2.

        self.A_[2, 0] = 1.
        self.A_[2, 1] = 2.
        self.A_[2, 2] = 7.
        self.A_[2, 3] = -6.

        self.A_[3, 0] = 3.
        self.A_[3, 1] = 4.
        self.A_[3, 2] = 5.
        self.A_[3, 3] = 7.

        self.result_ = np.zeros(shape=(self.taille_))
        self.vp_ = 0.
        self.x_ = np.zeros(shape=(self.taille_))
        self.x_[0] = 1.
        return True

    def terminate(self):
        pass

    def initTimeStep(self, dt):
        return True

    # Solve next time-step problem. Solves a steady state if dt < 0. No return.
    def solveTimeStep(self):
        self.result_ = np.dot(self.A_, self.x_) + self.b_
        self.vp_ = np.linalg.norm(self.result_)
        self.result_ /= self.vp_
        return True

    # Abort previous time-step solving. No return. No return.
    def abortTimeStep(self):
        pass

    # Return an output scalar
    def getValue(self, name):
        if name == "taille":
            return self.taille_
        if name == "valeur_propre":
            return self.vp_
        int_name = int(name)
        if int_name >= 0 and int_name < self.taille_:
            return self.result_[int_name]
        else:
            raise Exception("PhysicsMatrix.getValue only outputs between 0 and " + str(self.taille_ - 1) + " available.")

    # Import an input scalar. No return.
    def setValue(self, name, value):
        int_name = int(name)
        if int_name >= 0 and int_name < self.taille_:
            self.x_[int_name] = value
        else:
            raise Exception("PhysicsMatrix.setValue only inputs between 0 and " + str(self.taille_ - 1) + " allowed.")

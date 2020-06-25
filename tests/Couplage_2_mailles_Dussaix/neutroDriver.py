# -*- coding: utf-8 -*-
# This class is the "neutronic" part of the two meshes model.
from __future__ import print_function, division
from math import *
import numpy

import MEDCoupling

import MEDBuilder
from C3PO.physicsDriver import physicsDriver


class neutroDriver(physicsDriver):
    def __init__(self):
        physicsDriver.__init__(self)
        self.densities_ = [1., 1.]
        self.MEDResu_ = 0
        self.meanT_ = 1.
        self.isInit_ = False

    # Initialize the object.
    def initialize(self):
        if not self.isInit_:
            self.MEDResu_ = MEDBuilder.makeFieldCarre()
            self.isInit_ = True
        return True

    def terminate(self):
        return True

    def initTimeStep(self, dt):
        return True

    # Solve next time-step problem. Solves a steady state if dt < 0.
    def solveTimeStep(self):
        v = [self.meanT_ * self.densities_[0] / (self.densities_[0] + self.densities_[1]) + self.meanT_ / 2., self.meanT_ * self.densities_[1] / (self.densities_[0] + self.densities_[1]) + self.meanT_ / 2.]
        array = MEDCoupling.DataArrayDouble.New()
        array.setValues(v, len(v), 1)
        self.MEDResu_.setArray(array)
        return True

    # Abort previous time-step solving. No return.
    def abortTimeStep(self):
        pass

    # Return an output scalar
    def getOutputMEDField(self, name):
        if name == "Temperatures":
            return self.MEDResu_
        else:
            raise Exception("neutroDriver.getOutputMEDField Only Temperatures output available.")

    # Import an input scalar. No return.
    def setInputMEDField(self, name, field):
        if name == "Densities":
            array = field.getArray()
            self.densities_[0] = array.getIJ(0, 0)
            self.densities_[1] = array.getIJ(1, 0)

    def getInputMEDFieldTemplate(self, name):
        return self.MEDResu_

    def setValue(self, name, value):
        if name == "meanT":
            self.meanT_ = value

# -*- coding: utf-8 -*-
# This class is the "neutronic" part of the two meshes model.
from __future__ import print_function, division
from math import *
import numpy

import c3po.medcouplingCompat as mc

import MEDBuilder
from c3po.PhysicsDriver import PhysicsDriver


class NeutroDriver(PhysicsDriver):
    def __init__(self):
        PhysicsDriver.__init__(self)
        self.densities_ = [1., 1.]
        self.MEDResu_ = 0
        self.meanT_ = 1.
        self.isInit_ = False
        self._stationaryMode = False

    def initialize(self):
        if not self.isInit_:
            self.MEDResu_ = MEDBuilder.makeFieldCarre()
            self.isInit_ = True
        return True

    def terminate(self):
        pass

    def initTimeStep(self, dt):
        return True

    def solveTimeStep(self):
        v = [self.meanT_ * self.densities_[0] / (self.densities_[0] + self.densities_[1]) + self.meanT_ / 2., self.meanT_ * self.densities_[1] / (self.densities_[0] + self.densities_[1]) + self.meanT_ / 2.]
        array = mc.DataArrayDouble.New()
        array.setValues(v, len(v), 1)
        self.MEDResu_.setArray(array)
        return True

    def setStationaryMode(self, stationaryMode):
        self._stationaryMode = stationaryMode

    def getStationaryMode(self):
        return self._stationaryMode

    def validateTimeStep(self):
        pass

    def abortTimeStep(self):
        pass

    def getOutputMEDDoubleField(self, name):
        if name == "Temperatures":
            resu = self.MEDResu_
            try:
                resu.setMesh(self.MEDResu_.getMesh().deepCopy())
            except:
                resu.setMesh(self.MEDResu_.getMesh().deepCpy())
            return resu
        else:
            raise Exception("NeutroDriver.getOutputMEDDoubleField Only Temperatures output available.")

    def updateOutputMEDDoubleField(self, name, field):
        if name == "Temperatures":
            field.setArray(self.MEDResu_.getArray())
        else:
            raise Exception("NeutroDriver.updateOutputMEDDoubleField Only Temperatures output available.")

    def setInputMEDDoubleField(self, name, field):
        if name == "Densities":
            array = field.getArray()
            self.densities_[0] = array.getIJ(0, 0)
            self.densities_[1] = array.getIJ(1, 0)

    def getInputMEDDoubleFieldTemplate(self, name):
        return self.MEDResu_

    def setInputDoubleValue(self, name, value):
        if name == "meanT":
            self.meanT_ = value

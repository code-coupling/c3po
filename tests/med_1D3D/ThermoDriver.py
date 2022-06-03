# -*- coding: utf-8 -*-
from __future__ import print_function, division
import math

import c3po.medcouplingCompat as mc

import tests.med_1D3D.MEDBuilder as MEDBuilder
from c3po.PhysicsDriver import PhysicsDriver


class ThermoDriver(PhysicsDriver):
    def __init__(self):
        PhysicsDriver.__init__(self)
        self._medP = None
        self._medT = None
        self._length = 3.001
        self._nMesh = 10
        self._stationaryMode = False
        self._T0 = 0.

    def setT0(self, T0):
        self._T0 = T0

    def initialize(self):
        self._medP = None
        self._medT = MEDBuilder.makeField1D(self._length, self._nMesh)
        self._stationaryMode = False
        return True

    def terminate(self):
        pass

    def initTimeStep(self, dt):
        if dt > 0.:
            return False
        return True

    def solveTimeStep(self):
        listP = [0.]*(self._nMesh)
        arrayT = self._medT.getArray()
        if self._medP is not None:
            arrayP = self._medP.getArray()
        else:
            arrayP = mc.DataArrayDouble(listP)
        for i in range(self._nMesh):
            arrayT.setIJ(i, 0, self._T0 + 2. * arrayP.getIJ(i, 0))
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
        if name == "Temperature":
            return self._medT.cloneWithMesh(True)
        else:
            raise Exception("ThermoDriver.getOutputMEDDoubleField : Only Temperature output available.")

    def updateOutputMEDDoubleField(self, name, field):
        if name == "Temperature":
            try:
                field.setArray(self._medT.getArray().deepCopy())
            except:
                field.setArray(self._medT.getArray().deepCpy())
        else:
            raise Exception("ThermoDriver.updateOutputMEDDoubleField : Only Temperature output available.")

    def setInputMEDDoubleField(self, name, field):
        if name == "Power":
            self._medP = field

    def getInputMEDDoubleFieldTemplate(self, name):
        return self._medT

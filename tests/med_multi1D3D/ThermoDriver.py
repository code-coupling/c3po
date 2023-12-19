# -*- coding: utf-8 -*-
from __future__ import print_function, division
import math

import c3po.medcouplingCompat as mc

import tests.medBuilder as medBuilder
from c3po.PhysicsDriver import PhysicsDriver


class ThermoDriver(PhysicsDriver):
    def __init__(self):
        PhysicsDriver.__init__(self)
        self._medP = None
        self._medPTemplate = None
        self._medT = None
        self._medBu = None
        self._medBuOld = None
        self._length = 3.001
        self._nMesh = 10
        self._stationaryMode = False
        self._T0 = 0.
        self._dt = 0.

    def setT0(self, T0):
        self._T0 = T0

    def initialize(self):
        self._medP = None
        self._medT = medBuilder.makeField1D(self._length, self._nMesh)
        self._medBu = medBuilder.makeField1D(self._length, self._nMesh)
        self._medBuOld = medBuilder.makeField1D(self._length, self._nMesh)
        self._medPTemplate = medBuilder.makeField1D(self._length, self._nMesh)
        self._medPTemplate.setNature(mc.ExtensiveMaximum)
        self._stationaryMode = False
        return True

    def terminate(self):
        pass

    def initTimeStep(self, dt):
        #if dt > 0.:
        #    return False
        self._dt = dt
        return True

    def solveTimeStep(self):
        listP = [0.] * (self._nMesh)
        arrayT = self._medT.getArray()
        arrayBu = self._medBu.getArray()
        arrayBuOld = self._medBuOld.getArray()
        if self._medP is not None:
            arrayP = self._medP.getArray()
        else:
            arrayP = mc.DataArrayDouble(listP)
        for i in range(self._nMesh):
            arrayT.setIJ(i, 0, self._T0 + 2. * arrayP.getIJ(i, 0))
            arrayBu.setIJ(i, 0, arrayBuOld.getIJ(i, 0) + self._dt * arrayP.getIJ(i, 0))
        return True

    def setStationaryMode(self, stationaryMode):
        self._stationaryMode = stationaryMode

    def getStationaryMode(self):
        return self._stationaryMode

    def validateTimeStep(self):
        arrayBu = self._medBu.getArray()
        arrayBuOld = self._medBuOld.getArray()
        for i in range(self._nMesh):
            arrayBuOld.setIJ(i, 0, arrayBu.getIJ(i, 0))

    def abortTimeStep(self):
        pass

    def getOutputMEDDoubleField(self, name):
        if name == "Temperature":
            return self._medT.cloneWithMesh(True)
        elif name == "Burn-up":
            return self._medBu.cloneWithMesh(True)
        else:
            raise Exception("ThermoDriver.getOutputMEDDoubleField : Only Temperature and Burn-up output available.")

    def updateOutputMEDDoubleField(self, name, field):
        if name == "Temperature":
            try:
                field.setArray(self._medT.getArray().deepCopy())
            except:
                field.setArray(self._medT.getArray().deepCpy())
        elif name == "Burn-up":
            try:
                field.setArray(self._medBu.getArray().deepCopy())
            except:
                field.setArray(self._medBu.getArray().deepCpy())
        else:
            raise Exception("ThermoDriver.updateOutputMEDDoubleField : Only Temperature and Burn-up output available.")

    def setInputMEDDoubleField(self, name, field):
        if name == "Power":
            self._medP = field

    def getInputMEDDoubleFieldTemplate(self, name):
        return self._medPTemplate

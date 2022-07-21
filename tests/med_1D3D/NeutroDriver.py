# -*- coding: utf-8 -*-
from __future__ import print_function, division
import math

import c3po.medcouplingCompat as mc

import tests.med_1D3D.MEDBuilder as MEDBuilder
from c3po.PhysicsDriver import PhysicsDriver


class NeutroDriver(PhysicsDriver):
    def __init__(self):
        PhysicsDriver.__init__(self)
        self._medP = None
        self._medT = None
        self._sizeX = 100.
        self._sizeY = 100.
        self._sizeZ = 500.
        self._nbMeshX = 4
        self._nbMeshY = 4
        self._nbMeshZ = 10
        self._stationaryMode = False

    def initialize(self):
        self._medP = MEDBuilder.makeFieldCarre(self._sizeX, self._sizeY, self._sizeZ, self._nbMeshX, self._nbMeshY, self._nbMeshZ)
        self._medT = None
        self._stationaryMode = False
        return True

    def terminate(self):
        pass

    def initTimeStep(self, dt):
        if dt > 0.:
            return False
        return True

    def solveTimeStep(self):
        arrayP = self._medP.getArray()
        listT = [1.] * (self._nbMeshX * self._nbMeshY * self._nbMeshZ)
        if self._medT is not None:
            arrayT = self._medT.getArray()
        else:
            arrayT = mc.DataArrayDouble(listT)
        dx = self._sizeX / self._nbMeshX
        dy = self._sizeY / self._nbMeshY
        dz = self._sizeZ / self._nbMeshZ
        imesh = 0
        for iz in range(self._nbMeshZ):
            for iy in range(self._nbMeshY):
                for ix in range(self._nbMeshX):
                    x = (ix + 0.5) * dx
                    y = (iy + 0.5) * dy
                    z = (iz + 0.5) * dz
                    arrayP.setIJ(imesh, 0, math.cos((x / (self._sizeX / 2.) - 1.) * math.pi / 2.) *
                                 math.cos((y / (self._sizeY / 2.) - 1.) * math.pi / 2.) *
                                 math.cos((z / (self._sizeZ / 2.) - 1.) * math.pi / 2.) *
                                 (1. - (arrayT.getIJ(imesh, 0) - 1.) * 0.2))
                    imesh += 1
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
        if name == "Power":
            return self._medP.cloneWithMesh(True)
        else:
            raise Exception("NeutroDriver.getOutputMEDDoubleField : Only Power output available.")

    def updateOutputMEDDoubleField(self, name, field):
        if name == "Power":
            try:
                field.setArray(self._medP.getArray().deepCopy())
            except:
                field.setArray(self._medP.getArray().deepCpy())
        else:
            raise Exception("NeutroDriver.updateOutputMEDDoubleField : Only Power output available.")

    def setInputMEDDoubleField(self, name, field):
        if name == "Temperature":
            self._medT = field

    def getInputMEDDoubleFieldTemplate(self, name):
        return self._medP

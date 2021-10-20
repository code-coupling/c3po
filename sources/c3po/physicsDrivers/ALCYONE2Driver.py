# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class ALCYONE2Driver. """
from __future__ import print_function, division
from ctypes import cdll
import mpi4py.MPI as mpi

import pleiades
import pleiadesMPI

from Alcyone2Init import Alcyone2Init

import c3po.medcouplingCompat as mc
from c3po.PhysicsDriver import PhysicsDriver


class ALCYONE2Driver(PhysicsDriver):
    """! This is the implementation of PhysicsDriver for Alcyone2.

    A Alcyone2Init method must be available. It has the internal Alcyone2 object as input.
    """

    def __init__(self):
        PhysicsDriver.__init__(self)
        cdll.LoadLibrary("libALCYONE.so")
        self._alcyone2 = pleiades.createComponent("AlcyoneComponent")
        pleiadesMPI.PleiadesMPIExternalSetting.getInstance().setMPIComm(mpi.COMM_SELF)
        self._dtFactor = 1.
        self._isInit = False
        self._timeShift = 0.
        self._stationaryMode = False

    def getMEDCouplingMajorVersion(self):
        return mc.MEDCouplingVersionMajMinRel()[0]

    def isMEDCoupling64Bits(self):
        return mc.MEDCouplingSizeOfIDs() == 64

    def setMPIComm(self, mpicomm):
        pleiadesMPI.PleiadesMPIExternalSetting.getInstance().setMPIComm(mpicomm)

    def initialize(self):
        if not self._isInit:
            self._isInit = True
            Alcyone2Init(self._alcyone2)
            self._alcyone2.initialize()
            pleiades.setVerboseLevel(0)
        return True

    def terminate(self):
        self._alcyone2.terminate()

    def presentTime(self):
        return self._alcyone2.presentTime() - self._timeShift

    def computeTimeStep(self):
        dt = self._alcyone2.computeTimeStep()
        return (self._dtFactor * dt, True)

    def initTimeStep(self, dt):
        if dt == 0:
            dt = 0.001  # Tres specifique a notre cas test !
        self._alcyone2.initTimeStep(dt)
        return True

    def solveTimeStep(self):
        resu = self._alcyone2.solveTimeStep()
        if not resu:
            self._dtFactor *= 0.5
        return resu

    def validateTimeStep(self):
        self._alcyone2.validateTimeStep()
        self._dtFactor = 1.

    def setStationaryMode(self, stationaryMode):
        self._stationaryMode = stationaryMode

    def getStationaryMode(self):
        return self._stationaryMode

    def abortTimeStep(self):
        self._alcyone2.abortTimeStep()

    def isStationary(self):
        return self._alcyone2.isStationary()

    def resetTime(self, time_):
        self._timeShift = self._alcyone2.presentTime() - time_

    def iterateTimeStep(self):
        return self._alcyone2.iterateTimeStep()

    def save(self, label, method):
        self._alcyone2.save(label, method)

    def restore(self, label, method):
        self._alcyone2.restore(label, method)

    def forget(self, label, method):
        self._alcyone2.forget(label, method)

    def getInputFieldsNames(self):
        fieldNames = self._alcyone2.getInputFieldsNames()
        fieldNames += ["LinearPower"]
        return fieldNames

    def getOutputFieldsNames(self):
        fieldNames = self._alcyone2.getOutputMEDField()
        fieldNames += ["Temperature_FUEL_Rowland"]
        return fieldNames

    def getInputMEDDoubleFieldTemplate(self, name):
        return self._alcyone2.getOutputMEDField("Temperature_SCE")

    def setInputMEDDoubleField(self, name, field):
        if name == "LinearPower":
            arrayZ = field.getMesh().getCoordsAt(0)
            arrayDz = mc.DataArrayDouble()
            arrayDz.alloc(arrayZ.getNbOfElems() - 1)
            for i in range(arrayZ.getNbOfElems() - 1):
                arrayDz.setIJ(i, 0, arrayZ.getIJ(i + 1, 0) - arrayZ.getIJ(i, 0))
            field.getArray().divideEqual(arrayDz)
        self._alcyone2.setInputField(name, field)

    def getOutputMEDDoubleField(self, name):
        field = 0
        if name == "Temperature_FUEL_Rowland":
            field = self._alcyone2.getOutputMEDField("Temperature_PCI")
            field2 = self._alcyone2.getOutputMEDField("Temperature_SCE")
            field *= 4. / 9.
            field2 *= 5. / 9.
            field.getArray().addEqual(field2.getArray())
        else:
            field = self._alcyone2.getOutputMEDField(name)
        field.setNature(mc.IntensiveMaximum)
        return field

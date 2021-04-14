# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class Alcyone2Driver. """
from __future__ import print_function, division
import mpi4py.MPI as mpi

import C3PO.medcoupling_compat as mc

from C3PO.PhysicsDriver import PhysicsDriver
from Alcyone2Init import Alcyone2Init

import pleiades
import pleiadesMPI

from ctypes import cdll


class Alcyone2Driver(PhysicsDriver):
    """! This is the implementation of PhysicsDriver for Alcyone2.

    A Alcyone2Init method must be available. It has the internal Alcyone2 object as input.
    """

    def __init__(self):
        PhysicsDriver.__init__(self)
        cdll.LoadLibrary("libALCYONE.so")
        self.Alcyone2_ = pleiades.createComponent("AlcyoneComponent")
        pleiadesMPI.PleiadesMPIExternalSetting.getInstance().setMPIComm(mpi.COMM_SELF)
        self.dt_factor_ = 1.
        self.isInit_ = False

    def setMPIComm(self, mpicomm):
        pleiadesMPI.PleiadesMPIExternalSetting.getInstance().setMPIComm(mpicomm)

    def initialize(self):
        if not self.isInit_:
            self.isInit_ = True
            Alcyone2Init(self.Alcyone2_)
            self.Alcyone2_.initialize()
            pleiades.setVerboseLevel(0)
        return True

    def terminate(self):
        self.Alcyone2_.terminate()

    def presentTime(self):
        return self.Alcyone2_.presentTime()

    def computeTimeStep(self):
        dt = self.Alcyone2_.computeTimeStep()
        return (self.dt_factor_ * dt, True)

    def initTimeStep(self, dt):
        if dt <= 0:
            dt = 0.001  # Tres specifique a notre cas test !
        self.Alcyone2_.initTimeStep(dt)
        return True

    def solveTimeStep(self):
        resu = self.Alcyone2_.solveTimeStep()
        if not resu:
            self.dt_factor_ *= 0.5
        return resu

    def validateTimeStep(self):
        self.Alcyone2_.validateTimeStep()
        self.dt_factor_ = 1.

    def abortTimeStep(self):
        self.Alcyone2_.abortTimeStep()

    def isStationary(self):
        return self.Alcyone2_.isStationary()

    def iterateTimeStep(self):
        return self.Alcyone2_.iterateTimeStep()

    def save(self, label, method):
        self.Alcyone2_.save(label, method)

    def restore(self, label, method):
        self.Alcyone2_.restore(label, method)

    def forget(self, label, method):
        self.Alcyone2_.forget(label, method)

    def getInputFieldsNames(self):
        fieldNames = self.Alcyone2_.getInputFieldsNames()
        fieldNames + ["LinearPower"]
        return fieldNames

    def getInputMEDFieldTemplate(self, name):
        return self.Alcyone2_.getOutputMEDField("Temperature_SCE")

    def setInputMEDField(self, name, field):
        if name == "LinearPower":
            ArrayZ = field.getMesh().getCoordsAt(0)
            ArrayDz = mc.DataArrayDouble()
            ArrayDz.alloc(ArrayZ.getNbOfElems() - 1)
            for i in range(ArrayZ.getNbOfElems() - 1):
                ArrayDz.setIJ(i, 0, ArrayZ.getIJ(i + 1, 0) - ArrayZ.getIJ(i, 0))
            field.getArray().divideEqual(ArrayDz)
        self.Alcyone2_.setInputField(name, field)

    def getOutputFieldsNames(self):
        fieldNames = self.Alcyone2_.getOutputMEDField()
        fieldNames + ["Temperature_FUEL_Rowland"]
        return fieldNames

    def getOutputMEDField(self, name):
        field = 0
        if name == "Temperature_FUEL_Rowland":
            field = self.Alcyone2_.getOutputMEDField("Temperature_PCI")
            field2 = self.Alcyone2_.getOutputMEDField("Temperature_SCE")
            field *= 4. / 9.
            field2 *= 5. / 9.
            field.getArray().addEqual(field2.getArray())
        else:
            field = self.Alcyone2_.getOutputMEDField(name)
        field.setNature(mc.IntensiveMaximum)
        return field

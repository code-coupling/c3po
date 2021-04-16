# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class FLICA4Driver. """
from __future__ import print_function, division
import os
import sys
import glob
import shutil
import subprocess

import FlicaICoCo
import MEDCoupling

from C3PO.PhysicsDriver import PhysicsDriver


class FLICA4Driver(PhysicsDriver):
    """! This is the implementation of PhysicsDriver for FLICA4. """

    def __init__(self):
        """! Build a FLICA4Driver object. """
        PhysicsDriver.__init__(self)
        self.isInit_ = False
        self.isStationnary_ = False
        self.permSteps_ = 1000
        self.flica_, self.handle_ = FlicaICoCo.openLib(str(os.path.join(os.getenv("FLICA_SHARED_LIB"), "libflica4.so")))
       # self.flica_.setDataFile(os.path.join(os.getenv("DATADIR"), "flica4_static.dat"))

    def __del__(self):
        FlicaICoCo.closeLib(self.handle_)

    def setDataFile(self, datafile):
        self.flica_.setDataFile(datafile)

    def initialize(self):
        if not self.isInit_:
            self.isInit_ = True
            return self.flica_.initialize()
        else:
            return True

    def terminate(self):
        self.isInit_ = False
        self.flica_.terminate()
        return True

    def presentTime(self):
        return self.flica_.presentTime()

    def computeTimeStep(self):
        return self.flica_.computeTimeStep()

    def initTimeStep(self, dt):
        if dt < 0.:
            self.isStationnary_ = True
            return True
        else:
            return self.flica_.initTimeStep(dt)

    def solveTimeStep(self):
        if self.isStationnary_:
            return self.flica_.solveSteadyState(self.permSteps_)
        else:
            return self.flica_.solveTimeStep()

    def validateTimeStep(self):
        if not self.isStationnary_:
            self.flica_.validateTimeStep()

    def abortTimeStep(self):
        self.flica_.abortTimeStep()

    def getInputFieldsNames(self):
        return self.flica_.getInputFieldsNames()

    def getInputMEDFieldTemplate(self, name):
        if name == "FuelPower":
            return self.getOutputMEDField("FuelDopplerTemperature")
        else:
            return self.getOutputMEDField("LiquidTemperature")

    def getOutputFieldsNames(self):
        return self.flica_.getOutputFieldsNames()

    def setInputMEDField(self, name, field):
        self.flica_.setInputMEDField(name, field)

    def getOutputMEDField(self, name):
        field = self.flica_.getOutputMEDField(name)
        field.setNature(MEDCoupling.ConservativeVolumic)
        return field

    def setValue(self, name, value):
        if(name == "nbIterMaxSteadyState"):
            self.permSteps_ = value
        else:
            self.flica_.setValue(name, value)

    def getValue(self, name):
        return self.flica_.getValue(name)

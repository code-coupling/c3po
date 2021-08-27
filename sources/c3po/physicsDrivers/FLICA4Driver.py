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

import FlicaICoCo

import c3po.medcouplingCompat as mc
from c3po.PhysicsDriver import PhysicsDriver


class FLICA4Driver(PhysicsDriver):
    """! This is the implementation of PhysicsDriver for FLICA4. """

    def __init__(self):
        """! Build a FLICA4Driver object. """
        PhysicsDriver.__init__(self)
        self._isInit = False
        self._permSteps = 1000
        self._flica4, self._handle = FlicaICoCo.openLib(str(os.path.join(os.getenv("FLICA_SHARED_LIB"), "libflica4.so")))
       # self._flica4.setDataFile(os.path.join(os.getenv("DATADIR"), "flica4_static.dat"))
        self._timeShift = 0.
        self._stationaryMode = False

    def getICOCOVersion(self):
        return '2.0'

    def getMEDCouplingMajorVersion(self):
        return mc.MEDCouplingVersionMajMinRel()[0]

    def isMEDCoupling64Bits(self):
        return mc.MEDCouplingSizeOfIDs() == 64

    def __del__(self):
        FlicaICoCo.closeLib(self._handle)

    def setDataFile(self, datafile):
        self._flica4.setDataFile(datafile)

    def initialize(self):
        if not self._isInit:
            self._isInit = True
            return self._flica4.initialize()
        return True

    def terminate(self):
        self._isInit = False
        self._flica4.terminate()

    def presentTime(self):
        return self._flica4.presentTime() - self._timeShift

    def computeTimeStep(self):
        return self._flica4.computeTimeStep()

    def initTimeStep(self, dt):
        if self._stationaryMode:
            return True
        return self._flica4.initTimeStep(dt)

    def solveTimeStep(self):
        if self._stationaryMode:
            return self._flica4.solveSteadyState(self._permSteps)
        return self._flica4.solveTimeStep()

    def validateTimeStep(self):
        if not self._stationaryMode:
            self._flica4.validateTimeStep()

    def setStationaryMode(self, stationaryMode):
        self._stationaryMode = stationaryMode

    def getStationaryMode(self):
        return self._stationaryMode

    def abortTimeStep(self):
        self._flica4.abortTimeStep()

    def resetTime(self, time_):
        self._timeShift = self._flica4.presentTime() - time_

    def getInputFieldsNames(self):
        return self._flica4.getInputFieldsNames()

    def getOutputFieldsNames(self):
        return self._flica4.getOutputFieldsNames()

    def getInputMEDDoubleFieldTemplate(self, name):
        if name == "FuelPower":
            return self.getOutputMEDField("FuelDopplerTemperature")
        return self.getOutputMEDField("LiquidTemperature")

    def setInputMEDDoubleField(self, name, field):
        self._flica4.setInputMEDField(name, field)

    def getOutputMEDDoubleField(self, name):
        field = self._flica4.getOutputMEDField(name)
        field.setNature(mc.IntensiveMaximum)
        return field

    def setInputDoubleValue(self, name, value):
        self._flica4.setValue(name, value)

    def setInputIntValue(self, name,  value):
        if name == "nbIterMaxSteadyState":
            self._permSteps = value
        else:
            raise Exception("FLICA4Driver.setInputIntValue : unknown scalar "+ name + ".")

    def getOutputDoubleValue(self, name):
        return self._flica4.getValue(name)


class FLICA4AutoSwitchDriver(PhysicsDriver):
    """! This PhysicsDriver drives two FLICA4Driver, for stationnary and transient,
    and switches from one to the other automatically.
    """

    dataFileStationnary = os.path.join(os.getenv("DATADIR"), "flica4_static.dat")
    dataFileTransient = os.path.join(os.getenv("DATADIR"), "flica4_transient.dat")

    def __init__(self):
        PhysicsDriver.__init__(self)
        self._flica4Steady = FLICA4Driver()
        self._flica4Transient = FLICA4Driver()
        self._flica4Current = self._flica4Steady
        self._isStationnary = True
        self._stationaryMode = False
        self._isInit = False
        self._timeShift = 0.

    def getICOCOVersion(self):
        return self._flica4Current.getICOCOVersion()

    def getMEDCouplingMajorVersion(self):
        return self._flica4Current.getMEDCouplingMajorVersion()

    def isMEDCoupling64Bits(self):
        return self._flica4Current.isMEDCoupling64Bits()

    def initialize(self):
        if self._isStationnary:
            if self._isInit:
                return True
            self._isInit = True
            self._flica4Steady.setDataFile(FLICA4AutoSwitchDriver.dataFileStationnary)
            return self._flica4Steady.initialize()
        raise Exception("FLICA4AutoSwitchDriver.initialize : only available with stationary FLICA4Driver.")

    def terminate(self):
        self._flica4Current.terminate()

    def presentTime(self):
        return self._flica4Current.presentTime() - self._timeShift

    def computeTimeStep(self):
        return self._flica4Current.computeTimeStep()

    def initTimeStep(self, dt):
        if self._stationaryMode:
            if self._isStationnary:
                return self._flica4Current.initTimeStep(dt)
            self._isStationnary = True
            time_ = self._flica4Current.presentTime()
            self._flica4Transient.terminate()
            self._flica4Transient = FLICA4Driver()
            if not self._isInit:
                self._isInit = True
                self._flica4Steady.setDataFile(FLICA4AutoSwitchDriver.dataFileStationnary)
                self._flica4Steady.initialize()
            self._flica4Current = self._flica4Steady
            self._timeShift = self._flica4Current.presentTime() - time_
            return self._flica4Current.initTimeStep(dt)
        if self._isStationnary:
            self._isStationnary = False
            time_ = self._flica4Current.presentTime()
            self._flica4Steady.terminate()
            self._flica4Steady = FLICA4Driver()
            self._isInit = False
            self._flica4Transient.setDataFile(FLICA4AutoSwitchDriver.dataFileTransient)
            self._flica4Transient.initialize()
            self._flica4Current = self._flica4Transient
            self._timeShift = self._flica4Current.presentTime() - time_
            return self._flica4Current.initTimeStep(dt)
        return self._flica4Current.initTimeStep(dt)

    def solveTimeStep(self):
        return self._flica4Current.solveTimeStep()

    def validateTimeStep(self):
        self._flica4Current.validateTimeStep()

    def setStationaryMode(self, stationaryMode):
        self._stationaryMode = stationaryMode

    def getStationaryMode(self):
        return self._stationaryMode

    def abortTimeStep(self):
        self._flica4Current.abortTimeStep()

    def resetTime(self, time_):
        self._timeShift = self._flica4Current.presentTime() - time_

    def getInputFieldsNames(self):
        return self._flica4Current.getInputFieldsNames()

    def getOutputFieldsNames(self):
        return self._flica4Current.getOutputFieldsNames()

    def getInputMEDDoubleFieldTemplate(self, name):
        return self._flica4Current.getInputMEDDoubleFieldTemplate(name)

    def setInputMEDDoubleField(self, name, field):
        self._flica4Current.setInputMEDDoubleField(name, field)

    def getOutputMEDDoubleField(self, name):
        return self._flica4Current.getOutputMEDDoubleField(name)

    def setInputDoubleValue(self, name, value):
        self._flica4Current.setInputDoubleValue(name, value)

    def setInputIntValue(self, name, value):
        self._flica4Current.setInputIntValue(name, value)

    def getOutputDoubleValue(self, name):
        return self._flica4Current.getOutputDoubleValue(name)

# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class THEDIDriver. """
from __future__ import print_function, division

from c3po.PhysicsDriver import PhysicsDriver


class THEDIDriver(PhysicsDriver):
    """! This is the implementation of PhysicsDriver for THEDI. """

    def __init__(self, thediICoCo):
        """! Build a THEDIDriver object.

        @param thediICoCo implementation of the ICOCO interface for THEDI.
        """
        PhysicsDriver.__init__(self)
        if thediICoCo.GetICoCoMajorVersion() != self.GetICoCoMajorVersion():
            raise AssertionError("The ICoCo major version of the provided object ({}) is not the expected one ({})".format(thediICoCo.GetICoCoMajorVersion(), self.GetICoCoMajorVersion()))
        self._thedi = thediICoCo
        self._isInit = False

    def getMEDCouplingMajorVersion(self):
        return self._thedi.getMEDCouplingMajorVersion()

    def isMEDCoupling64Bits(self):
        return self._thedi.isMEDCoupling64Bits()

    def initialize(self):
        if not self._isInit:
            self._isInit = True
            return self._thedi.initialize()
        return True

    def terminate(self):
        self._isInit = False
        self._thedi.terminate()

    def presentTime(self):
        return self._thedi.presentTime()

    def computeTimeStep(self):
        return self._thedi.computeTimeStep()

    def initTimeStep(self, dt):
        return self._thedi.initTimeStep(dt)

    def solveTimeStep(self):
        return self._thedi.solveTimeStep()

    def validateTimeStep(self):
        self._thedi.validateTimeStep()

    def setStationaryMode(self, stationaryMode):
        self._thedi.setStationaryMode(stationaryMode)

    def getStationaryMode(self):
        return self._thedi.getStationaryMode()

    def isStationary(self):
        return self._thedi.isStationary()

    def abortTimeStep(self):
        self._thedi.abortTimeStep()

    def resetTime(self, time_):
        self._thedi.resetTime(time_)

    def iterateTimeStep(self):
        return self._thedi.iterateTimeStep()

    def save(self, label, method):
        self._thedi.save(label, method)

    def restore(self, label, method):
        self._thedi.restore(label, method)

    def forget(self, label, method):
        self._thedi.forget(label, method)

    def getInputFieldsNames(self):
        return self._thedi.getInputFieldsNames()

    def getOutputFieldsNames(self):
        return self._thedi.getOutputFieldsNames()

    def getFieldType(self, name):
        return self._thedi.getFieldType(name)

    def getMeshUnit(self):
        return self._thedi.getMeshUnit()

    def getFieldUnit(self, name):
        return self._thedi.getFieldUnit(name)

    def getInputMEDDoubleFieldTemplate(self, name):
        return self._thedi.getInputMEDDoubleFieldTemplate(name)

    def setInputMEDDoubleField(self, name, field):
        self._thedi.setInputMEDDoubleField(name, field)

    def getOutputMEDDoubleField(self, name):
        return self._thedi.getOutputMEDDoubleField(name)

    def updateOutputMEDDoubleField(self, name, field):
        self._thedi.updateOutputMEDDoubleField(name, field)

    def getInputValuesNames(self):
        return self._thedi.getInputValuesNames()

    def getOutputValuesNames(self):
        return self._thedi.getOutputValuesNames()

    def getValueType(self, name):
        return self._thedi.getValueType(name)

    def getValueUnit(self, name):
        return self._thedi.getValueUnit(name)

    def setInputDoubleValue(self, name, value):
        self._thedi.setInputDoubleValue(name, value)

    def getOutputDoubleValue(self, name):
        return self._thedi.getOutputDoubleValue(name)

    def setInputIntValue(self, name, value):
        self._thedi.setInputIntValue(name, value)

    def getOutputIntValue(self, name):
        return self._thedi.getOutputIntValue(name)

    def setInputStringValue(self, name, value):
        self._thedi.setInputStringValue(name, value)

    def getOutputStringValue(self, name):
        return self._thedi.getOutputStringValue(name)

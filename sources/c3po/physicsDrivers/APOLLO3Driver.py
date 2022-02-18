# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class APOLLO3Driver. """
from __future__ import print_function, division

from c3po.PhysicsDriver import PhysicsDriver


class APOLLO3Driver(PhysicsDriver):
    """! This is the implementation of PhysicsDriver for APOLLO3. """

    def __init__(self, apollo3ICoCo):
        """! Build a APOLLO3Driver object.

        @param apollo3ICoCo implementation of the ICOCO interface for APOLLO3.
        """
        PhysicsDriver.__init__(self)
        if apollo3ICoCo.GetICoCoMajorVersion() != self.getICoCoMajorVersion():
            raise AssertionError("The ICoCo major version of the provided object ({}) is not the expected one ({})".format(apollo3ICoCo.GetICoCoMajorVersion(), self.getICoCoMajorVersion()))
        self._apollo3 = apollo3ICoCo

    def getMEDCouplingMajorVersion(self):
        return self._apollo3.getMEDCouplingMajorVersion()

    def isMEDCoupling64Bits(self):
        return self._apollo3.isMEDCoupling64Bits()

    def setDataFile(self, datafile):
        self._apollo3.setDataFile(datafile)

    def initialize(self):
        return self._apollo3.initialize()

    def terminate(self):
        self._apollo3.terminate()

    def presentTime(self):
        return self._apollo3.presentTime()

    def computeTimeStep(self):
        return self._apollo3.computeTimeStep()

    def initTimeStep(self, dt):
        return self._apollo3.initTimeStep(dt)

    def solveTimeStep(self):
        return self._apollo3.solveTimeStep()

    def validateTimeStep(self):
        self._apollo3.validateTimeStep()

    def setStationaryMode(self, stationaryMode):
        self._apollo3.setStationaryMode(stationaryMode)

    def getStationaryMode(self):
        return self._apollo3.getStationaryMode()

    def isStationary(self):
        return self._apollo3.isStationary()

    def abortTimeStep(self):
        self._apollo3.abortTimeStep()

    def resetTime(self, time_):
        self._apollo3.resetTime(time_)

    def iterateTimeStep(self):
        return self._apollo3.iterateTimeStep()

    def save(self, label, method):
        self._apollo3.save(label, method)

    def restore(self, label, method):
        self._apollo3.restore(label, method)

    def forget(self, label, method):
        self._apollo3.forget(label, method)

    def getInputFieldsNames(self):
        return self._apollo3.getInputFieldsNames()

    def getOutputFieldsNames(self):
        return self._apollo3.getOutputFieldsNames()

    def getFieldType(self, name):
        return self._apollo3.getFieldType(name)

    def getMeshUnit(self):
        return self._apollo3.getMeshUnit()

    def getFieldUnit(self, name):
        return self._apollo3.getFieldUnit(name)

    def getInputMEDDoubleFieldTemplate(self, name):
        return self._apollo3.getInputMEDDoubleFieldTemplate(name)

    def setInputMEDDoubleField(self, name, field):
        self._apollo3.setInputMEDDoubleField(name, field)

    def getOutputMEDDoubleField(self, name):
        return self._apollo3.getOutputMEDDoubleField(name)

    def updateOutputMEDDoubleField(self, name, field):
        self._apollo3.updateOutputMEDDoubleField(name, field)

    def getInputValuesNames(self):
        return self._apollo3.getInputValuesNames()

    def getOutputValuesNames(self):
        return self._apollo3.getOutputValuesNames()

    def getValueType(self, name):
        return self._apollo3.getValueType(name)

    def getValueUnit(self, name):
        return self._apollo3.getValueUnit(name)

    def setInputDoubleValue(self, name, value):
        self._apollo3.setInputDoubleValue(name, value)

    def getOutputDoubleValue(self, name):
        return self._apollo3.getOutputDoubleValue(name)

    def setInputIntValue(self, name, value):
        self._apollo3.setInputIntValue(name, value)

    def getOutputIntValue(self, name):
        return self._apollo3.getOutputIntValue(name)

    def setInputStringValue(self, name, value):
        self._apollo3.setInputStringValue(name, value)

    def getOutputStringValue(self, name):
        return self._apollo3.getOutputStringValue(name)

# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class ICOCODriver. """
from __future__ import print_function, division

from c3po.PhysicsDriver import PhysicsDriver


class ICOCODriver(PhysicsDriver):
    """! This is the implementation of PhysicsDriver for any ICoCo Problem implementation. """

    def __init__(self, problem):
        """! Build a ICOCODriver object.

        @param problem Implementation of the ICoCo Problem.
        """
        PhysicsDriver.__init__(self)
        if problem.GetICoCoMajorVersion() != self.GetICoCoMajorVersion():
            raise AssertionError("The ICoCo major version of the provided object ({}) is not the expected one ({})".format(problem.GetICoCoMajorVersion(), self.GetICoCoMajorVersion()))
        self._problem = problem

    def getMEDCouplingMajorVersion(self):
        return self._problem.getMEDCouplingMajorVersion()

    def isMEDCoupling64Bits(self):
        return self._problem.isMEDCoupling64Bits()

    def setDataFile(self, datafile):
        self._problem.setDataFile(datafile)

    def initialize(self):
        return self._problem.initialize()

    def terminate(self):
        self._problem.terminate()

    def presentTime(self):
        return self._problem.presentTime()

    def computeTimeStep(self):
        return self._problem.computeTimeStep()

    def initTimeStep(self, dt):
        return self._problem.initTimeStep(dt)

    def solveTimeStep(self):
        return self._problem.solveTimeStep()

    def validateTimeStep(self):
        self._problem.validateTimeStep()

    def setStationaryMode(self, stationaryMode):
        self._problem.setStationaryMode(stationaryMode)

    def getStationaryMode(self):
        return self._problem.getStationaryMode()

    def isStationary(self):
        return self._problem.isStationary()

    def abortTimeStep(self):
        self._problem.abortTimeStep()

    def resetTime(self, time_):
        self._problem.resetTime(time_)

    def iterateTimeStep(self):
        return self._problem.iterateTimeStep()

    def save(self, label, method):
        self._problem.save(label, method)

    def restore(self, label, method):
        self._problem.restore(label, method)

    def forget(self, label, method):
        self._problem.forget(label, method)

    def getInputFieldsNames(self):
        return self._problem.getInputFieldsNames()

    def getOutputFieldsNames(self):
        return self._problem.getOutputFieldsNames()

    def getFieldType(self, name):
        return self._problem.getFieldType(name)

    def getMeshUnit(self):
        return self._problem.getMeshUnit()

    def getFieldUnit(self, name):
        return self._problem.getFieldUnit(name)

    def getInputMEDDoubleFieldTemplate(self, name):
        return self._problem.getInputMEDDoubleFieldTemplate(name)

    def setInputMEDDoubleField(self, name, field):
        self._problem.setInputMEDDoubleField(name, field)

    def getOutputMEDDoubleField(self, name):
        return self._problem.getOutputMEDDoubleField(name)

    def updateOutputMEDDoubleField(self, name, field):
        self._problem.updateOutputMEDDoubleField(name, field)

    def getInputValuesNames(self):
        return self._problem.getInputValuesNames()

    def getOutputValuesNames(self):
        return self._problem.getOutputValuesNames()

    def getValueType(self, name):
        return self._problem.getValueType(name)

    def getValueUnit(self, name):
        return self._problem.getValueUnit(name)

    def setInputDoubleValue(self, name, value):
        self._problem.setInputDoubleValue(name, value)

    def getOutputDoubleValue(self, name):
        return self._problem.getOutputDoubleValue(name)

    def setInputIntValue(self, name, value):
        self._problem.setInputIntValue(name, value)

    def getOutputIntValue(self, name):
        return self._problem.getOutputIntValue(name)

    def setInputStringValue(self, name, value):
        self._problem.setInputStringValue(name, value)

    def getOutputStringValue(self, name):
        return self._problem.getOutputStringValue(name)

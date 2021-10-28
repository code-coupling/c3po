# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class TimeAccumulator. """
from __future__ import print_function, division

from c3po.PhysicsDriver import PhysicsDriver


class TimeAccumulator(PhysicsDriver):
    """! TimeAccumulator wraps a PhysicsDriver into a macro time step procedure (for transients or stationaries (through stabilized transients)).

    In transient calculations, the TimeAccumulator object is driven like any PhysicsDriver, but it will use macro time steps (chosen with
    setValue("macrodt", dt)) whereas the wraped PhysicsDriver may use smaller internal time steps (given by computeTimeStep()).

    In stationary calculations, if the stabilizedTransient mode is activated, when a steady state is asked to the TimeAccumulator object
    (initTimeStep(0) in stationaryMode), a time loop over the wraped PhysicsDriver object is run until steady state is reached (isStationary() return True).
    If the stabilizedTransient mode is not activated, steady state calculations (initTimeStep(0) in stationaryMode) are directly asked to the wraped PhysicsDriver.
    """

    def __init__(self, physics, saveParameters=None, stabilizedTransient=(False, 100.)):
        """! Build a TimeAccumulator object.

        @param physics the PhysicsDriver to wrap.
        @param saveParameters the tuple (label, method) that can be used to save / restore results in order to provide abortTimeStep capabilities in transient with macro time steps. It also used (but not required) in steady states (dt = 0) if the stabilizedTransient mode is activated.
        @param stabilizedTransient a tuple (activated, tMax). If activated is set to True, it computes steady states (dt = 0) as stabilized transients (until physics.isStationary() returns True or the current time reaches tInit + tMax) and then uses resetTime(tInit) in order to keep time consistency (tInit is the returned value of physics.presentTime() before solving). If activated is set to False (default value), steady states (dt = 0) are directly asked to physics.
        """
        PhysicsDriver.__init__(self)
        self._physics = physics
        self._dt = None
        self._macrodt = None
        self._saveParameters = saveParameters
        self._stabilizedTransient = stabilizedTransient

    def getMEDCouplingMajorVersion(self):
        """! See PhysicsDriver.getMEDCouplingMajorVersion(). """
        return self._physics.getMEDCouplingMajorVersion()

    def isMEDCoupling64Bits(self):
        """! See PhysicsDriver.isMEDCoupling64Bits(). """
        return self._physics.isMEDCoupling64Bits()

    def setDataFile(self, datafile):
        """! See PhysicsDriver.setDataFile(). """
        self._physics.setDataFile(datafile)

    def setMPIComm(self, mpicomm):
        """! See PhysicsDriver.setMPIComm(). """
        self._physics.setMPIComm(mpicomm)

    def initialize(self):
        """! See PhysicsDriver.initialize(). """
        self._physics.init()
        return self._physics.getInitStatus()

    def terminate(self):
        """! See PhysicsDriver.terminate(). """
        if self._saveParameters is not None:
            self._physics.forget(*self._saveParameters)
        self._physics.terminate()

    def presentTime(self):
        """! See PhysicsDriver.presentTime(). """
        return self._physics.presentTime()

    def computeTimeStep(self):
        """! See PhysicsDriver.computeTimeStep().

        Return the asked macro time step if set (by setValue("macrodt", dt)), the prefered time step of the PhysicsDriver otherwise.
        """
        (dtPhysics, stop) = self._physics.computeTimeStep()
        if self._macrodt is not None:
            dtPhysics = self._macrodt
        return (dtPhysics, stop)

    def initTimeStep(self, dt):
        """! See PhysicsDriver.initTimeStep(). """
        self._dt = dt
        if self._dt <= 0 and not self._stabilizedTransient[0]:
            return self._physics.initTimeStep(dt)
        if self._dt == 0 and self._stabilizedTransient[0] and not self._physics.getStationaryMode():
            raise AssertionError("TimeAccumulator.initTimeStep : Stationary mode must be activated (setStationaryMode(True)) in order to use a stabilized transient to reach a steady state solution.")
        if self._saveParameters is not None and ((self._dt > 0 and self._macrodt is not None) or (self._dt == 0 and self._stabilizedTransient[0])):
            self._physics.save(*self._saveParameters)
        return True

    def solveTimeStep(self):
        """! Make the PhysicsDriver to reach the end of the macro time step asked to TimeAccumulator
        using its own time advance procedure.
        """
        if self._dt > 0.:
            self._physics.solveTransient(self.presentTime() + self._dt, finishAtTmax=True)
        elif self._stabilizedTransient[0]:
            timeInit = self.presentTime()
            self._physics.solveTransient(timeInit + self._stabilizedTransient[1], stopIfStationary=True)
            self._physics.resetTime(timeInit)
            return self._physics.isStationary()
        else:
            self._physics.solve()
        return self._physics.getSolveStatus()

    def validateTimeStep(self):
        """! See PhysicsDriver.validateTimeStep(). """
        if self._dt <= 0 and not self._stabilizedTransient[0]:
            self._physics.validateTimeStep()
        self._dt = None

    def setStationaryMode(self, stationaryMode):
        """! See PhysicsDriver.setStationaryMode(). """
        self._physics.setStationaryMode(stationaryMode)

    def getStationaryMode(self):
        """! See PhysicsDriver.getStationaryMode(). """
        return self._physics.getStationaryMode()

    def abortTimeStep(self):
        """! See PhysicsDriver.abortTimeStep(). """
        if (self._dt > 0 and self._macrodt is not None) or (self._dt == 0 and self._stabilizedTransient[0]):
            if self._saveParameters is not None:
                self._physics.restore(*self._saveParameters)
            elif self._dt > 0:
                raise Exception("TimeAccumulator.abortTimeStep : not available without saveParameters.")
        elif self._dt == 0:
            self._physics.abortTimeStep()
        self._dt = None

    def isStationary(self):
        """! See PhysicsDriver.isStationary(). """
        return self._physics.isStationary()

    def resetTime(self, time_):
        """! See PhysicsDriver.resetTime(). """
        self._physics.resetTime(time_)

    def getInputFieldsNames(self):
        """! See c3po.DataAccessor.DataAccessor.getInputFieldsNames(). """
        return self._physics.getInputFieldsNames()

    def getOutputFieldsNames(self):
        """! See c3po.DataAccessor.DataAccessor.getOutputFieldsNames(). """
        return self._physics.getOutputFieldsNames()

    def getFieldType(self, name):
        """! See c3po.DataAccessor.DataAccessor.getFieldType(). """
        return self._physics.getFieldType(name)

    def getMeshUnit(self):
        """! See c3po.DataAccessor.DataAccessor.getMeshUnit(). """
        return self._physics.getMeshUnit()

    def getFieldUnit(self, name):
        """! See c3po.DataAccessor.DataAccessor.getFieldUnit(). """
        return self._physics.getFieldUnit(name)

    def getInputMEDDoubleFieldTemplate(self, name):
        """! See c3po.DataAccessor.DataAccessor.getInputMEDDoubleFieldTemplate(). """
        return self._physics.getInputMEDDoubleFieldTemplate(name)

    def setInputMEDDoubleField(self, name, field):
        """! See c3po.DataAccessor.DataAccessor.setInputMEDDoubleField(). """
        self._physics.setInputMEDDoubleField(name, field)

    def getOutputMEDDoubleField(self, name):
        """! See c3po.DataAccessor.DataAccessor.getOutputMEDDoubleField(). """
        return self._physics.getOutputMEDDoubleField(name)

    def updateOutputMEDDoubleField(self, name, field):
        """! See c3po.DataAccessor.DataAccessor.updateOutputMEDDoubleField(). """
        return self._physics.updateOutputMEDDoubleField(name, field)

    def getInputMEDIntFieldTemplate(self, name):
        """! See c3po.DataAccessor.DataAccessor.getInputMEDIntFieldTemplate(). """
        return self._physics.getInputMEDIntFieldTemplate(name)

    def setInputMEDIntField(self, name, field):
        """! See c3po.DataAccessor.DataAccessor.setInputMEDIntField(). """
        self._physics.setInputMEDIntField(name, field)

    def getOutputMEDIntField(self, name):
        """! See c3po.DataAccessor.DataAccessor.getOutputMEDIntField(). """
        return self._physics.getOutputMEDIntField(name)

    def updateOutputMEDIntField(self, name, field):
        """! See c3po.DataAccessor.DataAccessor.updateOutputMEDIntField(). """
        return self._physics.updateOutputMEDIntField(name, field)

    def getInputValuesNames(self):
        """! See c3po.DataAccessor.DataAccessor.getInputValuesNames(). """
        return self._physics.getInputValuesNames() + ["macrodt"]

    def getOutputValuesNames(self):
        """! See c3po.DataAccessor.DataAccessor.getOutputValuesNames(). """
        return self._physics.getOutputValuesNames()

    def getValueType(self, name):
        """! See c3po.DataAccessor.DataAccessor.getValueType(). """
        return self._physics.getValueType(name)

    def getValueUnit(self, name):
        """! See c3po.DataAccessor.DataAccessor.getValueUnit(). """
        return self._physics.getValueUnit(name)

    def setInputDoubleValue(self, name, value):
        """! See c3po.DataAccessor.DataAccessor.setInputDoubleValue().

        The macro time step used by the object can be modified here, using name="macrodt".
        """
        if name == "macrodt":
            self._macrodt = value
        else:
            self._physics.setInputDoubleValue(name, value)

    def getOutputDoubleValue(self, name):
        """! See c3po.DataAccessor.DataAccessor.getOutputDoubleValue(). """
        return self._physics.getOutputDoubleValue(name)

    def setInputIntValue(self, name, value):
        """! See c3po.DataAccessor.DataAccessor.setInputIntValue(). """
        self._physics.setInputIntValue(name, value)

    def getOutputIntValue(self, name):
        """! See c3po.DataAccessor.DataAccessor.getOutputIntValue(). """
        return self._physics.getOutputIntValue(name)

    def setInputStringValue(self, name, value):
        """! See c3po.DataAccessor.DataAccessor.setInputStringValue(). """
        self._physics.setInputStringValue(name, value)

    def getOutputStringValue(self, name):
        """! See c3po.DataAccessor.DataAccessor.getOutputStringValue(). """
        return self._physics.getOutputStringValue(name)

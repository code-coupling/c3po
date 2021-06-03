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
    """! TimeAccumulator wraps a PhysicsDriver in order to allow it to use multiple
    internal time steps for each "macro" time step asked to TimeAccumulator.
    """

    def __init__(self, physics, saveParameters=None):
        """! Build a TimeAccumulator object.

        @param physics the PhysicsDriver to deal with.
        @param saveParameters the tuple (label, method) that can be used to save / restore results in order to provide abortTimeStep capabilities.
        """
        PhysicsDriver.__init__(self)
        self._physics = physics
        self._dt = 0
        self._macrodt = None
        self._saveParameters = saveParameters

    def setDataFile(self, datafile):
        """! See PhysicsDriver.setDataFile(). """
        self._physics.setDataFile(datafile)

    def setMPIComm(self, mpicomm):
        """! See PhysicsDriver.setMPIComm(). """
        self._physics.setMPIComm(mpicomm)

    def initialize(self):
        """! See PhysicsDriver.initialize(). """
        result = self._physics.initialize()
        if saveParameters is not None:
            self._physics.save(*self._saveParameters)
        return result

    def terminate(self):
        """! See PhysicsDriver.terminate(). """
        if saveParameters is not None:
            self._physics.forget(*self._saveParameters)
        self._physics.terminate()

    def presentTime(self):
        """! See PhysicsDriver.presentTime(). """
        return self._physics.presentTime()

    def computeTimeStep(self):
        """! See PhysicsDriver.computeTimeStep().

        Return the asked macro time step if set, the prefered time step of the PhysicsDriver otherwise.
        """
        (dtPhysics, stop) = self._physics.computeTimeStep()
        if self._macrodt is not None:
            dtPhysics = self._macrodt
        return (dtPhysics, stop)

    def initTimeStep(self, dt):
        """! See PhysicsDriver.initTimeStep(). """
        self._dt = dt
        return True

    def solveTimeStep(self):
        """! Make the PhysicsDriver to reach the end of the macro time step asked to TimeAccumulator
        using its own time advance procedure.
        """
        self._physics.solveTransient(self.presentTime() + self._dt, finishAtTmax=True)
        return self.getSolveStatus()

    def validateTimeStep(self):
        """! See PhysicsDriver.validateTimeStep(). """
        self._dt = 0
        if saveParameters is not None and self._macrodt is not None:
            self._physics.save(*self._saveParameters)

    def abortTimeStep(self):
        """! See PhysicsDriver.abortTimeStep(). """
        self._dt = 0
        if self._macrodt is not None:
            if saveParameters is not None:
                self._physics.restore(*self._saveParameters)
            else:
                raise Exception("TimeAccumulator.abortTimeStep : not available without saveParameters.")

    def isStationary(self):
        """! See PhysicsDriver.isStationary(). """
        return self._physics.isStationary()

    def getInputFieldsNames(self):
        """! See PhysicsDriver.getInputFieldsNames(). """
        return self._physics.getInputFieldsNames()

    def getOutputFieldsNames(self):
        """! See PhysicsDriver.getOutputFieldsNames(). """
        return self._physics.getOutputFieldsNames()

    def getInputValuesNames(self):
        """! See PhysicsDriver.getInputValuesNames(). """
        return self._physics.getInputValuesNames() + ["macrodt"]

    def getOutputValuesNames(self):
        """! See PhysicsDriver.getOutputValuesNames(). """
        return self._physics.getOutputValuesNames()

    def getInputMEDFieldTemplate(self, name):
        """! See DataAccessor.getInputMEDFieldTemplate(). """
        return self._physics.getInputMEDFieldTemplate(name)

    def setInputMEDField(self, name, field):
        """! See DataAccessor.setInputMEDField(). """
        self._physics.setInputMEDField(name, field)

    def getOutputMEDField(self, name):
        """! See DataAccessor.getOutputMEDField(). """
        return self._physics.getOutputMEDField(name)

    def setValue(self, name, value):
        """! See DataAccessor.setValue().

        The macro time step used by the object can be modified here, using name="macrodt".
        """
        if name == "macrodt":
            self._macrodt = value
        else:
            self._physics.setValue(name, value)

    def getValue(self, name):
        """! See DataAccessor.getValue(). """
        return self._physics.getValue(name)

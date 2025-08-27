# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the wrapper class :class:`.PhysicsDriverWrapper`. """
from __future__ import print_function, division

from c3po.PhysicsDriver import PhysicsDriver


class PhysicsDriverWrapper(PhysicsDriver):
    """ :class:`.PhysicsDriverWrapper` wraps a :class:`.PhysicsDriver` object without modifying its behavior.

    This class is a skeleton, intended to be overloaded, for modifying the behavior of a :class:`.PhysicsDriver` by composition.
    """

    def __init__(self, physics):
        """ Build a :class:`.PhysicsDriverWrapper` object.

        Parameters
        ----------
        physics : PhysicsDriver
            The :class:`.PhysicsDriver` to wrap.
        """
        PhysicsDriver.__init__(self)
        self._physics = physics

    def getPhysicsDriver(self):
        """ Return the wrapped :class:`.PhysicsDriver`.

        Returns
        -------
        PhysicsDriver
            the wrapped PhysicsDriver.
        """
        return self._physics

    def getMEDCouplingMajorVersion(self):
        """ See :meth:`.PhysicsDriver.getMEDCouplingMajorVersion`. """
        return self._physics.getMEDCouplingMajorVersion()

    def isMEDCoupling64Bits(self):
        """ See :meth:`.PhysicsDriver.isMEDCoupling64Bits`. """
        return self._physics.isMEDCoupling64Bits()

    def setDataFile(self, datafile):
        """ See :meth:`.PhysicsDriver.setDataFile`. """
        self._physics.setDataFile(datafile)

    def setMPIComm(self, mpicomm):
        """ See :meth:`.PhysicsDriver.setMPIComm`. """
        self._physics.setMPIComm(mpicomm)

    def getMPIComm(self):
        """ See :meth:`c3po.DataAccessor.DataAccessor.getMPIComm`. """
        return self._physics.getMPIComm()

    def initialize(self):
        """ See :meth:`.PhysicsDriver.initialize`. """
        self._physics.init()
        return self._physics.getInitStatus()

    def terminate(self):
        """ See :meth:`.PhysicsDriver.terminate`. """
        self._physics.term()

    def presentTime(self):
        """ See :meth:`.PhysicsDriver.presentTime`. """
        return self._physics.presentTime()

    def computeTimeStep(self):
        """ See :meth:`.PhysicsDriver.computeTimeStep`. """
        return self._physics.computeTimeStep()

    def initTimeStep(self, dt):
        """ See :meth:`.PhysicsDriver.initTimeStep`. """
        return self._physics.initTimeStep(dt)

    def solveTimeStep(self):
        """ See :meth:`.PhysicsDriver.solveTimeStep`. """
        self._physics.solve()
        return self._physics.getSolveStatus()

    def iterateTimeStep(self):
        """ See :meth:`.PhysicsDriver.iterateTimeStep`. """
        self._physics.iterate()
        return self._physics.getIterateStatus()

    def validateTimeStep(self):
        """ See :meth:`.PhysicsDriver.validateTimeStep`. """
        self._physics.validateTimeStep()

    def setStationaryMode(self, stationaryMode):
        """ See :meth:`.PhysicsDriver.setStationaryMode`. """
        self._physics.setStationaryMode(stationaryMode)

    def getStationaryMode(self):
        """ See :meth:`.PhysicsDriver.getStationaryMode`. """
        return self._physics.getStationaryMode()

    def abortTimeStep(self):
        """ See :meth:`.PhysicsDriver.abortTimeStep`. """
        self._physics.abortTimeStep()

    def isStationary(self):
        """ See :meth:`.PhysicsDriver.isStationary`. """
        return self._physics.isStationary()

    def resetTime(self, time_):
        """ See :meth:`.PhysicsDriver.resetTime`. """
        self._physics.resetTime(time_)

    def save(self, label, method):
        """ See :meth:`.PhysicsDriver.save`. """
        self._physics.save(label, method)

    def restore(self, label, method):
        """ See :meth:`.PhysicsDriver.restore`. """
        self._physics.restore(label, method)

    def forget(self, label, method):
        """ See :meth:`.PhysicsDriver.forget`. """
        self._physics.forget(label, method)

    def getInputFieldsNames(self):
        """ See :meth:`c3po.DataAccessor.DataAccessor.getInputFieldsNames`. """
        return self._physics.getInputFieldsNames()

    def getOutputFieldsNames(self):
        """ See :meth:`c3po.DataAccessor.DataAccessor.getOutputFieldsNames`. """
        return self._physics.getOutputFieldsNames()

    def getFieldType(self, name):
        """ See :meth:`c3po.DataAccessor.DataAccessor.getFieldType`. """
        return self._physics.getFieldType(name)

    def getMeshUnit(self):
        """ See :meth:`c3po.DataAccessor.DataAccessor.getMeshUnit`. """
        return self._physics.getMeshUnit()

    def getFieldUnit(self, name):
        """ See :meth:`c3po.DataAccessor.DataAccessor.getFieldUnit`. """
        return self._physics.getFieldUnit(name)

    def getInputMEDDoubleFieldTemplate(self, name):
        """ See :meth:`c3po.DataAccessor.DataAccessor.getInputMEDDoubleFieldTemplate`. """
        return self._physics.getInputMEDDoubleFieldTemplate(name)

    def setInputMEDDoubleField(self, name, field):
        """ See :meth:`c3po.DataAccessor.DataAccessor.setInputMEDDoubleField`. """
        self._physics.setInputMEDDoubleField(name, field)

    def getOutputMEDDoubleField(self, name):
        """ See :meth:`c3po.DataAccessor.DataAccessor.getOutputMEDDoubleField`. """
        return self._physics.getOutputMEDDoubleField(name)

    def updateOutputMEDDoubleField(self, name, field):
        """ See :meth:`c3po.DataAccessor.DataAccessor.updateOutputMEDDoubleField`. """
        return self._physics.updateOutputMEDDoubleField(name, field)

    def getInputMEDIntFieldTemplate(self, name):
        """ See :meth:`c3po.DataAccessor.DataAccessor.getInputMEDIntFieldTemplate`. """
        return self._physics.getInputMEDIntFieldTemplate(name)

    def setInputMEDIntField(self, name, field):
        """ See :meth:`c3po.DataAccessor.DataAccessor.setInputMEDIntField`. """
        self._physics.setInputMEDIntField(name, field)

    def getOutputMEDIntField(self, name):
        """ See :meth:`c3po.DataAccessor.DataAccessor.getOutputMEDIntField`. """
        return self._physics.getOutputMEDIntField(name)

    def updateOutputMEDIntField(self, name, field):
        """ See :meth:`c3po.DataAccessor.DataAccessor.updateOutputMEDIntField`. """
        return self._physics.updateOutputMEDIntField(name, field)

    def getInputMEDStringFieldTemplate(self, name):
        """ See :meth:`c3po.DataAccessor.DataAccessor.getInputMEDStringFieldTemplate`. """
        return self._physics.getInputMEDStringFieldTemplate(name)

    def setInputMEDStringField(self, name, field):
        """ See :meth:`c3po.DataAccessor.DataAccessor.setInputMEDStringField`. """
        self._physics.setInputMEDStringField(name, field)

    def getOutputMEDStringField(self, name):
        """ See :meth:`c3po.DataAccessor.DataAccessor.getOutputMEDStringField`. """
        return self._physics.getOutputMEDStringField(name)

    def updateOutputMEDStringField(self, name, field):
        """ See :meth:`c3po.DataAccessor.DataAccessor.updateOutputMEDStringField`. """
        return self._physics.updateOutputMEDStringField(name, field)

    def getInputValuesNames(self):
        """ See :meth:`c3po.DataAccessor.DataAccessor.getInputValuesNames`. """
        return self._physics.getInputValuesNames()

    def getOutputValuesNames(self):
        """ See :meth:`c3po.DataAccessor.DataAccessor.getOutputValuesNames`. """
        return self._physics.getOutputValuesNames()

    def getValueType(self, name):
        """ See :meth:`c3po.DataAccessor.DataAccessor.getValueType`. """
        return self._physics.getValueType(name)

    def getValueUnit(self, name):
        """ See :meth:`c3po.DataAccessor.DataAccessor.getValueUnit`. """
        return self._physics.getValueUnit(name)

    def setInputDoubleValue(self, name, value):
        """ See :meth:`c3po.DataAccessor.DataAccessor.setInputDoubleValue`. """
        self._physics.setInputDoubleValue(name, value)

    def getOutputDoubleValue(self, name):
        """ See :meth:`c3po.DataAccessor.DataAccessor.getOutputDoubleValue`. """
        return self._physics.getOutputDoubleValue(name)

    def setInputIntValue(self, name, value):
        """ See :meth:`c3po.DataAccessor.DataAccessor.setInputIntValue`. """
        self._physics.setInputIntValue(name, value)

    def getOutputIntValue(self, name):
        """ See :meth:`c3po.DataAccessor.DataAccessor.getOutputIntValue`. """
        return self._physics.getOutputIntValue(name)

    def setInputStringValue(self, name, value):
        """ See :meth:`c3po.DataAccessor.DataAccessor.setInputStringValue`. """
        self._physics.setInputStringValue(name, value)

    def getOutputStringValue(self, name):
        """ See :meth:`c3po.DataAccessor.DataAccessor.getOutputStringValue`. """
        return self._physics.getOutputStringValue(name)

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

    def __init__(self, ICOCOclass):
        """! Build a APOLLO3Driver object.

        @param ICOCOclass implementation of the ICOCO interface for APOLLO3.
        """
        PhysicsDriver.__init__(self)
        self._apollo3 = ICOCOclass
        self._isInit = False

    def setDataFile(self, datafile):
        self._apollo3.setDataFile(datafile)

    def initialize(self):
        if not self._isInit:
            self._isInit = True
            return self._apollo3.initialize()
        return True

    def terminate(self):
        self._isInit = False
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

    def abortTimeStep(self):
        self._apollo3.abortTimeStep()

    def getInputMEDFieldTemplate(self, name):
        return self._apollo3.getInputMEDFieldTemplate(name)

    def setInputMEDField(self, name, field):
        self._apollo3.setInputMEDField(name, field)

    def getOutputMEDField(self, name):
        return self._apollo3.getOutputMEDField(name)

    def setValue(self, name, value):
        self._apollo3.setValue(name, value)

    def getValue(self, name):
        return self._apollo3.getValue(name)

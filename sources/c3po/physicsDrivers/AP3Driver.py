# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class AP3Driver. """
from __future__ import print_function, division
from C3PO.PhysicsDriver import PhysicsDriver


class AP3Driver(PhysicsDriver):
    """! This is the implementation of PhysicsDriver for APOLLO3. """

    def __init__(self, ICOCOclass):
        """! Build a AP3Driver object.

        @param ICOCOclass implementation of the ICOCO interface for APOLLO3.
        """
        PhysicsDriver.__init__(self)
        self.neutro_ = ICOCOclass
        self.isInit_ = False

    def setDataFile(self, df):
        self.neutro_.setDataFile(df)

    def initialize(self):
        if not self.isInit_:
            self.isInit_ = True
            return self.neutro_.initialize()
        else:
            return True

    def terminate(self):
        self.isInit_ = False
        self.neutro_.terminate()

    def presentTime(self):
        return self.neutro_.presentTime()

    def computeTimeStep(self):
        return self.neutro_.computeTimeStep()

    def initTimeStep(self, dt):
        return self.neutro_.initTimeStep(dt)

    def solveTimeStep(self):
        return self.neutro_.solveTimeStep()

    def validateTimeStep(self):
        self.neutro_.validateTimeStep()

    def abortTimeStep(self):
        self.neutro_.abortTimeStep()

    def getInputMEDFieldTemplate(self, name):
        return self.neutro_.getInputMEDFieldTemplate(name)

    def setInputMEDField(self, name, field):
        self.neutro_.setInputMEDField(name, field)

    def getOutputMEDField(self, name):
        return self.neutro_.getOutputMEDField(name)

    def setValue(self, name, value):
        self.neutro_.setValue(name, value)

    def getValue(self, name):
        return self.neutro_.getValue(name)

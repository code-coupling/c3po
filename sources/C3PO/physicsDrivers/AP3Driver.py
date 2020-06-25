# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contains the class AP3Driver. """
from __future__ import print_function, division

import MEDCoupling

from C3PO.physicsDriver import physicsDriver


class AP3Driver(physicsDriver):
    """ This is the implementation of physicsDriver for APOLLO3. """

    def __init__(self, ICOCOclass):
        """ Builds a AP3Driver object.

        :param ICOCOclass: Object implementing the ICOCO interface for APOLLO3.
        """
        physicsDriver.__init__(self)
        self.neutro_ = ICOCOclass
        self.isSolveSteadyStateAsked_ = False
        self.isInit_ = False

    def initialize(self):
        if not self.isInit_:
            self.isInit_ = True
            return self.neutro_.initialize()
        else:
            return True

    def terminate(self):
        return True

    def presentTime(self):
        return self.neutro_.presentTime()

    def computeTimeStep(self):
        return self.neutro_.computeTimeStep()

    def initTimeStep(self, dt):
        self.isSolveSteadyStateAsked_ = (dt <= 0)
        return self.neutro_.initTimeStep(dt)

    def solveTimeStep(self):
        if self.isSolveSteadyStateAsked_:
            return self.neutro_.solveSteadyState()
        else:
            return self.neutro_.solveTimeStep()

    def validateTimeStep(self):
        self.neutro_.validateTimeStep()

    def abortTimeStep(self):
        if not self.isSolveSteadyStateAsked_:
            self.neutro_.abortTimeStep()
        else:
            pass

    def getInputMEDFieldTemplate(self, name):
        """ Returns an empty field lying on the MEDCouplingMesh object used by APOLLO3. 

        Fields given to APOLLO3 by setInputMEDField must used this mesh.
        """
        outputField = MEDCoupling.MEDCouplingFieldDouble(MEDCoupling.ON_CELLS, MEDCoupling.ONE_TIME)
        outputField.setMesh(self.neutro_.getMesh())
        return outputField

    def setInputMEDField(self, name, field):
        self.neutro_.setInputMEDField(name=name, fieldMed=field)

    def getOutputMEDField(self, name):
        return self.neutro_.getOutputMEDField(name=name)

    def setValue(self, name, value):
        self.neutro_.setValue(name, value)

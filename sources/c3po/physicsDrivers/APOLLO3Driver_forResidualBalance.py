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
from .APOLLO3Driver import APOLLO3Driver
import Apollo3 

class APOLLO3Driver_forResidualBalance(APOLLO3Driver):
    """! This is the implementation of PhysicsDriver for APOLLO3. """

    def __init__(self, apollo3ICoCo):
        """! Build a APOLLO3Driver object.

        @param apollo3ICoCo implementation of the ICOCO interface for APOLLO3.
        """
        APOLLO3Driver.__init__(self,apollo3ICoCo)
        if apollo3ICoCo.GetICoCoMajorVersion() != self.GetICoCoMajorVersion():
            raise AssertionError("The ICoCo major version of the provided object ({}) is not the expected one ({})".format(apollo3ICoCo.GetICoCoMajorVersion(), self.GetICoCoMajorVersion()))
        self._apollo3 = apollo3ICoCo

    def getOutputDoubleValue(self, name):  # pylint: disable=too-many-return-statements        
        if name == "PRECISION_INITIALE":
            number_external_iterations = self._apollo3.a3d.solverAPI.getParameterInt(Apollo3.Tools.SolverAPI_Parameter.ParameterEnum.NEXT)
            self._apollo3.a3d.solverAPI.setParameter(Apollo3.Tools.SolverAPI_Parameter.ParameterEnum.NEXT,1)
            self.solveTimeStep()
            self._apollo3.a3d.solverAPI.setParameter(Apollo3.Tools.SolverAPI_Parameter.ParameterEnum.NEXT,number_external_iterations)
            return self._apollo3.a3d.solverAPI.getReachedFluxPrecision()
        elif name == "PRECISION_ATTEINTE":
            return self._apollo3.a3d.solverAPI.getReachedFluxPrecision()
        elif name == "PRECISION":
            return self._apollo3.a3d.solverAPI.getParameterFloat(Apollo3.Tools.SolverAPI_Parameter.ParameterEnum.PRECF)
        else :
            return APOLLO3Driver.getOutputDoubleValue(self, name)

    def setInputDoubleValue(self, name, value):
     
        if name == "PRECISION" : 
            self._apollo3.a3d.solverAPI.setParameter(Apollo3.Tools.SolverAPI_Parameter.ParameterEnum.PRECF,value)
            self._apollo3.a3d.solverAPI.setParameter(Apollo3.Tools.SolverAPI_Parameter.ParameterEnum.PRECVP,value/10)
        else : 
            APOLLO3Driver.setInputDoubleValue(self, name, value)

    def setInputIntValue(self, name, value):
              
        if(name == "SOLVER_MAX_ITERATIONS") : 
            self._apollo3.a3d.solverAPI.setParameter(Apollo3.Tools.SolverAPI_Parameter.ParameterEnum.NEXT,value)
        else:
            APOLLO3Driver.setInputIntValue(self, name, value)           
# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class Coupler. """
from __future__ import print_function, division

from C3PO.PhysicsDriver import PhysicsDriver


class NormChoice(object):
    """! Enum definition of norm choice.

    Values :
        - normMax
        - norm2
    """
    normMax = 0
    norm2 = 1


class Coupler(PhysicsDriver):
    """! Coupler is the base class for the definition of a coupling. 

    A coupling is defined using PhysicsDriver, DataManager and Exchanger objects. 
    A user needs to define his own class inheriting from Coupler and to define its solveTimeStep() method. 
    It may also be necessary to overload the get/set methods (of fields and / or of scalars) inherited from PhysicsDriver.

    @note Coupler inherits from PhysicsDriver what allows to define a coupling of couplings! 
    """

    def __init__(self, physics, exchangers, dataManagers=[]):
        """! Build an Coupler object.

        @param physics a list (or dictionary) of PhysicsDriver objects to be coupled.
        @param exchangers a list (or dictionary) of Exchanger for the coupling.
        @param dataManagers a list (or dictionary) of DataManager used in the coupling.
        """
        PhysicsDriver.__init__(self)
        self.physicsDrivers_ = physics
        self.physicsDriversList_ = physics if not isinstance(physics, dict) else list(physics.values())
        self.exchangers_ = exchangers
        self.dataManagers_ = dataManagers
        self.norm_ = NormChoice.normMax
        self.dt_ = 1.e30

    def initialize(self):
        """! See PhysicsDriver.initialize(). """
        for physics in self.physicsDriversList_:
            physics.init()
        resu = True
        for physics in self.physicsDriversList_:
            resu = (resu and physics.getInitStatus())
        return resu

    def terminate(self):
        """! See PhysicsDriver.terminate(). """
        resu = True
        for physics in self.physicsDriversList_:
            resu = (resu and physics.terminate())
        return resu

    def presentTime(self):
        """! See PhysicsDriver.presentTime(). """
        if len(self.physicsDriversList_) > 0:
            return self.physicsDriversList_[0].presentTime()
        return 0.

    def computeTimeStep(self):
        """! See PhysicsDriver.computeTimeStep(). """
        (dt, stop) = (1.e30, True)
        for physics in self.physicsDriversList_:
            (dtPhysics, stopPhysics) = physics.computeTimeStep()
            if dtPhysics < dt:
                dt = dtPhysics
            stop = (stop and stopPhysics)
        return (dt, stop)

    def initTimeStep(self, dt):
        """! See PhysicsDriver.initTimeStep(). """
        self.dt_ = dt
        resu = True
        for physics in self.physicsDriversList_:
            resu = (resu and physics.initTimeStep(dt))
        return resu

    def getSolveStatus(self):
        """! See PhysicsDriver.getSolveStatus(). """
        resu = True
        for physics in self.physicsDriversList_:
            resu = resu and physics.getSolveStatus()
        return resu

    def validateTimeStep(self):
        """! See PhysicsDriver.validateTimeStep(). """
        for physics in self.physicsDriversList_:
            physics.validateTimeStep()

    def abortTimeStep(self):
        """! See PhysicsDriver.abortTimeStep(). """
        for physics in self.physicsDriversList_:
            physics.abortTimeStep()

    def isStationary(self):
        """! See PhysicsDriver.isStationary(). """
        resu = True
        for physics in self.physicsDriversList_:
            resu = (resu and physics.isStationary())
        return resu

    def setNormChoice(self, choice):
        """! Choose a norm for future use. 

        @param choice to be choosen between :
            - NormChoice.normMax : infinite norm. This is the default choice.
            - NormChoice.norm2 : norm 2 ( sqrt(sum_i(val[i] * val[i])) ).
        """
        self.norm_ = choice

    def getNorm(self, data):
        """! Return the norm choosen by setNormChoice of data (a DataManager). 

        @param data a DataManager object.

        @return the asked norm of data.
        """
        if self.norm_ == NormChoice.normMax:
            return data.normMax()
        elif self.norm_ == NormChoice.norm2:
            return data.norm2()
        else:
            raise Exception("Coupler.getNorm The required norm is unknown.")

    def readNormData(self):
        normData = []
        for data in self.dataManagers_:
            normData.append(self.getNorm(data))
        return normData

    def normalizeData(self, norms):
        for i, norm in enumerate(norms):
            if norm > 0.:
                self.dataManagers_[i] *= 1. / norm

    def denormalizeData(self, norms):
        for i, norm in enumerate(norms):
            if norm > 0.:
                self.dataManagers_[i] *= norm

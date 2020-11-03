# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contains the class Coupler. """
from __future__ import print_function, division

from .PhysicsDriver import PhysicsDriver


class NormChoice(object):
    """ Enum definition of norm choice.

    Values :
        - normMax
        - norm2
    """
    normMax = 0
    norm2 = 1


class Coupler(PhysicsDriver):
    """ This is the base class for defining a coupling. This definition of a coupling uses PhysicsDriver, DataManager and Exchanger objects. 

    Coupler inherits from PhysicsDriver which allows to define a coupling of couplings! 

    Most of the methods inherited from PhysicsDriver are overloaded by calls to the same methods of the coupled PhysicsDriver.

    A user needs to define his own class inheriting from coupling and defining the solveTimeStep() method in order to define the sequence of calculations and exchanges to be made at each time step.
    It may also be necessary to overload the methods inherited from PhysicsDriver allowing access to data (MED or scalar) if one wishes to make coupling of couplings.
    """

    def __init__(self, physics, exchangers, dataManagers=[]):
        """ Builds an Coupler object.

        :param physics: the list of PhysicsDriver objects to be coupled.
        :param exchangers: the list of Exchanger for the coupling.
        :param dataManagers: the list of DataManager used in the coupling.
        """
        PhysicsDriver.__init__(self)
        self.physicsDrivers_ = physics
        self.exchangers_ = exchangers
        self.dataManagers_ = dataManagers
        self.norm_ = NormChoice.normMax
        self.dt_ = 1.e30

    def initialize(self):
        for physics in self.physicsDrivers_:
            physics.init()
        resu = True
        for physics in self.physicsDrivers_:
            resu = (resu and physics.getInitStatus())
        return resu

    def terminate(self):
        resu = True
        for physics in self.physicsDrivers_:
            resu = (resu and physics.terminate())
        return resu

    def presentTime(self):
        if len(self.physicsDrivers_) > 0:
            return self.physicsDrivers_[0].presentTime()
        return 0.

    def computeTimeStep(self):
        (dt, stop) = (1.e30, True)
        for physics in self.physicsDrivers_:
            (dtPhysics, stopPhysics) = physics.computeTimeStep()
            if dtPhysics < dt:
                dt = dtPhysics
            stop = (stop and stopPhysics)
        return (dt, stop)

    def initTimeStep(self, dt):
        self.dt_ = dt
        resu = True
        for physics in self.physicsDrivers_:
            resu = (resu and physics.initTimeStep(dt))
        return resu

    def getSolveStatus(self):
        resu = True
        for physics in self.physicsDrivers_:
            resu = resu and physics.getSolveStatus()
        return resu

    def validateTimeStep(self):
        for physics in self.physicsDrivers_:
            physics.validateTimeStep()

    def abortTimeStep(self):
        for physics in self.physicsDrivers_:
            physics.abortTimeStep()

    def isStationary(self):
        resu = True
        for physics in self.physicsDrivers_:
            resu = (resu and physics.isStationary())
        return resu

    def setNormChoice(self, choice):
        """ Allows to choose a norm for future use. 

        Possible choices are :
            - NormChoice.normMax : infinite norm. This is the default choice.
            - NormChoice.norm2 : norm 2 ( sqrt(sum_i(val[i] * val[i])) ).
        """
        self.norm_ = choice

    def getNorm(self, data):
        """ Return the norm of data (a DataManager) choosen by setNormChoice. """
        if self.norm_ == NormChoice.normMax:
            return data.normMax()
        elif self.norm_ == NormChoice.norm2:
            return data.norm2()
        else:
            raise Exception("Coupler.getNorm The required norm is unknown.")

# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class FixedPointCoupler. """
from __future__ import print_function, division

from c3po.Coupler import Coupler
from c3po.CollaborativeDataManager import CollaborativeDataManager


class FixedPointCoupler(Coupler):
    """! FixedPointCoupler inherits from Coupler and proposes a damped fixed point algorithm.

    The class proposes an algorithm for the resolution of F(X) = X. Thus FixedPointCoupler is a Coupler working with :

    - A single PhysicsDriver (possibly a Coupler) defining the calculations to be made each time F is called.
    - A list of DataManager allowing to manipulate the data in the coupling (the X).
    - Two Exchanger allowing to go from the PhysicsDriver to the DataManager and vice versa.

    Each DataManager is normalized with its own norm got after the first iteration.
    They are then used as a single DataManager using CollaborativeDataManager.

    At each iteration we do (with n the iteration number and alpha the damping factor):

        X^{n+1} = alpha * F(X^{n}) + (1 - alpha) * X^{n}

    The convergence criteria is : ||F(X^{n}) - X^{n}|| / ||X^{n+1}|| < tolerance. The default norm used is the infinite norm. setNormChoice() allows to choose another one.

    The default value of tolerance is 1.E-6. Call setConvergenceParameters() to change it.

    The default maximum number of iterations is 100. Call setConvergenceParameters() to change it.

    The default damping factor is 1 (no damping). Call setDampingFactor() to change it.
    """

    def __init__(self, physics, exchangers, dataManagers):
        """! Build a FixedPointCoupler object.

        @param physics list of only one PhysicsDriver (possibly a Coupler).
        @param exchangers list of exactly two Exchanger allowing to go from the PhysicsDriver to the DataManager and vice versa.
        @param dataManagers list of DataManager.
        """
        Coupler.__init__(self, physics, exchangers, dataManagers)
        self._tolerance = 1.E-6
        self._maxiter = 100
        self._dampingFactor = 1.
        self._isConverged = False
        self._printLevel = 2

        if not isinstance(physics, list) or not isinstance(exchangers, list) or not isinstance(dataManagers, list):
            raise Exception("FixedPointCoupler.__init__ physics, exchangers and dataManagers must be lists!")
        if len(physics) != 1:
            raise Exception("FixedPointCoupler.__init__ There must be only one PhysicsDriver")
        if len(exchangers) != 2:
            raise Exception("FixedPointCoupler.__init__ There must be exactly two Exchanger")

    def setPrintLevel(self, level):
        """! Set the print level during iterations (0=None, 1 keeps last iteration, 2 prints every iteration).

        @param level integer in range [0;2].
        """
        if not level in [0, 1, 2]:
            raise Exception("FixedPointCoupler.setPrintLevel level should be one of [0, 1, 2]!")
        self._printLevel = level

    def setConvergenceParameters(self, tolerance, maxiter):
        """! Set the convergence parameters (tolerance and maximum number of iterations).

        @param tolerance the convergence threshold in ||F(X^{n}) - X^{n}|| / ||X^{n+1}|| < tolerance.
        @param maxiter the maximal number of iterations.
        """
        self._tolerance = tolerance
        self._maxiter = maxiter

    def setDampingFactor(self, dampingFactor):
        """! Set the damping factor of the method.

        @param dampingFactor the damping factor alpha in the formula X^{n+1} = alpha * F(X^{n}) + (1 - alpha) * X^{n}.
        """
        self._dampingFactor = dampingFactor

    def solveTimeStep(self):
        """! Solve a time step using the damped fixed-point algorithm.

        See also c3po.PhysicsDriver.PhysicsDriver.solveTimeStep().
        """
        iiter = 0
        error = self._tolerance + 1.
        physics = self._physicsDrivers[0]
        physics2Data = self._exchangers[0]
        data2physics = self._exchangers[1]

        # Init
        if self._printLevel:
            printEndOfLine = "\r" if self._printLevel == 1 else "\n"
            print("iteration {} ".format(iiter), end=printEndOfLine)

        physics.solve()
        physics2Data.exchange()

        data = CollaborativeDataManager(self._dataManagers)
        normData = self.readNormData()
        self.normalizeData(normData)

        previousData = data.clone()
        iiter += 1

        while error > self._tolerance and iiter < self._maxiter:
            if self._printLevel:
                print("iteration {} ".format(iiter), end="")

            self.abortTimeStep()
            self.initTimeStep(self._dt)
            self.denormalizeData(normData)
            data2physics.exchange()

            physics.solve()
            physics2Data.exchange()
            self.normalizeData(normData)

            if self._dampingFactor != 1.:
                data *= self._dampingFactor
                data.imuladd(1. - self._dampingFactor, previousData)

            if iiter == 1:
                diffData = data.clone()
            else:
                diffData.copy(data)
            diffData -= previousData
            error = self.getNorm(diffData) / self.getNorm(data)
            error /= self._dampingFactor

            previousData.copy(data)

            iiter += 1
            if self._printLevel:
                print("error : {:.3e} ".format(error), end=printEndOfLine)
            
        if self._printLevel == 1:
            print("iteration {} error : {:.3e} ".format(iiter, error))

        self.denormalizeData(normData)
        return physics.getSolveStatus() and error <= self._tolerance

    # On definit les methodes suivantes pour qu'elles soient vues par tracer.
    def initialize(self):
        """! See Coupler.initialize(). """
        return Coupler.initialize(self)

    def terminate(self):
        """! See Coupler.terminate(). """
        Coupler.terminate(self)

    def computeTimeStep(self):
        """! See Coupler.computeTimeStep(). """
        return Coupler.computeTimeStep(self)

    def initTimeStep(self, dt):
        """! See Coupler.initTimeStep(). """
        return Coupler.initTimeStep(self, dt)

    def validateTimeStep(self):
        """! See Coupler.validateTimeStep(). """
        Coupler.validateTimeStep(self)

    def setStationaryMode(self, stationaryMode):
        """! See Coupler.setStationaryMode(). """
        Coupler.setStationaryMode(self, stationaryMode)

    def abortTimeStep(self):
        """! See Coupler.abortTimeStep(). """
        Coupler.abortTimeStep(self)

    def resetTime(self, time_):
        """! See Coupler.resetTime(). """
        Coupler.resetTime(self, time_)

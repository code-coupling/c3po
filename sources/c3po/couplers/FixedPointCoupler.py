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

from c3po.PhysicsDriver import PhysicsDriver
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

    The convergence criteria is : ||F(X^{n}) - X^{n}|| / ||F(X^{n})|| < tolerance. The default norm used is the infinite norm. setNormChoice() allows to choose another one.

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
        self._printLevel = 2
        self._useIterate = False
        self._iter = 0

        if not isinstance(physics, list) or not isinstance(exchangers, list) or not isinstance(dataManagers, list):
            raise Exception("FixedPointCoupler.__init__ physics, exchangers and dataManagers must be lists!")
        if len(physics) != 1:
            raise Exception("FixedPointCoupler.__init__ There must be only one PhysicsDriver")
        if len(exchangers) != 2:
            raise Exception("FixedPointCoupler.__init__ There must be exactly two Exchanger")

        self._data = CollaborativeDataManager(self._dataManagers)
        self._previousData = None
        self._normData = 0.

    def setConvergenceParameters(self, tolerance, maxiter):
        """! Set the convergence parameters (tolerance and maximum number of iterations).

        @param tolerance the convergence threshold in ||F(X^{n}) - X^{n}|| / ||F(X^{n})|| < tolerance.
        @param maxiter the maximal number of iterations.
        """
        self._tolerance = tolerance
        self._maxiter = maxiter

    def setDampingFactor(self, dampingFactor):
        """! Set the damping factor of the method.

        @param dampingFactor the damping factor alpha in the formula X^{n+1} = alpha * F(X^{n}) + (1 - alpha) * X^{n}.
        """
        self._dampingFactor = dampingFactor

    def setPrintLevel(self, level):
        """! Set the print level during iterations (0=None, 1 keeps last iteration, 2 prints every iteration).

        @param level integer in range [0;2]. Default: 2.
        """
        if not level in [0, 1, 2]:
            raise Exception("FixedPointCoupler.setPrintLevel level should be one of [0, 1, 2]!")
        self._printLevel = level

    def setUseIterate(self, useIterate):
        """ ! If True is given, the iterate() method on the given PhysicsDriver is called instead of the solve() method.

        @param useIterate bool. Set True to use iterate(), False to use solve(). Default: False.
        """
        self._useIterate = useIterate

    def iterateTimeStep(self):
        """! Make on iteration of a damped fixed-point algorithm.

        See also c3po.PhysicsDriver.PhysicsDriver.iterateTimeStep().
        """
        physics = self._physicsDrivers[0]
        physics2Data = self._exchangers[0]
        data2physics = self._exchangers[1]

        if self._iter > 0:
            if not self._useIterate:
                physics.abortTimeStep()
                physics.initTimeStep(self._dt)
            data2physics.exchange()

        physics.iterate() if self._useIterate else physics.solve()
        physics2Data.exchange()

        if self._iter == 0:
            self._normData = self.readNormData()
        self.normalizeData(self._normData)

        if self._iter > 0:
            normNewData = self.getNorm(self._data)
            self._data -= self._previousData
            error = self.getNorm(self._data) / normNewData

            self._data *= self._dampingFactor
            self._data += self._previousData

            self._previousData.copy(self._data)
        else:
            error = self._tolerance + 1.
            self._previousData = self._data.clone()

        self.denormalizeData(self._normData)
        if self._printLevel:
            printEndOfLine = "\r" if self._printLevel == 1 else "\n"
            if self._iter == 0:
                print("fixed-point iteration {} ".format(self._iter), end=printEndOfLine)
            else:
                print("fixed-point iteration {} error : {:.5e}".format(self._iter, error), end=printEndOfLine)

        self._iter += 1

        succeed, converged = physics.getIterateStatus() if self._useIterate else (physics.getSolveStatus(), True)
        converged = converged and error <= self._tolerance

        return succeed, converged

    def solveTimeStep(self):
        """! Solve a time step using the damped fixed-point algorithm.

        See also c3po.PhysicsDriver.PhysicsDriver.solveTimeStep().
        """
        converged = False
        succeed = True

        while succeed and (not converged) and self._iter < self._maxiter:
            self.iterate()
            succeed, converged = self.getIterateStatus()

        return succeed and converged

    def getIterateStatus(self):
        """! See PhysicsDriver.getSolveStatus(). """
        return PhysicsDriver.getIterateStatus(self)

    def getSolveStatus(self):
        """! See PhysicsDriver.getSolveStatus(). """
        return PhysicsDriver.getSolveStatus(self)

    def initTimeStep(self, dt):
        """ See c3po.PhysicsDriver.PhysicsDriver.initTimeStep().  """
        self._iter = 0
        self._previousData = 0
        Coupler.initTimeStep(self, dt)

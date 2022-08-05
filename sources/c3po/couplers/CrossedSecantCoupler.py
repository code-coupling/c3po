# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class CrossedSecantCoupler. """
from __future__ import print_function, division

from c3po.Coupler import Coupler
from c3po.CollaborativeDataManager import CollaborativeDataManager


class CrossedSecantCoupler(Coupler):
    """! CrossedSecantCoupler inherits from Coupler and proposes a fixed point algorithm with crossed secant acceleration.

    The class proposes an algorithm for the resolution of F(X) = X. Thus CrossedSecantCoupler is a Coupler working with :

    - A single PhysicsDriver (possibly a Coupler) defining the calculations to be made each time F is called.
    - A list of DataManager allowing to manipulate the data in the coupling (the X).
    - Two Exchanger allowing to go from the PhysicsDriver to the DataManager and vice versa.

    Each DataManager is normalized with its own norm got after the first iteration.
    They are then used as a single DataManager using CollaborativeDataManager.

    At each iteration we do (with n the iteration number):

        X^{n+1} = F(X^{n}) - ( F(X^{n}) - X^{n} ) * [ ( F(X^{n}) - F(X^{n-1}) ) .dot. ( F(X^{n}) - X^{n} - ( F(X^{n-1}) - X^{n-1} ) )  ] / (|| F(X^{n}) - X^{n} - ( F(X^{n-1}) - X^{n-1} ) ||**2)

    The convergence criteria is : ||F(X^{n}) - X^{n}|| / ||X^{n+1}|| < tolerance. The default norm used is the infinite norm. setNormChoice() allows to choose another one.

    The default value of tolerance is 1.E-6. Call setConvergenceParameters() to change it.

    The default maximum number of iterations is 100. Call setConvergenceParameters() to change it.
    """

    def __init__(self, physics, exchangers, dataManagers):
        """! Build a CrossedSecantCoupler object.

        @param physics list of only one PhysicsDriver (possibly a Coupler).
        @param exchangers list of exactly two Exchanger allowing to go from the PhysicsDriver to the DataManager and vice versa.
        @param dataManagers list of DataManager.
        """
        Coupler.__init__(self, physics, exchangers, dataManagers)
        self._tolerance = 1.E-6
        self._maxiter = 100
        self._isConverged = False
        self._printLevel = 2

        if not isinstance(physics, list) or not isinstance(exchangers, list) or not isinstance(dataManagers, list):
            raise Exception("CrossedSecantCoupler.__init__ physics, exchangers and dataManagers must be lists!")
        if len(physics) != 1:
            raise Exception("CrossedSecantCoupler.__init__ There must be only one PhysicsDriver")
        if len(exchangers) != 2:
            raise Exception("CrossedSecantCoupler.__init__ There must be exactly two Exchanger")

    def setConvergenceParameters(self, tolerance, maxiter):
        """! Set the convergence parameters (tolerance and maximum number of iterations).

        @param tolerance the convergence threshold in ||F(X^{n}) - X^{n}|| / ||X^{n+1}|| < tolerance.
        @param maxiter the maximal number of iterations.
        """
        self._tolerance = tolerance
        self._maxiter = maxiter

    def setPrintLevel(self, level):
        """! Set the print level during iterations (0=None, 1 keeps last iteration, 2 prints every iteration).

        @param level integer in range [0;2]. Default: 2.
        """
        if not level in [0, 1, 2]:
            raise Exception("FixedPointCoupler.setPrintLevel level should be one of [0, 1, 2]!")
        self._printLevel = level

    def solveTimeStep(self):
        """! Solve a time step using the damped fixed-point algorithm.

        See also c3po.PhysicsDriver.PhysicsDriver.solveTimeStep().
        """
        iiter = 0
        error = self._tolerance + 1.
        physics = self._physicsDrivers[0]
        physics2Data = self._exchangers[0]
        data2physics = self._exchangers[1]

        # Initialisation : iteration 0
        if self._printLevel:
            printEndOfLine = "\r" if self._printLevel == 1 else "\n"
            print("crossed secant iteration {} ".format(iiter), end=printEndOfLine)

        physics.solve()
        physics2Data.exchange()

        data = CollaborativeDataManager(self._dataManagers)
        normData = self.readNormData()
        self.normalizeData(normData)
        diffData = data.clone()
        iiter += 1

        # First iteration without acceleration
        self.abortTimeStep()
        self.initTimeStep(self._dt)
        self.denormalizeData(normData)
        data2physics.exchange()

        physics.solve()
        physics2Data.exchange() # data = G(X0) , previousData = X0
        self.normalizeData(normData)
        diffData -= data
        diffDataOld = diffData.clone() # G(x0) - x0

        error = self.getNorm(diffData) / self.getNorm(data)
        iiter += 1
        if self._printLevel:
            print("crossed secant iteration {} error : {:.5e} ".format(iiter - 1, error), end=printEndOfLine)
        dataOld = data.clone() # dataOld = X1 = G(x0)
        diffData.copy(data)

        while error > self._tolerance and iiter < self._maxiter:
            self.abortTimeStep()
            self.initTimeStep(self._dt)
            self.denormalizeData(normData)
            data2physics.exchange()

            physics.solve()
            physics2Data.exchange()
            self.normalizeData(normData)

            diffData -= data

            error = self.getNorm(diffData) / self.getNorm(data)
            iiter += 1
            if self._printLevel:
                print("crossed secant iteration {} error : {:.5e} ".format(iiter - 1, error), end=printEndOfLine)

            if error > self._tolerance :
                dataOld -= data
                diffDataOld -= diffData
                normDenominator = diffDataOld.norm2()
                factor = - dataOld.dot(diffDataOld)/(normDenominator * normDenominator)
                dataOld.copy(data)
                diffDataOld.copy(diffData)
                diffData *= factor
                data += diffData
                diffData.copy(data)

        self.denormalizeData(normData)
        return physics.getSolveStatus() and error <= self._tolerance

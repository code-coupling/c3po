# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contains the class GaussSeidelCoupler. """
from __future__ import print_function, division

from C3PO.coupler import coupler


class GaussSeidelCoupler(coupler):
    """ GaussSeidelCoupler inherits from coupler and proposes a damped fixed point algorithm.

    The class proposes an algorithm for the resolution of F(X) = X. Thus GaussSeidelCoupler is a coupler working with precisely :

        - A single physicsDriver (possibly a coupler) defining the calculations to be made each time F is called.
        - A single dataManager allowing to manipulate the data to be damped in the coupling (the X).
        - Two exchangers allowing to go from the physicsDrivers to the dataManager and vice versa.

    At each iteration we do (with n the iteration number and alpha the damping factor):

        X^{n+1} = alpha * F(X^{n}) + (1 - alpha) * X^{n}

    The convergence criteria is : ||F(X^{n}) - X^{n}|| / ||X^{n+1}|| < tolerance. The default norm used is the infinite norm. setNormChoice allows to choose another one.

    The default value of tolerance is 1.E-6. Call setConvergenceParameters to change it.
    The default maximum number of iterations is 100. Call setConvergenceParameters to change it.
    The default damping factor is 1 (no damping). Call setDampingFactor to change it.
    """

    def __init__(self, physics, exchangers, dataManager):
        """ Builds a GaussSeidelCoupler object.

        :param physics: list of only one physicsDriver (possibly a coupler).
        :param exchangers: list of exactly two exchangers allowing to go from the physicsDriver to the dataManager and vice versa.
        :param dataManager: list of only one dataManager.

        """
        coupler.__init__(self, physics, exchangers, dataManager)
        self.tolerance_ = 1.E-6
        self.maxiter_ = 100
        self.dampingFactor_ = 1.
        self.isConverged_ = False
        if len(physics) != 1:
            raise Exception("GaussSeidelCoupler.__init__ There must be only one physicsDriver")
        if len(exchangers) != 2:
            raise Exception("GaussSeidelCoupler.__init__ There must be exactly two exchangers")
        if len(dataManager) != 1:
            raise Exception("GaussSeidelCoupler.__init__ There must be only one dataManager")

    def setConvergenceParameters(self, tolerance, maxiter):
        """ Sets the convergence parameters (tolerance and maximum number of iterations). """
        self.tolerance_ = tolerance
        self.maxiter_ = maxiter

    def setDampingFactor(self, dampingFactor):
        """ Sets a new damping factor. """
        self.dampingFactor_ = dampingFactor

    def solveTimeStep(self):
        """ Solves a time step using the damped Gauss-Seidel algorithm. """
        iiter = 0
        error = self.tolerance_ + 1.
        physics = self.physicsDrivers_[0]
        physics2Data = self.exchangers_[0]
        data2physics = self.exchangers_[1]
        data = self.dataManagers_[0]

        # Init
        print("iteration ", iiter)
        physics.solve()
        physics2Data.exchange()
        previousData = data.clone()
        iiter += 1

        while error > self.tolerance_ and iiter < self.maxiter_:
            print("iteration ", iiter)

            self.abortTimeStep()
            self.initTimeStep(self.dt_)
            data2physics.exchange()

            physics.solve()
            physics2Data.exchange()

            if self.dampingFactor_ != 1.:
                data *= self.dampingFactor_
                data.imuladd(1. - self.dampingFactor_, previousData)

            if iiter == 1:
                diffData = data.clone()
            else:
                diffData.copy(data)
            diffData -= previousData
            error = self.getNorm(diffData) / self.getNorm(data)
            error /= self.dampingFactor_

            previousData.copy(data)

            iiter += 1
            print("error : ", error)

        return physics.getSolveStatus() and not(error > self.tolerance_)

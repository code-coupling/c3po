# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class AndersonCoupler. """
from __future__ import print_function, division

import numpy as np

from c3po.Coupler import Coupler


class AndersonCoupler(Coupler):
    """! AndersonCoupler inherits from Coupler and proposes a fixed point algorithm with Anderson acceleration.

    The class proposes an algorithm for the resolution of F(X) = X. Thus AndersonCoupler is a Coupler working with precisely :

    - A single PhysicsDriver (possibly a Coupler) defining the calculations to be made each time F is called.
    - A single DataManager allowing to manipulate the data in the coupling (the X).
    - Two Exchanger allowing to go from the PhysicsDriver to the DataManager and vice versa.

    The first two iterations just do (with n the iteration number):

        X^{n+1} = F(X^{n})

    Then the Anderson acceleration starts and computes X^{n+1} as a linear combination of [alpha * F(X^{n-i}) + (1. - alpha) * X^{n-i}].

    alpha, the relative fraction of F(X^{n-i}) and X^{n-i} can be set with setAndersonDampingFactor(). Default value is 1 (only F(X^{n-i})).

    The default order (number of previous states considered) is 2. Call setOrder() to change it.

    The convergence criteria is : ||F(X^{n}) - X^{n}|| / ||X^{n+1}|| < tolerance. The default norm used is the infinite norm. Coupler.setNormChoice() allows to choose another one.

    The default value of tolerance is 1.E-6. Call setConvergenceParameters() to change it.

    The default maximum number of iterations is 100. Call setConvergenceParameters() to change it.
    """

    def __init__(self, physics, exchangers, dataManager):
        """! Build a AndersonCoupler object.

        @param physics list of only one PhysicsDriver (possibly a Coupler).
        @param exchangers list of exactly two Exchanger allowing to go from the PhysicsDriver to the DataManager and vice versa.
        @param dataManager list of only one DataManager.
        """
        Coupler.__init__(self, physics, exchangers, dataManager)
        self.tolerance_ = 1.E-6
        self.maxiter_ = 100
        self.order_ = 2
        self.andersonDampingFactor_ = 1.
        self.isConverged_ = False

        if not isinstance(physics, list) or not isinstance(exchangers, list) or not isinstance(dataManager, list):
            raise Exception("AndersonCoupler.__init__ physics, exchangers and dataManager must be lists!")
        if len(physics) != 1:
            raise Exception("AndersonCoupler.__init__ There must be only one PhysicsDriver")
        if len(exchangers) != 2:
            raise Exception("AndersonCoupler.__init__ There must be exactly two Exchanger")
        if len(dataManager) != 1:
            raise Exception("AndersonCoupler.__init__ There must be only one DataManager")

    def setConvergenceParameters(self, tolerance, maxiter):
        """! Set the convergence parameters (tolerance and maximum number of iterations).

        @param tolerance the convergence threshold in ||F(X^{n}) - X^{n}|| / ||X^{n+1}|| < tolerance.
        @param maxiter the maximal number of iterations.
        """
        self.tolerance_ = tolerance
        self.maxiter_ = maxiter

    def setAndersonDampingFactor(self, andersonDampingFactor):
        """! Set the damping factor of the method, the relative contribution of F(X^{k}) and X^{k} on the calculation of next step.

        @param andersonDampingFactor the damping factor alpha in the formula alpha * F(X^{n-i}) + (1. - alpha) * X^{n-i}.
        """
        self.andersonDampingFactor_ = andersonDampingFactor

    def setOrder(self, order):
        """! Set the order of the method.

        @param order order of Anderson method. This is also the number of previous states stored by the algorithm.
        """
        if (order <= 0):
            raise Exception("AndersonCoupler.setOrder Set an order > 0 !")
        self.order_ = order

    def solveTimeStep(self):
        """! Solve a time step using the fixed point algorithm with Anderson acceleration.

        See also c3po.PhysicsDriver.PhysicsDriver.solveTimeStep().
        """
        physics = self.physicsDrivers_[0]
        physics2Data = self.exchangers_[0]
        data2physics = self.exchangers_[1]
        data = self.dataManagers_[0]
        Memory = [0] * (self.order_ + 1)
        diffFiFn = []
        iiter = 0

        # Init On calcul ici l'etat "0"
        print("iteration ", iiter)
        physics.solve()
        physics2Data.exchange()
        previousData = data.clone()
        iiter += 1

        # Premiere iteration non acceleree
        print("iteration ", iiter)
        self.abortTimeStep()
        self.initTimeStep(self.dt_)
        data2physics.exchange()
        physics.solve()
        physics2Data.exchange()
        diffData = data - previousData
        Memory[0] = [previousData.clone(), data.clone(), diffData.clone()]  # [u_0, G(u_0) = u_1, u_1 - u_0]
        previousData.copy(data)

        error = self.getNorm(diffData) / self.getNorm(data)
        print("error : ", error)

        iiter += 1

        while error > self.tolerance_ and iiter < self.maxiter_:
            if iiter == 2:
                print(" -- Anderson Acceleration starts ! ")
            print("iteration ", iiter)

            orderK = min(iiter - 1, self.order_)

            self.abortTimeStep()
            self.initTimeStep(self.dt_)
            data2physics.exchange()
            physics.solve()
            physics2Data.exchange()

            diffData.copy(data)
            diffData -= previousData
            error = self.getNorm(diffData) / self.getNorm(data)

            if error > self.tolerance_:

                if orderK == iiter - 1:
                    Memory[orderK] = [previousData.clone(), data.clone(), diffData.clone()]
                    diffFiFn.append(data.clone())
                else:
                    firstMemory = Memory[0]
                    for i in range(len(Memory) - 1):
                        Memory[i] = Memory[i + 1]
                    Memory[-1] = firstMemory
                    Memory[-1][0].copy(previousData)
                    Memory[-1][1].copy(data)
                    Memory[-1][2].copy(diffData)

                self.andersonAccelerationN(Memory, diffFiFn, data, orderK)
                previousData.copy(data)

            iiter += 1
            print("error : ", error)

        return physics.getSolveStatus() and not(error > self.tolerance_)

    def andersonAccelerationN(self, andersonMemory, diffFiFn, out, localOrder):
        """ INTERNAL """
        A = np.zeros(localOrder * localOrder).reshape(localOrder, localOrder)
        B = np.zeros(localOrder)
        for i in range(localOrder):
            diffFiFn[i].copy(andersonMemory[localOrder][2])
            diffFiFn[i] -= andersonMemory[i][2]
        for i in range(localOrder):
            for j in range(i):
                A[i][j] = diffFiFn[i].dot(diffFiFn[j])
                A[j][i] = A[i][j]
            A[i][i] = diffFiFn[i].dot(diffFiFn[i])
            B[i] = andersonMemory[localOrder][2].dot(diffFiFn[i])
        try:
            coeffs = np.linalg.solve(A, B)
            coeff_K = 1. - coeffs[0]
            out.copy(andersonMemory[0][0])
            out *= (1 - self.andersonDampingFactor_) * coeffs[0]
            out.imuladd(self.andersonDampingFactor_ * coeffs[0], andersonMemory[0][1])
            for i in range(1, localOrder):
                coeff_K -= coeffs[i]
                out.imuladd((1 - self.andersonDampingFactor_) * coeffs[i], andersonMemory[i][0])
                out.imuladd(self.andersonDampingFactor_ * coeffs[i], andersonMemory[i][1])
            out.imuladd((1 - self.andersonDampingFactor_) * coeff_K, andersonMemory[localOrder][0])
            out.imuladd(self.andersonDampingFactor_ * coeff_K, andersonMemory[localOrder][1])
        except np.linalg.LinAlgError:
            print(">>>>> Going to lower order")
            self.andersonAccelerationN(andersonMemory[1:], diffFiFn, out, localOrder - 1)

    # On definit les methodes suivantes pour qu'elles soient vues par Tracer.
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

    def abortTimeStep(self):
        """! See Coupler.abortTimeStep(). """
        Coupler.abortTimeStep(self)


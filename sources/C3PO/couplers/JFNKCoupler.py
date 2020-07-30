# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contains the class JFNKCoupler. """
from __future__ import print_function, division
import math
import numpy as np

from C3PO.coupler import coupler


def solveTriang(A, b):
    """For internal purpose only.

    Solves a triangular linear system."""

    n = b.shape[0]
    resu = np.zeros(shape=(n))
    for i in range(n - 1, -1, -1):
        resu[i] = b[i]
        for j in range(n - 1, i, -1):
            resu[i] -= A[i, j] * resu[j]
        resu[i] /= A[i, i]
    return resu


class JFNKCoupler(coupler):
    """ JFNKCoupler inherits from coupler and proposes a Jacobian-Free Newton Krylov coupling algorithm. This is a Newton algorithm using a Krylov (GMRES) method for the linear system solving.

    The Jacobian matrix is not computed, but the product of the jacobian matrix with a vector v is approximated by a Taylor formula (J_u is the jacobian of F at the point u):

    J_u v ~= (F(u + epsilon v) - F(u))/epsilon

    epsilon is a parameter of the algorithm. Its default value is 1E-4. Call setEpsilon to change it

    JFNKCoupler is a coupler working with precisely :

        - A single physicsDriver (possibly a coupler) defining the calculations to be made each time F is called. 
        - A single dataManager allowing to manipulate the data to be considered in the coupling.
        - Two exchangers allowing to go from the physicsDrivers to the dataManager and vice versa.

    As the Newton algorithm solves for F(X) = 0, in order to be coherent with the fixed point coupling algorithms, F(x) is defined as F(X) = f(X) - X, where f is the output of the physicsDriver.    

    The convergence criteria is : ||f(X^{n}) - X^{n}|| / ||f(X^{n})|| < tolerance. The default norm used is the infinite norm. setNormChoice allows to choose another one.

    The default Newton tolerance is 1.E-6. Call setConvergenceParameters to change it.
    The default maximum Newton number of iterations is 10. Call setConvergenceParameters to change it.
    The default Krylov tolerance is 1.E-4. Call setKrylovConvergenceParameters to change it.
    The default maximum Krylov iteration is 100. Call setKrylovConvergenceParameters to change it.

    """

    def __init__(self, physics, exchangers, dataManager):
        """ Builds a JFNKCoupler object.

        :param physics: list of only one physicsDriver (possibly a coupler).
        :param exchangers: list of exactly two exchangers allowing to go from the physicsDriver to the dataManager and vice versa.
        :param dataManager: list of only one dataManager.

        """
        coupler.__init__(self, physics, exchangers, dataManager)
        self.NewtonTolerance_ = 1.E-6
        self.NewtonMaxIter_ = 10
        self.KrylovTolerance_ = 1.E-4
        self.KrylovMaxIter_ = 100
        self.epsilon_ = 1.E-4
        self.isConverged_ = False

        if len(physics) != 1:
            raise Exception("JFNKCoupler.__init__ There must be only one physicsDriver")
        if len(exchangers) != 2:
            raise Exception("JFNKCoupler.__init__ There must be exactly two exchangers")
        if len(dataManager) != 1:
            raise Exception("JFNKCoupler.__init__ There must be only one dataManager")

    def setConvergenceParameters(self, tolerance, maxiter):
        """ Sets the convergence parameters (tolerance and maximum number of iterations). """
        self.NewtonTolerance_ = tolerance
        self.NewtonMaxIter_ = maxiter

    def setKrylovConvergenceParameters(self, tolerance, maxiter):
        """ Sets the maximum number of iteration of the inner Krylov method. """
        self.KrylovTolerance_ = tolerance
        self.KrylovMaxIter_ = maxiter

    def setEpsilon(self, epsilon):
        """ Sets the epsilon value of the method, used in the formula J_u v ~= (F(u + epsilon v) - F(u))/epsilon. """
        self.epsilon_ = epsilon

    def solveTimeStep(self):
        """ Solves a time step using the fixed point algorithm with Anderson acceleration. """

        physics = self.physicsDrivers_[0]
        physics2Data = self.exchangers_[0]
        data2physics = self.exchangers_[1]
        data = self.dataManagers_[0]
        iterNewton = 0
        iterKrylov = 0
        residual = 0
        previousData = 0
        Q = []

        print("Initialisation ")
        # On calcul ici l'etat "0"
        physics.solve()
        physics2Data.exchange()

        errorNewton = self.NewtonTolerance_ + 1

        while errorNewton > self.NewtonTolerance_ and iterNewton < self.NewtonMaxIter_:
            print("Newton iteration ", iterNewton)

            if iterNewton == 0:
                residual = data.clone()
                previousData = data.clone()
            else:
                residual.copy(data)
                previousData.copy(data)

            self.abortTimeStep()
            self.initTimeStep(self.dt_)
            data2physics.exchange()
            physics.solve()
            physics2Data.exchange()

            residual -= data  # residual is the second member of the linear system: -F(x) = -(f(x)-x)
            Norm2Residual = residual.norm2()

            errorNewton = self.getNorm(residual) / self.getNorm(data)
            if errorNewton > self.NewtonTolerance_:

                if len(Q) < 1:
                    Q.append(residual * (1. / Norm2Residual))
                else:
                    Q[0].copy(residual)
                    Q[0] *= (1. / Norm2Residual)

                H = np.zeros(shape=(1))
                O_transpose = np.zeros(shape=(1, 1))
                O_transpose[0, 0] = 1.
                R = np.zeros(shape=(1, 0))
                KrylovResidual = np.zeros(shape=(1))
                KrylovResidual[0] = Norm2Residual

                errorKrylov = self.KrylovTolerance_ + 1
                iterKrylov = 0

                while errorKrylov > self.KrylovTolerance_ and iterKrylov < self.KrylovMaxIter_:
                    print("    Krylov iteration ", iterKrylov)
                    iterKrylov += 1

                    data.copy(previousData)
                    data.imuladd(self.epsilon_, Q[iterKrylov - 1])

                    self.abortTimeStep()
                    self.initTimeStep(self.dt_)
                    data2physics.exchange()
                    physics.solve()
                    physics2Data.exchange()

                    data -= previousData
                    data.imuladd(-self.epsilon_, Q[iterKrylov - 1])

                    if len(Q) < iterKrylov + 1:
                        Q.append(data + residual)
                    else:
                        Q[iterKrylov].copy(data)
                        Q[iterKrylov] += residual
                    Q[iterKrylov] *= 1. / self.epsilon_

                    for i in range(iterKrylov):
                        H[i] = Q[i].dot(Q[iterKrylov])
                        Q[iterKrylov].imuladd(-H[i], Q[i])
                    H = np.append(H, Q[iterKrylov].norm2())
                    Q[iterKrylov] *= 1. / H[-1]

                    # Ajout des nouvelles ligne/colonne a O
                    tmpO = np.zeros(shape=(O_transpose.shape[0] + 1, O_transpose.shape[1] + 1))
                    tmpO[0:O_transpose.shape[0], 0:O_transpose.shape[1]] += O_transpose
                    O_transpose = tmpO
                    O_transpose[O_transpose.shape[0] - 1, O_transpose.shape[1] - 1] = 1.

                    H = np.dot(O_transpose, H)

                    Rot = np.zeros(shape=(iterKrylov + 1, iterKrylov + 1))
                    for i in range(iterKrylov - 1):
                        Rot[i, i] = 1.
                    normtmp = math.sqrt(H[-2] * H[-2] + H[-1] * H[-1])
                    Rot[iterKrylov - 1, iterKrylov - 1] = H[-2] / normtmp
                    Rot[iterKrylov, iterKrylov] = H[-2] / normtmp
                    Rot[iterKrylov - 1, iterKrylov] = H[-1] / normtmp
                    Rot[iterKrylov, iterKrylov - 1] = -H[-1] / normtmp

                    O_transpose = np.dot(Rot, O_transpose)

                    # Ajout des nouvelles ligne/colonne a R
                    tmpR = np.zeros(shape=(R.shape[0] + 1, R.shape[1] + 1))
                    tmpR[0:R.shape[0], 0:R.shape[1]] += R
                    R = tmpR
                    for i in range(iterKrylov + 1):
                        R[i, R.shape[1] - 1] = H[i]
                    R = np.dot(Rot, R)

                    KrylovResidual = np.append(KrylovResidual, 0.)
                    KrylovResidual = np.dot(Rot, KrylovResidual)

                    errorKrylov = abs(KrylovResidual[-1]) / Norm2Residual

                    print("    error Krylov : ", errorKrylov)

                SquareR = R[0:iterKrylov, 0:iterKrylov]
                ReduceKrylovResidual = KrylovResidual[0:iterKrylov]
                KrylovResu = solveTriang(SquareR, ReduceKrylovResidual)

                data.copy(previousData)
                for i in range(iterKrylov):
                    data.imuladd(KrylovResu[i], Q[i])

            iterNewton += 1
            print("error Newton : ", errorNewton)

        return physics.getSolveStatus() and not(errorNewton > self.NewtonTolerance_)

    #On definit les methodes suivantes pour qu'elles soient vues par tracer.
    def initialize(self):
        return coupler.initialize(self)

    def terminate(self):
        return coupler.terminate(self)

    def computeTimeStep(self):
        return coupler.computeTimeStep(self)

    def initTimeStep(self, dt):
        return coupler.initTimeStep(self, dt)

    def validateTimeStep(self):
        coupler.validateTimeStep(self)

    def abortTimeStep(self):
        coupler.abortTimeStep(self)
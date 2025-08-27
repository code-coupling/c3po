# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class :class:`.JFNKCoupler`. """
from __future__ import print_function, division
import math
import numpy as np

from c3po.Coupler import Coupler
from c3po.CollaborativeDataManager import CollaborativeDataManager
from c3po.services.Printer import Printer


def solveTriang(matrixA, vectorB):
    """ INTERNAL.

    Solves a triangular linear system.
    """
    dim = vectorB.shape[0]
    resu = np.zeros(shape=(dim))
    for i in range(dim - 1, -1, -1):
        resu[i] = vectorB[i]
        for j in range(dim - 1, i, -1):
            resu[i] -= matrixA[i, j] * resu[j]
        resu[i] /= matrixA[i, i]
    return resu


class JFNKCoupler(Coupler):
    """ :class:`.JFNKCoupler` inherits from :class:`.Coupler` and proposes a Jacobian-Free Newton
    Krylov coupling algorithm.

    This is a Newton algorithm using a Krylov (GMRES) method for the linear system solving.

    The Jacobian matrix is not computed, but the product of the jacobian matrix with a vector
    :math:`v` is approximated by a Taylor formula (:math:`J_u` is the jacobian of :math:`F` at the
    point :math:`u`):

    .. math::

        J_u v \\approx (F(u + \\varepsilon v) - F(u))/\\varepsilon

    :math:`\\varepsilon` is a parameter of the algorithm. Its default value is 1E-4. Call
    :meth:`setEpsilon` to change it

    JFNKCoupler is a Coupler working with :

    - A single :class:`.PhysicsDriver` (possibly a Coupler) defining the calculations to be made
      each time :math:`F` is called.
    - A list of :class:`.DataManager` allowing to manipulate the data in the coupling.
    - Two :class:`.Exchanger` allowing to go from the :class:`.PhysicsDriver` to the
      :class:`.DataManager` and vice versa.

    Each :class:`.DataManager` is normalized with its own norm got after the first iteration.
    They are then used as a single :class:`.DataManager| using :class:`.CollaborativeDataManager`.

    As the Newton algorithm solves for :math:`F(X) = 0`, in order to be coherent with the fixed point
    coupling algorithms, :math:`F(x)` is defined as :math:`F(X) = f(X) - X`, where :math:`f` is
    the output of the physicsDriver.

    The convergence criteria is : :math:`||f(X^{n}) - X^{n}|| / ||f(X^{n})|| < \\rm{tolerance}`.
    The default norm used is the infinite norm. :meth:`.Coupler.setNormChoice` allows to choose
    another one.

    The default Newton tolerance is 1.E-6. Call :meth:`setConvergenceParameters` to change it.

    The default maximum Newton number of iterations is 10. Call :meth:`setConvergenceParameters` to
    change it.

    The default Krylov tolerance is 1.E-4. Call :meth:`setKrylovConvergenceParameters` to change it.

    The default maximum Krylov iteration is 100. Call :meth:`setKrylovConvergenceParameters` to
    change it.

    """

    def __init__(self, physics, exchangers, dataManagers):
        """ Build a :class:`.JFNKCoupler` object.

        Parameters
        ----------
        physics : list[PhysicsDriver]
            List of only one :class:`.PhysicsDriver` (possibly a :class:`.Coupler`).
        exchangers : list[Exchanger]
            List of exactly two :class:`.Exchanger` allowing to go from the :class:`.PhysicsDriver`
            to the :class:`.DataManager` and vice versa.
        dataManagers : list[DataManager]
            List of :class:`.DataManager`.
        """
        Coupler.__init__(self, physics, exchangers, dataManagers)
        self._newtonTolerance = 1.E-6
        self._newtonMaxIter = 10
        self._krylovTolerance = 1.E-4
        self._krylovMaxIter = 100
        self._epsilon = 1.E-4
        self._iterationPrinter = Printer(2)
        self._leaveIfFailed = False

        if not isinstance(physics, list) or not isinstance(exchangers, list) or not isinstance(dataManagers, list):
            raise Exception("JFNKCoupler.__init__ physics, exchangers and dataManagers must be lists!")
        if len(physics) != 1:
            raise Exception("JFNKCoupler.__init__ There must be only one PhysicsDriver")
        if len(exchangers) != 2:
            raise Exception("JFNKCoupler.__init__ There must be exactly two Exchanger")

    def setConvergenceParameters(self, tolerance, maxiter):
        """ Set the convergence parameters (tolerance and maximum number of iterations).

        Parameters
        ----------
        tolerance
            The convergence threshold in
            :math:`||f(X^{n}) - X^{n}|| / ||f(X^{n})|| < \\rm{tolerance}`.
        maxiter
            The maximal number of iterations.
        """
        self._newtonTolerance = tolerance
        self._newtonMaxIter = maxiter

    def setKrylovConvergenceParameters(self, tolerance, maxiter):
        """ Set the convergence parameters (tolerance and maximum number of iterations) of the
        Krylov method.

        Parameters
        ----------
        tolerance
            The convergence threshold of the Krylov method.
        maxiter
            The maximal number of iterations of the Krylov method.
        """
        self._krylovTolerance = tolerance
        self._krylovMaxIter = maxiter

    def setEpsilon(self, epsilon):
        """ Set the ``epsilon`` value of the method.

        Parameters
        ----------
        epsilon
            The ``epsilon`` value in the formula :math:`J_u v \\approx (F(u + \\varepsilon v) -
            F(u))/\\varepsilon`.
        """
        self._epsilon = epsilon

    def setPrintLevel(self, level):
        """ Set the print level during iterations (0=None, 1 keeps last iteration, 2 prints every iteration).

        Parameters
        ----------
        level : int
            Integer in range [0;2]. Default: 2.
        """
        if not level in [0, 1, 2]:
            raise Exception("JFNKCoupler.setPrintLevel level should be one of [0, 1, 2]!")
        self._iterationPrinter.setPrintLevel(level)

    def setFailureManagement(self, leaveIfSolvingFailed):
        """ Set if iterations should continue or not in case of solver failure
        (:meth:`solveTimeStep` returns False).

        Parameters
        ----------
        leaveIfSolvingFailed : bool
            Set False to continue the iterations, True to stop. Default: False.
        """
        self._leaveIfFailed = leaveIfSolvingFailed

    def solveTimeStep(self):
        """ Solve a time step using Jacobian-Free Newton Krylov algorithm.

        See also :meth:`c3po.PhysicsDriver.PhysicsDriver.solveTimeStep`.
        """
        physics = self._physicsDrivers[0]
        physics2Data = self._exchangers[0]
        data2physics = self._exchangers[1]
        iterNewton = 0
        iterKrylov = 0
        residual = 0
        previousData = 0
        matrixQ = []

        # On calcul ici l'etat "0"
        physics.solve()
        if self._leaveIfFailed and not physics.getSolveStatus():
            return False
        physics2Data.exchange()

        data = CollaborativeDataManager(self._dataManagers)
        normData = self.readNormData()
        self.normalizeData(normData)

        errorNewton = self._newtonTolerance + 1

        while errorNewton > self._newtonTolerance and iterNewton < self._newtonMaxIter:
            if iterNewton == 0:
                residual = data.clone()
                previousData = data.clone()
            else:
                residual.copy(data)
                previousData.copy(data)

            self.abortTimeStep()
            self.initTimeStep(self._dt)
            self.denormalizeData(normData)
            data2physics.exchange()
            physics.solve()
            if self._leaveIfFailed and not physics.getSolveStatus():
                return False
            physics2Data.exchange()
            self.normalizeData(normData)

            residual -= data  # residual is the second member of the linear system: -F(x) = -(f(x)-x)
            norm2Residual = residual.norm2()

            errorNewton = self.getNorm(residual) / self.getNorm(data)

            if self._iterationPrinter.getPrintLevel() > 0:
                self._iterationPrinter.print("JFNK Newton iteration {} initial error : {:.5e}".format(iterNewton, errorNewton))

            if errorNewton > self._newtonTolerance:

                if len(matrixQ) < 1:
                    matrixQ.append(residual * (1. / norm2Residual))
                else:
                    matrixQ[0].copy(residual)
                    matrixQ[0] *= (1. / norm2Residual)

                vectorH = np.zeros(shape=(1))
                transposeO = np.zeros(shape=(1, 1))
                transposeO[0, 0] = 1.
                matrixR = np.zeros(shape=(1, 0))
                krylovResidual = np.zeros(shape=(1))
                krylovResidual[0] = norm2Residual

                errorKrylov = self._krylovTolerance + 1
                iterKrylov = 0

                while errorKrylov > self._krylovTolerance and iterKrylov < self._krylovMaxIter:
                    iterKrylov += 1

                    data.copy(previousData)
                    data.imuladd(self._epsilon, matrixQ[iterKrylov - 1])

                    self.abortTimeStep()
                    self.initTimeStep(self._dt)
                    self.denormalizeData(normData)
                    data2physics.exchange()
                    physics.solve()
                    if self._leaveIfFailed and not physics.getSolveStatus():
                        return False
                    physics2Data.exchange()
                    self.normalizeData(normData)

                    data -= previousData
                    data.imuladd(-self._epsilon, matrixQ[iterKrylov - 1])

                    if len(matrixQ) < iterKrylov + 1:
                        matrixQ.append(data + residual)
                    else:
                        matrixQ[iterKrylov].copy(data)
                        matrixQ[iterKrylov] += residual
                    matrixQ[iterKrylov] *= 1. / self._epsilon

                    for i in range(iterKrylov):
                        vectorH[i] = matrixQ[i].dot(matrixQ[iterKrylov])
                        matrixQ[iterKrylov].imuladd(-vectorH[i], matrixQ[i])
                    vectorH = np.append(vectorH, matrixQ[iterKrylov].norm2())
                    matrixQ[iterKrylov] *= 1. / vectorH[-1]

                    # Ajout des nouvelles ligne/colonne a O
                    tmpO = np.zeros(shape=(transposeO.shape[0] + 1, transposeO.shape[1] + 1))
                    tmpO[0:transposeO.shape[0], 0:transposeO.shape[1]] += transposeO
                    transposeO = tmpO
                    transposeO[transposeO.shape[0] - 1, transposeO.shape[1] - 1] = 1.

                    vectorH = np.dot(transposeO, vectorH)

                    rot = np.zeros(shape=(iterKrylov + 1, iterKrylov + 1))
                    for i in range(iterKrylov - 1):
                        rot[i, i] = 1.
                    normtmp = math.sqrt(vectorH[-2] * vectorH[-2] + vectorH[-1] * vectorH[-1])
                    rot[iterKrylov - 1, iterKrylov - 1] = vectorH[-2] / normtmp
                    rot[iterKrylov, iterKrylov] = vectorH[-2] / normtmp
                    rot[iterKrylov - 1, iterKrylov] = vectorH[-1] / normtmp
                    rot[iterKrylov, iterKrylov - 1] = -vectorH[-1] / normtmp

                    transposeO = np.dot(rot, transposeO)

                    # Ajout des nouvelles ligne/colonne a matrixR
                    tmpR = np.zeros(shape=(matrixR.shape[0] + 1, matrixR.shape[1] + 1))
                    tmpR[0:matrixR.shape[0], 0:matrixR.shape[1]] += matrixR
                    matrixR = tmpR
                    for i in range(iterKrylov + 1):
                        matrixR[i, matrixR.shape[1] - 1] = vectorH[i]
                    matrixR = np.dot(rot, matrixR)

                    krylovResidual = np.append(krylovResidual, 0.)
                    krylovResidual = np.dot(rot, krylovResidual)

                    errorKrylov = abs(krylovResidual[-1]) / norm2Residual

                    if self._iterationPrinter.getPrintLevel() > 0:
                        self._iterationPrinter.print("    JFNK Krylov iteration {} error : {:.5e}".format(iterKrylov - 1, errorKrylov))

                squareR = matrixR[0:iterKrylov, 0:iterKrylov]
                reduceKrylovResidual = krylovResidual[0:iterKrylov]
                krylovResu = solveTriang(squareR, reduceKrylovResidual)

                data.copy(previousData)
                for i in range(iterKrylov):
                    data.imuladd(krylovResu[i], matrixQ[i])

            iterNewton += 1

        if self._iterationPrinter.getPrintLevel() == 1:
            self._iterationPrinter.reprint(tmplevel=2)

        self.denormalizeData(normData)
        return physics.getSolveStatus() and errorNewton <= self._newtonTolerance

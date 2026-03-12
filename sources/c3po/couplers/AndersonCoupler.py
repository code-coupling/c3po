# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class :class:`.AndersonCoupler`. """
from __future__ import print_function, division
import math
import numpy as np

from c3po.PhysicsDriver import PhysicsDriver
from c3po.Coupler import Coupler
from c3po.CollaborativeDataManager import CollaborativeDataManager
from c3po.services.Printer import Printer


def deleteQRColumn(matrixQ, matrixR, dataTemp):
    """ INTERNAL

    Returns
    -------

        A new QR decomposition after deletion of one column.
    """
    dim = matrixR.shape[0]
    for i in range(dim - 1):
        temp = math.sqrt(matrixR[i, i + 1] * matrixR[i, i + 1] + matrixR[i + 1, i + 1] * matrixR[i + 1, i + 1])
        cval = matrixR[i, i + 1] / temp
        sval = matrixR[i + 1, i + 1] / temp
        matrixR[i, i + 1] = temp
        matrixR[i + 1, i + 1] = 0.
        for j in range(i + 2, dim):
            temp = cval * matrixR[i, j] + sval * matrixR[i + 1, j]
            matrixR[i + 1, j] = -sval * matrixR[i, j] + cval * matrixR[i + 1, j]
            matrixR[i, j] = temp
        dataTemp.copy(matrixQ[i])
        dataTemp *= cval
        dataTemp.imuladd(sval, matrixQ[i + 1])
        matrixQ[i + 1] *= cval
        matrixQ[i + 1].imuladd(-sval, matrixQ[i])
        matrixQ[i].copy(dataTemp)
    matrixR = matrixR[:dim - 1, 1:].copy()
    return matrixQ, matrixR


class AndersonCoupler(Coupler):
    """ :class:`.AndersonCoupler` inherits from :class:`.Coupler` and proposes a fixed point
    algorithm with Anderson acceleration.

    A QR decomposition is used for the optimization problem.

    The class proposes an algorithm for the resolution of :math:`F(X) = X`. Thus
    :class:`.AndersonCoupler` is a :class:`.Coupler` working with :

    - A single :class:`.PhysicsDriver` (possibly a :class:`.Coupler`) defining the calculations to
      be made each time :math:`F` is called.
    - A list of :class:`.DataManager` allowing to manipulate the data in the coupling (the :math:`X`).
    - Two :class:`.Exchanger` allowing to go from the :class:`.PhysicsDriver` to the
      :class:`.DataManager` and vice versa.

    Each :class:`.DataManager` is normalized with its own norm got after the first iteration.
    They are then used as a single :class:`.DataManager` using :class:`.CollaborativeDataManager`.

    The first two iterations just do (with :math:`n` the iteration number):

    .. math::

        X^{n+1} = F(X^{n})

    Then the Anderson acceleration starts and computes :math:`X^{n+1}` as a linear combination of
    :math:`[\\alpha.F(X^{n-i}) + (1. - \\alpha).X^{n-i}]`.

    :math:`\\alpha`, the relative fraction of :math:`F(X^{n-i})` and :math:`X^{n-i}` can be set with
    :meth:`setAndersonDampingFactor`. Default value is 1 (only :math:`F(X^{n-i})`).

    The default order (number of previous states considered) is 2. Call :meth:`setOrder` to change it.

    The convergence criteria is : :math:`||F(X^{n}) - X^{n}|| / ||F(X^{n})|| < \\rm{tolerance}`. The default
    norm used is the infinite norm. :meth:`.Coupler.setNormChoice` allows to choose another one.

    The default value of tolerance is 1.E-6. Call :meth:`setConvergenceParameters` to change it.

    The default maximum number of iterations is 100. Call :meth:`setConvergenceParameters` to
    change it.

    """

    def __init__(self, physics, exchangers, dataManagers):
        """ Build a :class:`.AndersonCoupler` object.

        Parameters
        ----------
        physics : list[PhysicsDriver], list[Coupler]
            List of only one :class:`.PhysicsDriver` (possibly a :class:`.Coupler`).
        exchangers : list[Exchanger]
            List of exactly two :class:`.Exchanger` allowing to go from the :class:`.PhysicsDriver`
            to the :class:`.DataManager` and vice versa.
        dataManagers : list[DataManager]
            List of :class:`.DataManager`.
        """
        Coupler.__init__(self, physics, exchangers, dataManagers)
        self._tolerance = 1.E-6
        self._maxiter = 100
        self._order = 2
        self._andersonDampingFactor = 1.
        self._iterationPrinter = Printer(2)
        self._leaveIfFailed = False

        if not isinstance(physics, list) or not isinstance(exchangers, list) or not isinstance(dataManagers, list):
            raise Exception("AndersonCoupler.__init__ physics, exchangers and dataManagers must be lists!")
        if len(physics) != 1:
            raise Exception("AndersonCoupler.__init__ There must be only one PhysicsDriver")
        if len(exchangers) != 2:
            raise Exception("AndersonCoupler.__init__ There must be exactly two Exchanger")

    def setConvergenceParameters(self, tolerance, maxiter):
        """ Set the convergence parameters (``tolerance`` and maximum number of iterations).

        Parameters
        ----------
        tolerance
            The convergence threshold in
            :math:`||F(X^{n}) - X^{n}|| / ||X^{n+1}|| < \\rm{tolerance}`.
        maxiter
            The maximal number of iterations.
        """
        self._tolerance = tolerance
        self._maxiter = maxiter

    def setAndersonDampingFactor(self, andersonDampingFactor):
        """ Set the damping factor of the method, the relative contribution of :math:`F(X^{k})` and
        :math:`X^{k}` on the calculation of next step.

        Parameters
        ----------
        andersonDampingFactor
            The damping factor :math:`\\alpha` in the formula
            :math:`\\alpha.F(X^{n-i}) + (1. - \\alpha).X^{n-i}`.
        """
        if andersonDampingFactor <= 0 or andersonDampingFactor > 1:
            raise Exception("AndersonCoupler.setAndersonDampingFactor Set a damping factor > 0 and <=1 !")
        self._andersonDampingFactor = andersonDampingFactor

    def setOrder(self, order):
        """ Set the order of the method.

        Parameters
        ----------
        order
            Order of Anderson method. This is also the number of previous states stored by the algorithm.
        """
        if order <= 0:
            raise Exception("AndersonCoupler.setOrder Set an order > 0 !")
        self._order = order

    def setPrintLevel(self, level):
        """ Set the print level during iterations (0=None, 1 keeps last iteration, 2 prints every iteration).

        Parameters
        ----------
        level : int
            Integer in range ``[0;2]``. Default: 2.
        """
        if not level in [0, 1, 2]:
            raise Exception("AndersonCoupler.setPrintLevel level should be one of [0, 1, 2]!")
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
        """ Solve a time step using the fixed point algorithm with Anderson acceleration.

        Inspire de Homer Walker (walker@wpi.edu), 10/14/2011.

        See also :meth:`c3po.PhysicsDriver.PhysicsDriver.solveTimeStep`.
        """
        physics = self._physicsDrivers[0]
        physics2Data = self._exchangers[0]
        data2physics = self._exchangers[1]
        iiter = 0
        # Compteur de la mémoire d'Anderson : nombre de résidus sauvegardés
        mAA = 0
        # Historique des dF
        memory = [0] * self._order
        iFirstMemory = 0  # permet de ne pas considerer les premiers elements de memory lorsque le conditionnement est mauvais.
        matrixR = np.zeros(shape=(1, 1))
        matrixQ = [0.] * self._order
        datatmp = 0.  # pour manipulation dans deleteQRColumn
        # Tolérance sur le conditionnement de matrixR ; valeur par défaut proposée par Ansar, reprise telle quelle
        dropErr = 1.e10

        # Init On calcul ici l'etat "0"
        if self._iterationPrinter.getPrintLevel() > 0:
            self._iterationPrinter.print("Anderson iteration {} ".format(iiter))

        physics.solve()
        if self._leaveIfFailed and not physics.getSolveStatus():
            return False

        physics2Data.exchange()

        data = CollaborativeDataManager(self._dataManagers)
        normData = self.readNormData()
        self.normalizeData(normData)

        previousData = data.clone()
        iiter += 1

        # Premiere iteration non acceleree
        self.abortTimeStep()
        self.initTimeStep(self._dt)
        self.denormalizeData(normData)
        data2physics.exchange()
        physics.solve()
        if self._leaveIfFailed and not physics.getSolveStatus():
            return False
        physics2Data.exchange()
        self.normalizeData(normData)
        diffData = data - previousData
        previousData.copy(data)

        deltaF = diffData * -1.
        delta = previousData * -1.

        error = self.getNorm(diffData) / self.getNorm(data)

        iiter += 1
        if self._iterationPrinter.getPrintLevel() > 0:
            self._iterationPrinter.print("Anderson iteration {} error : {:.5e} ".format(iiter - 1, error))

        while error > self._tolerance and iiter < self._maxiter:
            self.abortTimeStep()
            self.initTimeStep(self._dt)
            self.denormalizeData(normData)
            data2physics.exchange()
            physics.solve()
            if self._leaveIfFailed and not physics.getSolveStatus():
                return False
            physics2Data.exchange()     # data contient g(u_k), previousData contient u_k
            self.normalizeData(normData)

            diffData.copy(data)
            diffData -= previousData
            error = self.getNorm(diffData) / self.getNorm(data)

            if error > self._tolerance:

                deltaF += diffData  # F_i - F_{i-1}
                delta += data   # f(x_i) - f(x_{i-1})

                # Selon si on a atteint l'ordre m ou non, on ajoute le nouveau résidu ou bien on enlève la première colonne
                # et on rajoute le nouveau à la fin
                if iFirstMemory + mAA < len(memory):
                    memory[iFirstMemory + mAA] = delta.clone()
                else:
                    firstMemory = memory[0]
                    for i in range(len(memory) - 1):
                        memory[i] = memory[i + 1]
                    memory[-1] = firstMemory
                    memory[-1].copy(delta)
                    if iFirstMemory > 0:
                        iFirstMemory -= 1
                mAA += 1

                if mAA > self._order:
                    # Si la dimension est deja self._order, on a atteint la taille max : on retire la première colonne
                    # et on met à jour la décomposition en conséquence
                    if datatmp == 0.:
                        datatmp = data.clone()
                    matrixQ, matrixR = deleteQRColumn(matrixQ, matrixR, datatmp)
                    # La taille de la matrice matrixQ a diminué : on met à jour mAA
                    mAA -= 1

                # Ajout de la nouvelle colonne à matrixQ et matrixR,
                if matrixR.shape[0] != mAA:
                    tmpR = np.zeros(shape=(mAA, mAA))
                    tmpR[0:matrixR.shape[0], 0:matrixR.shape[1]] += matrixR
                    matrixR = tmpR

                for j in range(mAA - 1):
                    val = matrixQ[j].dot(deltaF)
                    matrixR[j, mAA - 1] = val
                    deltaF.imuladd(-val, matrixQ[j])
                matrixR[mAA - 1, mAA - 1] = deltaF.norm2()
                facteurmult = 1.
                if matrixR[mAA - 1, mAA - 1] != 0:
                    facteurmult = 1. / matrixR[mAA - 1, mAA - 1]
                if matrixQ[mAA - 1] == 0.:
                    matrixQ[mAA - 1] = deltaF * facteurmult
                else:
                    matrixQ[mAA - 1].copy(deltaF)
                    matrixQ[mAA - 1] *= facteurmult

                # On prepare l'iteration suivante.
                delta.copy(data)
                delta *= -1.
                deltaF.copy(diffData)
                deltaF *= -1.

                # Condition Control : en cas de mauvais conditionnement de memory : on peut contrôler ça avec le conditionnement de matrixR
                # En cas de mauvais conditionnement, on met à jour matrixQ et matrixR c'est à dire qu'on supprime la première colonne de memory (avec iFirstMemory)
                if dropErr > 0.:
                    condDF = np.linalg.cond(matrixR)
                    while condDF > dropErr and mAA > 1:
                        # print("cond(D) = %1.8e, reducing mAA to %d" % (condDF, mAA - 1))
                        if datatmp == 0.:
                            datatmp = data.clone()
                        matrixQ, matrixR = deleteQRColumn(matrixQ, matrixR, datatmp)
                        iFirstMemory += 1
                        mAA -= 1
                        condDF = np.linalg.cond(matrixR)
                # On résout le problème de minimisation : on calcule dans un premier temps matrixQ^T F
                matrixQF = np.zeros(mAA)
                for i in range(mAA):
                    matrixQF[i] = matrixQ[i].dot(diffData)
                # Puis on résoud le système triangulaire : matrixR gamma = matrixQF pour obtenir les coefficients d'Anderson
                gamma = np.linalg.lstsq(matrixR, matrixQF, rcond=-1)[0]

                # On calcule memory * gamma pour ensuite calculer le nouveau data
                for i in range(mAA):
                    data.imuladd(-gamma[i], memory[iFirstMemory + i])

                if self._andersonDampingFactor != 1.:
                    matrixRgamma = np.dot(matrixR, gamma)
                    data.imuladd(-(1. - self._andersonDampingFactor), diffData)
                    for i in range(mAA):
                        data.imuladd((1. - self._andersonDampingFactor) * matrixRgamma[i], matrixQ[i])

                previousData.copy(data)

            iiter += 1
            if self._iterationPrinter.getPrintLevel() > 0:
                self._iterationPrinter.print("Anderson iteration {} error : {:.5e} ".format(iiter - 1, error))

        if self._iterationPrinter.getPrintLevel() == 1:
            self._iterationPrinter.reprint(tmplevel=2)

        self.denormalizeData(normData)
        return physics.getSolveStatus() and error <= self._tolerance

    def getSolveStatus(self):
        """ See :meth:`.PhysicsDriver.getSolveStatus`. """
        return PhysicsDriver.getSolveStatus(self)

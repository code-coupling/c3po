# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contains the class AndersonQRCoupler. """
from __future__ import print_function, division
import math
import numpy as np

from C3PO.Coupler import Coupler

from numpy import array, linspace, sqrt, sin, zeros
from numpy.linalg import norm


def deleteQRColumn(Q, R, dataTemp):
    """For internal purpose only.

    Return a new QR decomposition after deletion of one column."""
    m = R.shape[0]
    for i in range(m - 1):
        temp = math.sqrt(R[i, i + 1] * R[i, i + 1] + R[i + 1, i + 1] * R[i + 1, i + 1])
        c = R[i, i + 1] / temp
        s = R[i + 1, i + 1] / temp
        R[i, i + 1] = temp
        R[i + 1, i + 1] = 0.
        for j in range(i + 2, m):
            temp = c * R[i, j] + s * R[i + 1, j]
            R[i + 1, j] = -s * R[i, j] + c * R[i + 1, j]
            R[i, j] = temp
        dataTemp.copy(Q[i])
        dataTemp *= c
        dataTemp.imuladd(s, Q[i + 1])
        Q[i + 1] *= c
        Q[i + 1].imuladd(-s, Q[i])
        Q[i].copy(dataTemp)
    R = R[:m - 1, 1:].copy()
    return Q, R


class AndersonQRCoupler(Coupler):
    """ AndersonQRCoupler inherits from Coupler and proposes a fixed point algorithm with Anderson acceleration (and a special solving method of the internal optimization problem). 

    The class proposes an algorithm for the resolution of F(X) = X. Thus AndersonCoupler is a Coupler working with precisely :

        - A single PhysicsDriver (possibly a Coupler) defining the calculations to be made each time F is called.
        - A single DataManager allowing to manipulate the data to be damped in the coupling (the X).
        - Two Exchanger allowing to go from the PhysicsDriver to the DataManager and vice versa.

    The first two iterations just do (with n the iteration number):

        X^{n+1} = F(X^{n})

    Then the Anderson acceleration starts and computes X^{n+1} as a linear combination of [alpha * F(X^{n-i}) + (1. - alpha) * X^{n-i}]. 

    alpha, the relative fraction of F(X^{n-i}) and X^{n-i} can be set with setAndersonDampingFactor. Default value is 1 (only F(X^{n-i})).

    The default order (number of previous states considered) is 2. Call setOrder to change it.

    The convergence criteria is : ||F(X^{n}) - X^{n}|| / ||F(X^{n})|| < tolerance. The default norm used is the infinite norm. setNormChoice allows to choose another one.

    The default value of tolerance is 1.E-6. Call setConvergenceParameters to change it.
    The default maximum number of iterations is 100. Call setConvergenceParameters to change it.

    """

    def __init__(self, physics, exchangers, dataManager):
        """ Builds a AndersonQRCoupler object.

        :param physics: list of only one PhysicsDriver (possibly a Coupler).
        :param exchangers: list of exactly two Exchanger allowing to go from the PhysicsDriver to the DataManager and vice versa.
        :param dataManager: list of only one DataManager.

        """
        Coupler.__init__(self, physics, exchangers, dataManager)
        self.tolerance_ = 1.E-6
        self.maxiter_ = 100
        self.order_ = 2
        self.andersonDampingFactor_ = 1.
        self.isConverged_ = False

        if not isinstance(physics, list) or not isinstance(exchangers, list) or not isinstance(dataManager, list):
            raise Exception("AndersonQRCoupler.__init__ physics, exchangers and dataManager must be lists!")
        if len(physics) != 1:
            raise Exception("AndersonQRCoupler.__init__ There must be only one PhysicsDriver")
        if len(exchangers) != 2:
            raise Exception("AndersonQRCoupler.__init__ There must be exactly two Exchanger")
        if len(dataManager) != 1:
            raise Exception("AndersonQRCoupler.__init__ There must be only one DataManager")

    def setConvergenceParameters(self, tolerance, maxiter):
        """ Sets the convergence parameters (tolerance and maximum number of iterations). """
        self.tolerance_ = tolerance
        self.maxiter_ = maxiter

    def setAndersonDampingFactor(self, andersonDampingFactor):
        """ Sets the damping factor of the method, the relative contribution of F(X^{k}) and X^{k} on the calculation of next step. """
        if andersonDampingFactor <= 0 or andersonDampingFactor > 1:
            raise Exception("AndersonQRCoupler.setAndersonDampingFactor Set a damping factor > 0 and <=1 !")
        self.andersonDampingFactor_ = andersonDampingFactor

    def setOrder(self, order):
        """ Sets the order of the method, the number of previous states considered. """
        if (order <= 0):
            raise Exception("AndersonQRCoupler.setOrder Set an order > 0 !")
        self.order_ = order

    def solveTimeStep(self):
        """ Solves a time step using the fixed point algorithm with Anderson acceleration. """

      # Inspiré de Homer Walker (walker@wpi.edu), 10/14/2011.
        physics = self.physicsDrivers_[0]
        physics2Data = self.exchangers_[0]
        data2physics = self.exchangers_[1]
        data = self.dataManagers_[0]
        iiter = 0
        # Compteur de la mémoire d'Anderson : nombre de résidus sauvegardés
        mAA = 0
        # Historique des dF
        Memory = [0] * self.order_
        iFirstMemory = 0  # permet de ne pas considerer les premiers elements de Memory lorsque le conditionnement est mauvais.
        R = np.zeros(shape=(1, 1))
        Q = [0.] * self.order_
        datatmp = 0.  # pour manipulation dans deleteQRColumn
        # Tolérance sur le conditionnement de R ; valeur par défaut proposée par Ansar, reprise telle quelle
        dropErr = 1.e10

        print("Initialisation ")
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
        previousData.copy(data)

        df = diffData * -1.
        delta = previousData * -1.

        error = self.getNorm(diffData) / self.getNorm(data)
        print("error : ", error)

        iiter += 1

        while error > self.tolerance_ and iiter < self.maxiter_:
            if iiter == 2:
                print(" -- Anderson Acceleration starts ! ")
            print("iteration ", iiter)

            self.abortTimeStep()
            self.initTimeStep(self.dt_)
            data2physics.exchange()
            physics.solve()
            physics2Data.exchange()     # data contient g(u_k), previousData contient u_k

            diffData.copy(data)
            diffData -= previousData
            error = self.getNorm(diffData) / self.getNorm(data)

            if error > self.tolerance_:

                df += diffData  # F_i - F_{i-1}
                delta += data   # f(x_i) - f(x_{i-1})

                # Selon si on a atteint l'ordre m ou non, on ajoute le nouveau résidu ou bien on enlève la première colonne
                # et on rajoute le nouveau à la fin
                if iFirstMemory + mAA < len(Memory):
                    Memory[iFirstMemory + mAA] = delta.clone()
                else:
                    firstMemory = Memory[0]
                    for i in range(len(Memory) - 1):
                        Memory[i] = Memory[i + 1]
                    Memory[-1] = firstMemory
                    Memory[-1].copy(delta)
                    if iFirstMemory > 0:
                        iFirstMemory -= 1
                mAA += 1

                if mAA > self.order_:
                    # Si la dimension est deja self.order_, on a atteint la taille max : on retire la première colonne
                    # et on met à jour la décomposition en conséquence
                    if datatmp == 0.:
                        datatmp = data.clone()
                    Q, R = deleteQRColumn(Q, R, datatmp)
                    # La taille de la matrice Q a diminué : on met à jour mAA
                    mAA -= 1

                # Ajout de la nouvelle colonne à Q et R,
                if R.shape[0] != mAA:
                    tmpR = np.zeros(shape=(mAA, mAA))
                    tmpR[0:R.shape[0], 0:R.shape[1]] += R
                    R = tmpR

                for j in range(mAA - 1):
                    val = Q[j].dot(df)
                    R[j, mAA - 1] = val
                    df.imuladd(-val, Q[j])
                R[mAA - 1, mAA - 1] = df.norm2()
                facteurmult = 1.
                if R[mAA - 1, mAA - 1] != 0:
                    facteurmult = 1. / R[mAA - 1, mAA - 1]
                if Q[mAA - 1] == 0.:
                    Q[mAA - 1] = df * facteurmult
                else:
                    Q[mAA - 1].copy(df)
                    Q[mAA - 1] *= facteurmult

                # On prepare l'iteration suivante.
                delta.copy(data)
                delta *= -1.
                df.copy(diffData)
                df *= -1.

                # Condition Control : en cas de mauvais conditionnement de Memory : on peut contrôler ça avec le conditionnement de R
                # En cas de mauvais conditionnement, on met à jour Q et R c'est à dire qu'on supprime la première colonne de Memory (avec iFirstMemory)
                if dropErr > 0.:
                    condDF = np.linalg.cond(R)
                    while condDF > dropErr and mAA > 1:
                        print("cond(D) = %1.8e, reducing mAA to %d" % (condDF, mAA - 1))
                        if datatmp == 0.:
                            datatmp = data.clone()
                        Q, R = deleteQRColumn(Q, R, datatmp)
                        iFirstMemory += 1
                        mAA -= 1
                        condDF = np.linalg.cond(R)
                # On résout le problème de minimisation : on calcule dans un premier temps Q^T F
                QF = np.zeros(mAA)
                for i in range(mAA):
                    QF[i] = Q[i].dot(diffData)
                # Puis on résoud le système triangulaire : R gamma = QF pour obtenir les coefficients d'Anderson
                gamma = np.linalg.lstsq(R, QF, rcond=-1)[0]

                # On calcule Memory * gamma pour ensuite calculer le nouveau data
                for i in range(mAA):
                    data.imuladd(-gamma[i], Memory[iFirstMemory + i])

                if self.andersonDampingFactor_ != 1.:
                    Rgamma = np.dot(R, gamma)
                    data.imuladd(-(1. - self.andersonDampingFactor_), diffData)
                    for i in range(mAA):
                        data.imuladd((1. - self.andersonDampingFactor_) * Rgamma[i], Q[i])

                previousData.copy(data)

            iiter += 1
            print("error : ", error)

        return physics.getSolveStatus() and not(error > self.tolerance_)

    # On definit les methodes suivantes pour qu'elles soient vues par Tracer.
    def initialize(self):
        return Coupler.initialize(self)

    def terminate(self):
        return Coupler.terminate(self)

    def computeTimeStep(self):
        return Coupler.computeTimeStep(self)

    def initTimeStep(self, dt):
        return Coupler.initTimeStep(self, dt)

    def validateTimeStep(self):
        Coupler.validateTimeStep(self)

    def abortTimeStep(self):
        Coupler.abortTimeStep(self)

# -*- coding: utf-8 -*-
from __future__ import print_function, division
import numpy as np

from c3po.PhysicsDriver import PhysicsDriver


class PlaquePhysicsDriver(PhysicsDriver):

    constanteSteph_ = 0.0000001

    @classmethod
    def AssembleMatGen2d(cls, nombreNoeudsX, c, e, f):
        """ Fonction pour creer une matrice identite, une matrice avec une diagonale de valeur "f", et une matrice tridiagonale de taille nombreNoeudsX avec c sur la diagonale et e sur les diagonales sup et inf. """
        Id = np.eye(nombreNoeudsX)
        upAndBotDiag = np.eye(nombreNoeudsX) * f
        diagMat = cls.AssembleMatGen1d(nombreNoeudsX, c, e)
        return Id, upAndBotDiag, diagMat

    @staticmethod
    def AssembleMatGen1d(d, alpha, beta):
        """ Fonction pour construire matrice tridiagonale de taille d avec alpha sur la diagonale et beta sur les diagonales sup et inf. """
        M = np.zeros((d, d))
        M[0, 0] = alpha
        M[0, 1] = beta
        M[d - 1, d - 1] = alpha
        M[d - 1, d - 2] = beta
        for i in range(1, d - 1):
            M[i, i] = alpha
            M[i, i - 1] = beta
            M[i, i + 1] = beta
        return M

    @classmethod
    def maj_jacobienne(cls, jaco, U, A, NX, NY):
        """ Mise à jour de la jacobienne de F. """
        for i in range(0, NX):
            for j in range(0, NY):
                jaco[i * NX + j, i * NX + j] = A[i * NX + j, i * NX + j] - 4 * cls.constanteSteph_ * U[j + i * NX]**3

    @classmethod
    def calcul_F(cls, A, U, B, NX, NY, T_ext):
        """ Calcul de la fonction F. """
        F = np.dot(A, U) - B
        for i in range(NX):
            for j in range(NY):
                F[j + i * NX] -= (U[j + i * NX]**4 - T_ext**4) * cls.constanteSteph_
        return F

    def __init__(self, tailleX, tailleY, noeudsX, noeudsY, mat_type='gauche', Tdroite=10, Tgauche=10, Thaut=10, Tbas=10, Text=10, Tinitiale=10, coeffThermique=1):
        PhysicsDriver.__init__(self)

        self.tailleDomaineX_ = tailleX  # Construction maillage
        self.tailleDomaineY_ = tailleY  # Construction maillage

        self.nombreNoeudsX_ = noeudsX  # Construction maillage
        self.nombreNoeudsY_ = noeudsY  # Construction maillage

        self.temperatureCLDroite_ = Tdroite  # Condtions aux limites
        self.temperatureCLGauche_ = Tgauche  # Condtions aux limites
        self.temperatureCLHaut_ = Thaut  # Condtions aux limites
        self.temperatureCLBas_ = Tbas  # Condtions aux limites
        self.temperatureCLExt_ = Text  # Condtions aux limites

        self.toleranceInterne_ = 1.0E-6
        self.erreurInterne_ = 1.00001
        self.erreurInitiale_ = 1.00001

        self.A_ = np.zeros((self.nombreNoeudsX_ * self.nombreNoeudsY_, self.nombreNoeudsX_ * self.nombreNoeudsY_))
        self.B_ = np.zeros((self.nombreNoeudsX_ * self.nombreNoeudsY_, 1))
        self.jaco_ = np.copy(self.A_)

        self.temperature_ = np.zeros((self.nombreNoeudsX_ * self.nombreNoeudsY_, 1))
        self.temperature_[0:self.nombreNoeudsX_ * self.nombreNoeudsY_, 0] = Tinitiale

        self._stationaryMode = False
        self.matType_ = mat_type

        self._print = False

        self.coeffThermique_ = coeffThermique

    def initialize(self):
        """ Creation des matrices liees au problème. """
        Id, upAndBotDiag, diagMat = self.AssembleMatGen2d(self.nombreNoeudsX_, -4, 1, 1)

        if self.matType_ == 'gauche':
            for j in range(self.nombreNoeudsY_):
                if j == 0:
                    self.A_[0:self.nombreNoeudsX_, 0:self.nombreNoeudsY_] = diagMat
                    self.A_[self.nombreNoeudsX_:2 * self.nombreNoeudsX_, 0:self.nombreNoeudsY_] = upAndBotDiag
                elif j == self.nombreNoeudsY_ - 1:
                    self.A_[j * self.nombreNoeudsX_:(j + 1) * self.nombreNoeudsX_, j * self.nombreNoeudsY_:(j + 1) * self.nombreNoeudsY_] = diagMat
                    self.A_[(j - 1) * self.nombreNoeudsX_:(j) * self.nombreNoeudsX_, j * self.nombreNoeudsY_:(j + 1) * self.nombreNoeudsY_] = upAndBotDiag
                else:
                    self.A_[j * self.nombreNoeudsX_:(j + 1) * self.nombreNoeudsX_, j * self.nombreNoeudsY_:(j + 1) * self.nombreNoeudsY_] = diagMat
                    self.A_[(j - 1) * self.nombreNoeudsX_:(j) * self.nombreNoeudsX_, j * self.nombreNoeudsY_:(j + 1) * self.nombreNoeudsY_] = upAndBotDiag
                    self.A_[(j + 1) * self.nombreNoeudsX_:(j + 2) * self.nombreNoeudsX_, j * self.nombreNoeudsY_:(j + 1) * self.nombreNoeudsY_] = upAndBotDiag
        else:
            for j in range(self.nombreNoeudsY_):
                if j == 0:
                    self.A_[0:self.nombreNoeudsX_, 0:self.nombreNoeudsY_] = -1 * Id
                    for i in range(1, self.nombreNoeudsX_ - 1):
                        self.A_[i, i + self.nombreNoeudsX_] = 1
                    self.A_[self.nombreNoeudsX_:2 * self.nombreNoeudsX_, 0:self.nombreNoeudsY_] = upAndBotDiag
                elif j == self.nombreNoeudsY_ - 1:
                    self.A_[j * self.nombreNoeudsX_:(j + 1) * self.nombreNoeudsX_, j * self.nombreNoeudsY_:(j + 1) * self.nombreNoeudsY_] = diagMat
                    self.A_[(j - 1) * self.nombreNoeudsX_:(j) * self.nombreNoeudsX_, j * self.nombreNoeudsY_:(j + 1) * self.nombreNoeudsY_] = upAndBotDiag
                else:
                    self.A_[j * self.nombreNoeudsX_:(j + 1) * self.nombreNoeudsX_, j * self.nombreNoeudsY_:(j + 1) * self.nombreNoeudsY_] = diagMat
                    self.A_[(j - 1) * self.nombreNoeudsX_:(j) * self.nombreNoeudsX_, j * self.nombreNoeudsY_:(j + 1) * self.nombreNoeudsY_] = upAndBotDiag
                    self.A_[(j + 1) * self.nombreNoeudsX_:(j + 2) * self.nombreNoeudsX_, j * self.nombreNoeudsY_:(j + 1) * self.nombreNoeudsY_] = upAndBotDiag

        # Construction matrice B
        if self.matType_ == 'gauche':
            for i in range(self.nombreNoeudsX_):
                if i == 0:
                    for j in range(self.nombreNoeudsX_):
                        self.B_[j, 0] -= self.temperatureCLGauche_
                self.B_[i * self.nombreNoeudsX_, 0] -= self.temperatureCLBas_
                self.B_[(i + 1) * self.nombreNoeudsX_ - 1, 0] -= self.temperatureCLHaut_
        else:
            for i in range(self.nombreNoeudsX_):
                if i == self.nombreNoeudsX_ - 1:
                    for j in range(self.nombreNoeudsY_):
                        self.B_[i * self.nombreNoeudsX_ + j, 0] -= self.temperatureCLDroite_
                self.B_[i * self.nombreNoeudsX_, 0] -= self.temperatureCLBas_
                self.B_[(i + 1) * self.nombreNoeudsX_ - 1, 0] -= self.temperatureCLHaut_

        # Construction jacobienne de F
        self.jaco_ = np.copy(self.A_)
        for i in range(1, self.nombreNoeudsX_ - 1):
            for j in range(1, self.nombreNoeudsY_ - 1):
                self.jaco_[i * self.nombreNoeudsX_ + j, i * self.nombreNoeudsX_ + j] -= 4 * self.constanteSteph_ * self.temperature_[j + i * self.nombreNoeudsX_]**3
        return True

    def terminate(self):
        pass

    def initTimeStep(self, dt):
        return True

    def solveTimeStep(self):
        isConverged_ = False

        while not isConverged_:
            _, isConverged_ = self.iterateTimeStep()

        return isConverged_

    def iterateTimeStep(self):
        deltaTemperature = np.copy(self.temperature_)
        self.maj_jacobienne(self.jaco_, self.temperature_, self.A_, self.nombreNoeudsX_, self.nombreNoeudsY_)
        F = self.calcul_F(self.A_, self.temperature_, self.B_, self.nombreNoeudsX_, self.nombreNoeudsY_, self.temperatureCLExt_)
        deltaTemperature = np.linalg.solve(self.jaco_, -F)
        deltaTemperature = np.reshape(deltaTemperature, np.shape(self.temperature_))
        self.erreurInterne_ = np.linalg.norm(deltaTemperature)
        if self._print:
            print("Norme de dX pour Newton :", self.erreurInterne_)
        self.temperature_ += deltaTemperature
        converged = self.erreurInterne_ < self.toleranceInterne_
        return True, converged

    def setStationaryMode(self, stationaryMode):
        self._stationaryMode = stationaryMode

    def getStationaryMode(self):
        return self._stationaryMode

   # Return an output scalar
    def getOutputDoubleValue(self, name):
        if name == "PRECISION_ATTEINTE":
            return self.erreurInterne_
        elif name == 'PRECISION':
            return self.toleranceInterne_
        else:
            int_name = int(name)
            if self.matType_ == 'gauche':
                if int_name >= 0 and int_name < self.nombreNoeudsX_:
                    phi = - self.coeffThermique_ * (self.temperature_[(self.nombreNoeudsX_ - 1) * self.nombreNoeudsX_ + int_name, 0] - self.temperature_[(self.nombreNoeudsX_ - 2) * self.nombreNoeudsX_ + int_name, 0])
                    return phi
                else:
                    raise Exception("PhysicsMatrix.getOutputDoubleValue only outputs between 0 and " + str(self.nombreNoeudsX_ - 1) + " available.")
            if self.matType_ == 'droit':
                if int_name >= 0 and int_name < self.nombreNoeudsX_:
                    return -self.temperature_[int_name, 0]
                else:
                    raise Exception("PhysicsMatrix.getOutputDoubleValue only outputs between 0 and " + str(self.nombreNoeudsX_ - 1) + " available.")

    # Import an input scalar. No return.
    def setInputDoubleValue(self, name, value):
        if name == 'PRECISION':
            self.toleranceInterne_ = value
        else:
            int_name = int(name)
            if self.matType_ == 'gauche':
                if int_name >= 0 and int_name < self.nombreNoeudsX_:

                    if int_name == 0:
                        self.B_[(self.nombreNoeudsX_ - 1) * self.nombreNoeudsX_ + int_name, 0] = value
                        self.B_[(self.nombreNoeudsX_ - 1) * self.nombreNoeudsX_ + int_name, 0] -= self.temperatureCLBas_
                    elif int_name == self.nombreNoeudsX_ - 1:
                        self.B_[(self.nombreNoeudsX_) * self.nombreNoeudsX_ - 1, 0] = value
                        self.B_[(self.nombreNoeudsX_) * self.nombreNoeudsX_ - 1, 0] -= self.temperatureCLHaut_
                    else:
                        self.B_[(self.nombreNoeudsX_ - 1) * self.nombreNoeudsX_ + int_name, 0] = value
                else:
                    raise Exception("PhysicsMatrix.setInputDoubleValue only inputs between 0 and " + str(self.nombreNoeudsX_ - 1) + " allowed.")
            if self.matType_ == 'droit':
                if int_name >= 0 and int_name < self.nombreNoeudsX_:
                    self.B_[int_name, 0] = - value / self.coeffThermique_
                else:
                    raise Exception("PhysicsMatrix.setInputDoubleValue only inputs between 0 and " + str(self.nombreNoeudsX_ - 1) + " allowed.")

    def abortTimeStep(self):
        pass

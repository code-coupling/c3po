# -*- coding: utf-8 -*-
from __future__ import print_function, division
import numpy as np
from numpy import linalg
from scipy.sparse.linalg.isolve import cg

from c3po.PhysicsDriver import PhysicsDriver

# Fonction pour créer une matrice identidé, une matrice avec une diagonale de valeur "f", et une matrice tridiagonale de taille nombreNoeudsX avec c sur la diagonale et e sur les diagonales sup et inf 
def AssembleMatGen2d(nombreNoeudsX, c,e,f):
    Id = np.eye(nombreNoeudsX)
    upAndBotDiag = np.eye(nombreNoeudsX) * f
    diagMat = AssembleMatGen1d(nombreNoeudsX,c,e)
    return Id, upAndBotDiag, diagMat

# Fonction pour construire matrice tridiagonale de taille d avec alpha sur la diagonale et beta sur les diagonales sup et inf
def AssembleMatGen1d(d,alpha,beta):
    M = np.zeros((d,d))
    M[0,0] = alpha
    M[0,1] = beta
    M[d-1,d-1] = alpha
    M[d-1,d-2] = beta
    for i in range(1,d-1):
        M[i,i] = alpha
        M[i,i-1] = beta
        M[i,i+1] = beta
    return M

# Mise à jour de la jacobienne de F 
def maj_jacobienne(jaco,U,A,NX, NY):
    for i in range(0,NX):
        for j in range(0,NY):
            jaco[i*NX+j,i*NX+j] = A[i*NX+j,i*NX+j] - 4  * constanteSteph * U[j+i*NX]**3

# Calcule de la fonction F 
def calcul_F(A,U,B,NX,NY, T_ext):
    F = np.dot(A,U) - B
    for i in range(NX):
        for j in range(NY):
            F[j+i*NX] -= (U[j+i*NX]**4 - T_ext**4)  *constanteSteph 
    return F

# Resolution du problème linéaire A * sol = b à l'aide du gradient conjugué 
def do_iteration(A, b, tolerance = None, m=None):
    global iteration
    iteration = 0
    def call(x):
        global iteration
        iteration = iteration + 1
    sol, info = cg(A, b, tol=tolerance, M=m, callback=call)
    return sol, info, iteration

constanteSteph = 0.0000001

class PlaquePhysicsDriver(PhysicsDriver):

    def __init__(self, tailleX, tailleY, noeudsX, noeudsY, mat_type = 'gauche',Tdroite=10,Tgauche=10,Thaut=10,Tbas=10,Text=10,Tinitiale=10,coeffThermique=1):
        PhysicsDriver.__init__(self)

        self.tailleDomaineX_ = tailleX # Construction maillage
        self.tailleDomaineY_ = tailleY # Construction maillage

        self.nombreNoeudsX_ = noeudsX # Construction maillage
        self.nombreNoeudsY_ = noeudsY # Construction maillage

        self.coeffThermique_ = 1. 

        self.temperatureCLDroite_ = 1. # Condtions aux limites
        self.temperatureCLGauche_ = 1. # Condtions aux limites
        self.temperatureCLHaut_   = 1. # Condtions aux limites
        self.temperatureCLBas_    = 1. # Condtions aux limites
        self.temperatureCLExt_    = 1. # Condtions aux limites

        self.toleranceInterne_ = 1.0E-6 
        self.toleranceInterneCible_ = 1.0E-6 
        self.erreurInterne_    = 1.00001
        self.erreurInitiale_   = 1.00001

        self.A_ = np.zeros((self.nombreNoeudsX_*self.nombreNoeudsY_,self.nombreNoeudsX_*self.nombreNoeudsY_))
        self.B_ = np.zeros((self.nombreNoeudsX_*self.nombreNoeudsY_,1))
        self.jaco_ = np.copy(self.A_)

        self.temperature_ = np.zeros((self.nombreNoeudsX_*self.nombreNoeudsY_,1))
      
        self.initialize_ = False
        self.init_ = False
        self._stationaryMode = False
        self.matType_ = mat_type

        self._print = True

        self.temperatureCLDroite_ = Tdroite
        self.temperatureCLGauche_ = Tgauche
        self.temperatureCLHaut_   = Thaut
        self.temperatureCLBas_    = Tbas
        self.temperatureCLExt_    = Text

        self.coeffThermique_ = coeffThermique

        self.temperature_[0:self.nombreNoeudsX_*self.nombreNoeudsY_,0] = Tinitiale

    # Initialize the object.
    def initialize(self):
        if not self.initialize_ : 
            # Création des matrices liées au problème
            # # Generation des matrices liées au problème
            Id, upAndBotDiag, diagMat = AssembleMatGen2d(self.nombreNoeudsX_,-4,1,1)

            if self.matType_ == 'gauche': 
                for j in range(self.nombreNoeudsY_):
                    if j == 0 : 
                        self.A_[0:self.nombreNoeudsX_,0:self.nombreNoeudsY_] = diagMat
                        self.A_[self.nombreNoeudsX_:2*self.nombreNoeudsX_,0:self.nombreNoeudsY_] = upAndBotDiag
                    elif j == self.nombreNoeudsY_-1 :
                        self.A_[j *self.nombreNoeudsX_:(j+1) * self.nombreNoeudsX_,j * self.nombreNoeudsY_:(j+1)*self.nombreNoeudsY_] = diagMat
                        self.A_[(j-1)*self.nombreNoeudsX_:(j) * self.nombreNoeudsX_,j *self.nombreNoeudsY_:(j+1)*self.nombreNoeudsY_] = upAndBotDiag
                    else : 
                        self.A_[j *self.nombreNoeudsX_:(j+1) * self.nombreNoeudsX_,j * self.nombreNoeudsY_:(j+1)*self.nombreNoeudsY_] = diagMat
                        self.A_[(j-1)*self.nombreNoeudsX_:(j) * self.nombreNoeudsX_,j *self.nombreNoeudsY_:(j+1)*self.nombreNoeudsY_] = upAndBotDiag
                        self.A_[(j+1)*self.nombreNoeudsX_:(j+2) * self.nombreNoeudsX_,j *self.nombreNoeudsY_:(j+1)*self.nombreNoeudsY_] = upAndBotDiag
            else : 
                for j in range(self.nombreNoeudsY_):
                    if j == 0 : 
                        self.A_[0:self.nombreNoeudsX_,0:self.nombreNoeudsY_] = -1 * Id
                        for i in range(1,self.nombreNoeudsX_-1):
                            self.A_[i,i+self.nombreNoeudsX_] = 1
                        self.A_[self.nombreNoeudsX_:2*self.nombreNoeudsX_,0:self.nombreNoeudsY_] = upAndBotDiag
                    elif j == self.nombreNoeudsY_-1 :
                        self.A_[j *self.nombreNoeudsX_:(j+1) * self.nombreNoeudsX_,j * self.nombreNoeudsY_:(j+1)*self.nombreNoeudsY_] = diagMat
                        self.A_[(j-1)*self.nombreNoeudsX_:(j) * self.nombreNoeudsX_,j *self.nombreNoeudsY_:(j+1)*self.nombreNoeudsY_] = upAndBotDiag
                    else : 
                        self.A_[j *self.nombreNoeudsX_:(j+1) * self.nombreNoeudsX_,j * self.nombreNoeudsY_:(j+1)*self.nombreNoeudsY_] = diagMat
                        self.A_[(j-1)*self.nombreNoeudsX_:(j) * self.nombreNoeudsX_,j *self.nombreNoeudsY_:(j+1)*self.nombreNoeudsY_] = upAndBotDiag
                        self.A_[(j+1)*self.nombreNoeudsX_:(j+2) * self.nombreNoeudsX_,j *self.nombreNoeudsY_:(j+1)*self.nombreNoeudsY_] = upAndBotDiag
            
            #Construction matrice B
            if self.matType_ == 'gauche': 
                for i in range(self.nombreNoeudsX_):
                    if i == 0 :            
                        for j in range(self.nombreNoeudsX_):
                            self.B_[j,0] -= self.temperatureCLGauche_
                    self.B_[i*self.nombreNoeudsX_,0] -= self.temperatureCLBas_
                    self.B_[(i+1)*self.nombreNoeudsX_-1,0] -= self.temperatureCLHaut_
            else : 
                for i in range(self.nombreNoeudsX_):
                    if i == self.nombreNoeudsX_-1 :            
                        for j in range(self.nombreNoeudsY_):
                            self.B_[i*self.nombreNoeudsX_+j,0] -= self.temperatureCLDroite_
                    self.B_[i*self.nombreNoeudsX_,0] -= self.temperatureCLBas_
                    self.B_[(i+1)*self.nombreNoeudsX_-1,0] -= self.temperatureCLHaut_ 

            # Construction jacobienne de F
            self.jaco_ = np.copy(self.A_)
            for i in range(1,self.nombreNoeudsX_-1):
                for j in range(1,self.nombreNoeudsY_-1):
                    self.jaco_[i*self.nombreNoeudsX_+j,i*self.nombreNoeudsX_+j] -= 4  * constanteSteph  *self.temperature_[j+i*self.nombreNoeudsX_]**3
            self.initialize_ = True
        else : 
            pass 
        return True

    def terminate(self):
        """! See c3po.PhysicsDriver.terminate(). """
        pass

    def initTimeStep(self, dt):
        """! See c3po.PhysicsDriver.initTimeStep(). """
        return True

    def solveTimeStep(self):
        """! See c3po.PhysicsDriver.solveTimeStep(). """
        iiter_ = 0
        isConverged_ = False 

        while not isConverged_ :
            _, isConverged_ = self.iterateTimeStep()
            iiter_ += 1

        return isConverged_

    # Solve next time-step problem. Solves a steady state if dt < 0. No return.
    def iterateTimeStep(self):
        """! See c3po.PhysicsDriver.iterateTimeStep(). """
        deltaTemperature = np.copy(self.temperature_)
        if not self.init_ : 
            for i in range(len(self.temperature_)):
                deltaTemperature[i]=1
            self.init_ = True
        self.erreurInterne_ = np.linalg.norm(deltaTemperature)
        maj_jacobienne(self.jaco_, self.temperature_, self.A_, self.nombreNoeudsX_, self.nombreNoeudsY_)
        F = calcul_F(self.A_, self.temperature_, self.B_, self.nombreNoeudsX_, self.nombreNoeudsY_, self.temperatureCLExt_)
        deltaTemperature, info, itg = do_iteration(self.jaco_,-F,tolerance=1.0E-12,m=np.eye((self.nombreNoeudsX_*self.nombreNoeudsX_))*np.diag(self.jaco_))
        if self._print : print("Nombre d'itérations linéaires :", itg)
        deltaTemperature = np.reshape(deltaTemperature,np.shape(self.temperature_))
        self.erreurInterne_ = np.linalg.norm(deltaTemperature)
        if self._print :  print("Norme de dX pour Newton :", self.erreurInterne_)
        self.temperature_ += deltaTemperature
        converged = self.erreurInterne_ < self.toleranceInterne_
        return True, converged

    def setStationaryMode(self, stationaryMode):
        """! See c3po.PhysicsDriver.setStationaryMode(). """
        self._stationaryMode = stationaryMode

    def getStationaryMode(self):
        """! See c3po.PhysicsDriver.getStationaryMode(). """
        return self._stationaryMode

   # Return an output scalar
    def getOutputDoubleValue(self, name):
        """! See c3po.PhysicsDriver.getOutputDoubleValue(). """
        if name == "PRECISION_ATTEINTE" : 
            return self.erreurInterne_
        elif name == 'PRECISION' : 
            return self.toleranceInterne_
        else :     
            int_name = int(name)
            if self.matType_ == 'gauche' : 
                if int_name >= 0 and int_name < self.nombreNoeudsX_:
                    phi = - self.coeffThermique_ * ( self.temperature_[(self.nombreNoeudsX_-1) * self.nombreNoeudsX_ + int_name, 0 ] - self.temperature_[(self.nombreNoeudsX_-2) * self.nombreNoeudsX_ + int_name , 0] ) 
                    return phi
                else:
                    raise Exception("PhysicsMatrix.getOutputDoubleValue only outputs between 0 and " + str(self.nombreNoeudsX_ - 1) + " available.")
            if self.matType_ == 'droit' : 
                if int_name >= 0 and int_name < self.nombreNoeudsX_:
                    return -self.temperature_[int_name,0] 
                else:
                    raise Exception("PhysicsMatrix.getOutputDoubleValue only outputs between 0 and " + str(self.nombreNoeudsX_ - 1) + " available.")
    
    # Import an input scalar. No return.
    def setInputDoubleValue(self, name, value):
        """! See c3po.PhysicsDriver.setInputDoubleValue(). """
        if name == 'PRECISION' or name == 'Accuracy': 
            self.toleranceInterne_ = value
        elif name == "PRECISION_CIBLE" : 
            self.toleranceInterneCible_ = value
        else: 
            int_name = int(name)
            if self.matType_ == 'gauche': 
                if int_name >= 0 and int_name < self.nombreNoeudsX_:
                    
                    if int_name == 0 : 
                        self.B_[(self.nombreNoeudsX_-1)*self.nombreNoeudsX_ + int_name,0]  = value
                        self.B_[(self.nombreNoeudsX_-1)*self.nombreNoeudsX_ + int_name,0] -= self.temperatureCLBas_
                    elif int_name == self.nombreNoeudsX_ - 1 : 
                        self.B_[(self.nombreNoeudsX_)*self.nombreNoeudsX_ -1,0]  = value
                        self.B_[(self.nombreNoeudsX_)*self.nombreNoeudsX_ -1,0] -= self.temperatureCLHaut_
                    else :
                        self.B_[(self.nombreNoeudsX_-1)*self.nombreNoeudsX_ + int_name,0] = value
                else:
                    raise Exception("PhysicsMatrix.setInputDoubleValue only inputs between 0 and " + str(self.nombreNoeudsX_ - 1) + " allowed.")
            if self.matType_ == 'droit' : 
                if int_name >= 0 and int_name < self.nombreNoeudsX_:
                    self.B_[int_name,0] = - value / self.coeffThermique_
                else:
                    raise Exception("PhysicsMatrix.setInputDoubleValue only inputs between 0 and " + str(self.nombreNoeudsX_ - 1) + " allowed.")

    def abortTimeStep(self):
        pass
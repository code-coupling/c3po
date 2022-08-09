# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class THEDIDriver. """
from __future__ import print_function, division

from c3po.PhysicsDriver import PhysicsDriver
from .THEDIDriver import THEDIDriver
import numpy as np

class THEDIDriver_forResidualBalance(THEDIDriver):
    """! This is the implementation of PhysicsDriver for THEDI. """

    def __init__(self, thediICoCo):
        """! Build a THEDIDriver object.

        @param thediICoCo implementation of the ICOCO interface for THEDI.
        """
        THEDIDriver.__init__(self, thediICoCo)
        if thediICoCo.GetICoCoMajorVersion() != self.GetICoCoMajorVersion():
            raise AssertionError("The ICoCo major version of the provided object ({}) is not the expected one ({})".format(thediICoCo.GetICoCoMajorVersion(), self.GetICoCoMajorVersion()))
        self._thedi = thediICoCo
        self._pasDeTemps = 0.
        self._precisionAtteinte = 1.001 
        self._precisionInitiale = 1.001 
        self._precision = 1e-8
        self._debit = False

        self._temperatureFacteurEchelle = 0.
        self._densiteFacteurEchelle = 0.
        self._pressionFacteurEchelle = 0.
        self._temperatureVapeurFacteurEchelle = 0.
        self._vitesseFacteurEchelle = 0.
        self._vitesseVapeurFacteurEchelle = 0.
        self._videFacteurEchelle = 0.
        self._temperatureEffectiveFacteurEchelle = 0.    

    def setInputDoubleValue(self, name, value):
        if name == "PRECISION" : 
            self._precision = value
        elif name == "pressionFacteurEchelle" : 
            self._pressionFacteurEchelle = value
        elif name == "densiteFacteurEchelle" : 
            self._densiteFacteurEchelle = value
        elif name == "temperatureFacteurEchelle" : 
            self._temperatureFacteurEchelle = value  
        elif name == "temperatureVapeurFacteurEchelle" : 
            self._temperatureVapeurFacteurEchelle = value  
        elif name == "temperatureEffectiveFacteurEchelle" : 
            self._temperatureEffectiveFacteurEchelle = value  
        elif name == "vitesseFacteurEchelle" : 
            self._vitesseFacteurEchelle = value  
        elif name == "vitesseMoyenneFacteurEchelle" : 
            self._vitesseMoyenneFacteurEchelle = value
        elif name == "vitesseVapeurFacteurEchelle" : 
            self._vitesseVapeurFacteurEchelle = value  
        elif name == "videFacteurEchelle" : 
            self._videFacteurEchelle = value  
        elif name == 'iterateStatus':
            self._iterateStatus = value
        elif name == 'pasDeTemps':
            self._pasDeTemps = value
        elif name == 'CFL':
            for i in range(len(self._thedi._coeur.Get_canaux())):
                self._thedi._coeur.Get_canal(i).Get_thermohydro().Set_schema_stationnaire(True,60,1E-8,value,60.)
        else : 
            THEDIDriver.setInputDoubleValue(self, name, value)

    def getOutputDoubleValue(self, name):
        if name == "PRECISION" : 
            return self._precision
        elif name == "pressionFacteurEchelle" : 
            return self._pressionFacteurEchelle
        elif name == "temperatureFacteurEchelle" : 
            return self._temperatureFacteurEchelle
        elif name == "densiteFacteurEchelle" : 
            return self._densiteFacteurEchelle
        elif name == "temperatureVapeurFacteurEchelle" : 
            return self._temperatureVapeurFacteurEchelle
        elif name == "temperatureEffectiveFacteurEchelle" : 
            return self._temperatureEffectiveFacteurEchelle
        elif name == "vitesseFacteurEchelle" : 
            return self._vitesseFacteurEchelle
        elif name == "vitesseMoyenneFacteurEchelle" : 
            return self._vitesseMoyenneFacteurEchelle 
        elif name == "vitesseVapeurFacteurEchelle" : 
            return self._vitesseVapeurFacteurEchelle
        elif name == "videFacteurEchelle" : 
            return self._videFacteurEchelle
        elif name == 'PRECISION_INITIALE':
            if self._pasDeTemps > 0 : 
                vitesseOld = self.getOutputMEDDoubleField('VITESSE_MASSIQUE')
                pressionOld= self.getOutputMEDDoubleField('PRESSION')
                temperatureOld  = self.getOutputMEDDoubleField('TEMPERATURE_LIQUIDE')
                videOld = self.getOutputMEDDoubleField('TAUX_DE_VIDE')
                
                self._thedi._coeur.Calcule_pas_de_temps_thermohydro(self._pasDeTemps,True)
                valideTimeStep = (self._thedi._coeur.Get_taille_dernier_pas_de_temps() == self._pasDeTemps)
                dtUsed = self._pasDeTemps
                while not valideTimeStep :
                    dtUsed /= 2
                    if dtUsed < 1e-6 : 
                        print('Le pas de temps devient inferieur a 10-6 : on abandonne ! ')
                        return False, False
                    print('Nouveau pas de temps pour le transitoire THEDI : dt = ', dtUsed)
                    self._thedi._coeur.Calcule_pas_de_temps_thermohydro(dtUsed,True)
                    valideTimeStep = (self._thedi._coeur.Get_taille_dernier_pas_de_temps() == dtUsed)
                self._thedi._coeur.Valide_pas_de_temps()
                
                vitesse = self.getOutputMEDDoubleField('VITESSE_MASSIQUE')
                pression = self.getOutputMEDDoubleField('PRESSION')
                temperature = self.getOutputMEDDoubleField('TEMPERATURE_LIQUIDE')
                vide = self.getOutputMEDDoubleField('TAUX_DE_VIDE')
                
                if self._temperatureFacteurEchelle == 0 :
                    self.setInputDoubleValue('pressionFacteurEchelle',pression.norm2())
                    self.setInputDoubleValue('vitesseMoyenneFacteurEchelle',vitesse.norm2())
                    self.setInputDoubleValue('temperatureFacteurEchelle',temperature.norm2())

                vitesseOld.setMesh(vitesse.getMesh())
                pressionOld.setMesh(pression.getMesh())
                temperatureOld.setMesh(temperature.getMesh())
                videOld.setMesh(vide.getMesh())
                
                self._precisionInitiale  = ((temperature-temperatureOld).__div__(self._temperatureFacteurEchelle)).norm2()**2 
                self._precisionInitiale += ((pression-pressionOld).__div__(self._pressionFacteurEchelle)).norm2()**2
                self._precisionInitiale += ((vitesse - vitesseOld).__div__(self._vitesseMoyenneFacteurEchelle)).norm2()**2
                self._precisionInitiale += (vide - videOld).norm2()**2 
                self._precisionInitiale /= ( (temperature.__div__(self._temperatureFacteurEchelle)).norm2()**2 + (pression.__div__(self._pressionFacteurEchelle)).norm2()**2 + (vitesse.__div__(self._vitesseMoyenneFacteurEchelle)).norm2()**2 + vide.norm2()**2 ) 
                self._precisionInitiale = np.sqrt(self._precisionInitiale)        
            else : 
                print("On n'a pas de transitoire stablisé, on ne peut pas avoir accès à la précision initiale !")
                return -1 
            return self._precisionInitiale
        elif name == 'PRECISION_ATTEINTE':
            return self._precisionAtteinte
        elif name == 'iterateStatus' :
            return self._iterateStatus
        else : 
            return THEDIDriver.getInputDoubleValue(self, name)
            #else :
            #raise Exception("THEDIDriver.getValue '{}' is not available yet".format(name))    

    
    def solve(self):
        return self.solveTimeStep()

    def solveTimeStep(self):
        if self._pasDeTemps > 0 : 
            iiter_ = 0
            isConverged_ = False 
            tempsCalcul = 0.
            print("iteration THEDI ", iiter_)
            
            vitesseOld = self.getOutputMEDDoubleField('VITESSE_MASSIQUE')
            pressionOld = self.getOutputMEDDoubleField('PRESSION')
            temperatureOld = self.getOutputMEDDoubleField('TEMPERATURE_LIQUIDE')
            videOld = self.getOutputMEDDoubleField('TAUX_DE_VIDE')


            try : 
                self._thedi._coeur.Calcule_pas_de_temps_thermohydro(self._pasDeTemps,True)
            except : 
                self._thedi._coeur.Calcule_pas_de_temps_thermique_cinetique_point(-1,False)
                self._thedi._coeur.Valide_pas_de_temps()
                return False 
            valideTimeStep = (self._thedi._coeur.Get_taille_dernier_pas_de_temps() == self._pasDeTemps)
            dtUsed = self._pasDeTemps
            while not valideTimeStep :
                dtUsed = dtUsed/2. 
                if dtUsed < 1e-6 : 
                    print('Le pas de temps devient inferieur a 10-6 : on abandonne ! ')
                    return False, False
                print('Nouveau pas de temps pour le transitoire THEDI : dt = ', dtUsed)

                try : 
                    self._thedi._coeur.Calcule_pas_de_temps_thermohydro(self._pasDeTemps,True)
                except : 
                    self._thedi._coeur.Calcule_pas_de_temps_thermique_cinetique_point(-1,False)
                    self._thedi._coeur.Valide_pas_de_temps()
                    return False 

                valideTimeStep = (self._thedi._coeur.Get_taille_dernier_pas_de_temps() == dtUsed)
            self._thedi._coeur.Valide_pas_de_temps()
            
            vitesse = self.getOutputMEDDoubleField('VITESSE_MASSIQUE')
            pression = self.getOutputMEDDoubleField('PRESSION')
            temperature = self.getOutputMEDDoubleField('TEMPERATURE_LIQUIDE')
            vide = self.getOutputMEDDoubleField('TAUX_DE_VIDE')
            
            vitesseOld.setMesh(vitesse.getMesh())
            pressionOld.setMesh(pression.getMesh())
            temperatureOld.setMesh(temperature.getMesh())
            videOld.setMesh(vide.getMesh())

            if self._temperatureFacteurEchelle == 0 :
                self.setInputDoubleValue('pressionFacteurEchelle',pression.norm2())
                self.setInputDoubleValue('vitesseMoyenneFacteurEchelle',vitesse.norm2())
                self.setInputDoubleValue('temperatureFacteurEchelle',temperature.norm2())
                    
            self._precisionAtteinte  = ((temperature-temperatureOld).__div__(self._temperatureFacteurEchelle)).norm2()**2 
            self._precisionAtteinte += ((pression-pressionOld).__div__(self._pressionFacteurEchelle)).norm2()**2
            self._precisionAtteinte += ((vitesse - vitesseOld).__div__(self._vitesseMoyenneFacteurEchelle)).norm2()**2
            self._precisionAtteinte += (vide - videOld).norm2()**2 
            self._precisionAtteinte /= ( (temperature.__div__(self._temperatureFacteurEchelle)).norm2()**2 + (pression.__div__(self._pressionFacteurEchelle)).norm2()**2 + (vitesse.__div__(self._vitesseMoyenneFacteurEchelle)).norm2()**2 + vide.norm2()**2 ) 
            self._precisionAtteinte = np.sqrt(self._precisionAtteinte)      

            tempsCalcul += self._thedi._coeur.Get_taille_dernier_pas_de_temps()
        
            iiter_ += 1
            
            vitesseOld = vitesse
            pressionOld = pression
            temperatureOld  = temperature
            videOld = vide
            
            print("error THEDI: ", self._precisionAtteinte)
            while (self._precisionAtteinte > self._precision) : 
                print("iteration THEDI ", iiter_)
                
                dtUsed = self._pasDeTemps             
                try : 
                    self._thedi._coeur.Calcule_pas_de_temps_thermohydro(dtUsed,True)
                except :                     
                    self._thedi._coeur.Calcule_pas_de_temps_thermique_cinetique_point(-1,False)
                    self._thedi._coeur.Valide_pas_de_temps()
                    return False                   
                
                valideTimeStep = (self._thedi._coeur.Get_taille_dernier_pas_de_temps() == dtUsed)
                while not valideTimeStep :
                    dtUsed = dtUsed/2.
                    if dtUsed < 1e-6 : 
                        print('Le pas de temps devient inferieur a 10-6 : on abandonne ! ')
                        return False
                    print('Nouveau pas de temps pour le transitoire THEDI : dt = ', dtUsed)
                    try : 
                        self._thedi._coeur.Calcule_pas_de_temps_thermohydro(dtUsed,True)
                    except :                      
                        self._thedi._coeur.Calcule_pas_de_temps_thermique_cinetique_point(-1,False)
                        self._thedi._coeur.Valide_pas_de_temps()
                        return False    
                    valideTimeStep = (self._thedi._coeur.Get_taille_dernier_pas_de_temps() == dtUsed)
                self._thedi._coeur.Valide_pas_de_temps()
                
                tempsCalcul += self._thedi._coeur.Get_taille_dernier_pas_de_temps()
                vitesse = self.getOutputMEDDoubleField('VITESSE_MASSIQUE')
                pression = self.getOutputMEDDoubleField('PRESSION')
                temperature = self.getOutputMEDDoubleField('TEMPERATURE_LIQUIDE')
                vide = self.getOutputMEDDoubleField('TAUX_DE_VIDE')

                vitesseOld.setMesh(vitesse.getMesh())
                pressionOld.setMesh(pression.getMesh())
                temperatureOld.setMesh(temperature.getMesh())
                videOld.setMesh(vide.getMesh())

                self._precisionAtteinte =      ((temperature-temperatureOld).__div__(self._temperatureFacteurEchelle)).norm2()**2 
                self._precisionAtteinte += ((pression-pressionOld).__div__(self._pressionFacteurEchelle)).norm2()**2
                self._precisionAtteinte += ((vitesse - vitesseOld).__div__(self._vitesseMoyenneFacteurEchelle)).norm2()**2
                self._precisionAtteinte += (vide - videOld).norm2()**2 
                self._precisionAtteinte /= (  (temperature.__div__(self._temperatureFacteurEchelle)).norm2()**2 + (pression.__div__(self._pressionFacteurEchelle)).norm2()**2 + (vitesse.__div__(self._vitesseMoyenneFacteurEchelle)).norm2()**2 + vide.norm2()**2 ) 
                self._precisionAtteinte = np.sqrt(self._precisionAtteinte)    
                iiter_ += 1
                
                vitesseOld = vitesse
                pressionOld = pression
                temperatureOld  = temperature
                videOld = vide
                print("error THEDI : ", self._precisionAtteinte)
            print("Taux de vide max : ", self.getOutputMEDDoubleField('TAUX_DE_VIDE').getMaxValue())
            self._thedi._coeur.Calcule_pas_de_temps_thermique_cinetique_point(-1,False)
            self._thedi._coeur.Valide_pas_de_temps()
            isConverged_ = not(self._precisionAtteinte > self._precision)
            return isConverged_
        else : 
            return THEDIDriver.solveTimeStep(self)
            
    
    
    

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

import pyTHEDI as THEDI
try:
    import pyTHEDI_MED as THEDI_MED
except:
    pass
from THEDIInit import THEDIInit

import c3po.medcouplingCompat as mc
from c3po.PhysicsDriver import PhysicsDriver


class THEDIDriver(PhysicsDriver):
    """! This is the implementation of PhysicsDriver for THEDI.

    A THEDIInit method must be available. It has to take four inputs:
    - A THEDI.COEUR object to initialize.
    - A THEDI.MED_INTERFACE to initialize. It will give access to THEDI MED functionalities.
    - An (empty) list of THEDI channel objects to build.
    - An (empty) list of THEDI materials to build.
    """

    def __init__(self):
        PhysicsDriver.__init__(self)
        self._isInit = False
        self._time = 0.
        self._dt = 1.e30
        self._coeur = THEDI.COEUR()
        try:
            self._medInterface = THEDI_MED.INTERFACE()
        except:
            self._medInterface = THEDI.MED_INTERFACE()
        self._canaux = []
        self._materiaux = []
        self._outputFieldCorrespondence = {}
        if hasattr(THEDI, "Sortie_MED"):
            self._outputFieldCorrespondence["TEMPERATURE_LIQUIDE"] = THEDI.Sortie_MED.TEMPERATURE_LIQUIDE
            self._outputFieldCorrespondence["TEMPERATURE_VAPEUR"] = THEDI.Sortie_MED.TEMPERATURE_VAPEUR
            self._outputFieldCorrespondence["TEMPERATURE_MOYENNE"] = THEDI.Sortie_MED.TEMPERATURE_MOYENNE
            self._outputFieldCorrespondence["MASSE_VOLUMIQUE"] = THEDI.Sortie_MED.MASSE_VOLUMIQUE
            self._outputFieldCorrespondence["PRESSION"] = THEDI.Sortie_MED.PRESSION
            self._outputFieldCorrespondence["TAUX_DE_VIDE"] = THEDI.Sortie_MED.TAUX_DE_VIDE
            self._outputFieldCorrespondence["VITESSE_MASSIQUE"] = THEDI.Sortie_MED.VITESSE_MASSIQUE
            self._outputFieldCorrespondence["VITESSE_LIQUIDE"] = THEDI.Sortie_MED.VITESSE_LIQUIDE
            self._outputFieldCorrespondence["VITESSE_VAPEUR"] = THEDI.Sortie_MED.VITESSE_VAPEUR
            self._outputFieldCorrespondence["TITRE"] = THEDI.Sortie_MED.TITRE
            self._outputFieldCorrespondence["ENERGIE_INTERNE"] = THEDI.Sortie_MED.ENERGIE_INTERNE
            self._outputFieldCorrespondence["ENTHALPIE"] = THEDI.Sortie_MED.ENTHALPIE
            self._outputFieldCorrespondence["FLUX_CRITIQUE_SUR_FLUX"] = THEDI.Sortie_MED.FLUX_CRITIQUE_SUR_FLUX
            self._outputFieldCorrespondence["T_PAROI"] = THEDI.Sortie_MED.T_PAROI
            self._outputFieldCorrespondence["T_INTERNE"] = THEDI.Sortie_MED.T_INTERNE
            self._outputFieldCorrespondence["T_EFFECTIVE"] = THEDI.Sortie_MED.T_EFFECTIVE
        else:
            self._outputFieldCorrespondence["TEMPERATURE_LIQUIDE"] = THEDI_MED.Sortie_MED.TEMPERATURE_LIQUIDE
            self._outputFieldCorrespondence["TEMPERATURE_VAPEUR"] = THEDI_MED.Sortie_MED.TEMPERATURE_VAPEUR
            self._outputFieldCorrespondence["TEMPERATURE_MOYENNE"] = THEDI_MED.Sortie_MED.TEMPERATURE_MOYENNE
            self._outputFieldCorrespondence["MASSE_VOLUMIQUE"] = THEDI_MED.Sortie_MED.MASSE_VOLUMIQUE
            self._outputFieldCorrespondence["PRESSION"] = THEDI_MED.Sortie_MED.PRESSION
            self._outputFieldCorrespondence["TAUX_DE_VIDE"] = THEDI_MED.Sortie_MED.TAUX_DE_VIDE
            self._outputFieldCorrespondence["VITESSE_MASSIQUE"] = THEDI_MED.Sortie_MED.VITESSE_MASSIQUE
            self._outputFieldCorrespondence["VITESSE_LIQUIDE"] = THEDI_MED.Sortie_MED.VITESSE_LIQUIDE
            self._outputFieldCorrespondence["VITESSE_VAPEUR"] = THEDI_MED.Sortie_MED.VITESSE_VAPEUR
            self._outputFieldCorrespondence["TITRE"] = THEDI_MED.Sortie_MED.TITRE
            self._outputFieldCorrespondence["ENERGIE_INTERNE"] = THEDI_MED.Sortie_MED.ENERGIE_INTERNE
            self._outputFieldCorrespondence["ENTHALPIE"] = THEDI_MED.Sortie_MED.ENTHALPIE
            self._outputFieldCorrespondence["FLUX_CRITIQUE_SUR_FLUX"] = THEDI_MED.Sortie_MED.FLUX_CRITIQUE_SUR_FLUX
            self._outputFieldCorrespondence["T_PAROI"] = THEDI_MED.Sortie_MED.T_PAROI
            self._outputFieldCorrespondence["T_INTERNE"] = THEDI_MED.Sortie_MED.T_INTERNE
            self._outputFieldCorrespondence["T_EFFECTIVE"] = THEDI_MED.Sortie_MED.T_EFFECTIVE
            self._outputFieldCorrespondence["PUISSANCE_SOLIDE"] = THEDI_MED.Sortie_MED.PUISSANCE_SOLIDE
            self._outputFieldCorrespondence["PUISSANCE_LIQUIDE"] = THEDI_MED.Sortie_MED.PUISSANCE_LIQUIDE

    def getTHEDIObjects(self):
        """! Return THEDI objects.

        @return THEDI.COEUR and THEDI.MED_INTERFACE.
        """
        return self._coeur, self._medInterface

    def initialize(self):
        if not self._isInit:
            self._isInit = True
            self._canaux[:] = []
            self._materiaux[:] = []
            THEDIInit(self._coeur, self._medInterface, self._canaux, self._materiaux)
        return True

    def terminate(self):
        pass

    def presentTime(self):
        return self._time

    def computeTimeStep(self):
        return (self._dt, False)

    def initTimeStep(self, dt):
        self._dt = dt
        return True

    def solveTimeStep(self):
        self._coeur.Calcule_pas_de_temps(self._dt)
        return self._coeur.Get_taille_dernier_pas_de_temps() == self._dt

    def validateTimeStep(self):
        if self._dt > 0.:
            self._time += self._dt
        self._coeur.Valide_pas_de_temps()

    def abortTimeStep(self):
        pass

    def getInputMEDFieldTemplate(self, name):
        """! Return an empty field lying on the MEDCouplingMesh object used by THEDI.

        See PhysicsDriver.getInputMEDFieldTemplate().

        THEDI can take fields given on any mesh and performs projection if needed, but no projection are done if this mesh is used.
        """
        outputField = mc.MEDCouplingFieldDouble(mc.ON_CELLS, mc.ONE_TIME)
        try:
            self._medInterface.Place_maillage_interne_dans_champ(outputField)
        except:
            self._medInterface.Place_maillage_interne_thermohydro_dans_champ(outputField)
        return outputField

    def setInputMEDField(self, name, field):
        """! Set the MED field field to the component under the name name.

        See PhysicsDriver.setInputMEDField().

        Accepted fields are :
        - "fluidPower"
        - "solidPower::NameObject::NameMats" with NameObject the name of a solid object in THEDI and NameMats a list of material names.
        - "setParamLambda::NameObject::NameMat::Int" with NameObject the name of a solid object in THEDI, NameMat a material name and Int a number identifying the parameter to set for thermal conductivity calculation.
        - "setParamCapa::NameObject::NameMat::Int" idem previous but for heat capacity.
        - "feedbackCoef::Int" with Int a number identifying the given parameter (used for point-kinetics reactivity calculation).
        """
        mots = name.split("::")
        if len(mots) == 1 and mots[0] == "fluidPower":
            self._medInterface.Set_puissance_fluide(field)
        elif len(mots) > 2 and mots[0] == "solidPower":
            materialNames = []
            for i in range(2, len(mots)):
                materialNames.append(mots[i])
            self._medInterface.Set_puissance_solide(field, mots[1], materialNames)
        elif len(mots) == 4 and (mots[0] == "setParamLambda" or mots[0] == "setParamCapa"):
            typeProp = 0
            if mots[0] == "setParamLambda":
                typeProp = THEDI.Type_propriete_thermique.LAMBDA
            else:
                typeProp = THEDI.Type_propriete_thermique.RHOCP
            self._medInterface.Set_parametres_divers_thermiques(field, mots[1], mots[2], typeProp, int(mots[3]))
        elif len(mots) == 2 and mots[0] == "feedbackCoef":
            self._medInterface.Set_coef_CR(field, int(mots[1]))
        else:
            raise Exception("THEDIDriver.setInputMEDField the field " + name + " cannot be set.")

    def getOutputFieldsNames(self):
        return list(self._outputFieldCorrespondence.keys())

    def getOutputMEDField(self, name):
        """! Return the MED field of name name extracted from the component.

        See PhysicsDriver.getOutputMEDField().

        Fields that can be returned :
        - "TEMPERATURE_LIQUIDE"
        - "TEMPERATURE_VAPEUR"
        - "TEMPERATURE_MOYENNE"
        - "MASSE_VOLUMIQUE"
        - "PRESSION"
        - "TAUX_DE_VIDE"
        - "VITESSE_MASSIQUE"
        - "VITESSE_LIQUIDE"
        - "VITESSE_VAPEUR"
        - "TITRE"
        - "ENERGIE_INTERNE"
        - "ENTHALPIE"
        - "FLUX_CRITIQUE_SUR_FLUX"
        - "T_PAROI"
        - "T_INTERNE"
        - "T_EFFECTIVE"
        """
        outputField = mc.MEDCouplingFieldDouble(mc.ON_CELLS, mc.ONE_TIME)
        if name in self._outputFieldCorrespondence.keys():
            self._medInterface.Get_champ(self._outputFieldCorrespondence[name], outputField)
            return outputField
        raise Exception("THEDIDriver.getOutputMEDField the field " + name + " is not available.")

    def setValue(self, name, value):
        raise Exception("THEDIDriver.setValue is not supported")

    def getValue(self, name):
        raise Exception("THEDIDriver.getValue is not supported")

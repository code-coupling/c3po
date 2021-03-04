# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contains the class CRONOS2Driver. """
from __future__ import print_function, division

import MEDCoupling
import Access
import MEDconvert
import MEDtsetpt

from C3PO.PhysicsDriver import PhysicsDriver
from TagClass import TagClass


class CRONOS2Driver(PhysicsDriver):
    """ This is the implementation of PhysicsDriver for CRONOS2. """

    def __init__(self):
        """ Builds a CRONOS2Driver object. """
        PhysicsDriver.__init__(self)
        self.isInit_ = False

        # CRONOS2 input file
        self.datafile_ = ""

        # Access session in python
        self.a_ = 0

        # name of MED fields
        self.tag_ = TagClass() 

        # physical time
        self.t_ = 0

        # time step for transient
        self.dt_ = 0

    def set_tag(self, tag):
        self.tag_ = tag

    def setDataFile(self, datafile):
        self.datafile_ = datafile

    def initialize(self):
        if not self.isInit_: 
            self.a_ = Access.Access()
            self.a_.begin(10000,0)
            self.isInit = True
            if bool(self.datafile_):
                self.a_.evalFile(self.datafile_)
            self.a_.eval("T_C3PO = TABLE: ; T_C3PO.'ITH' = 0 ; T_C3PO.'MED' = TABLE: ;")
            self.a_.eval("T_C3PO T_RES T_STR T_OPT = ICOCO_INITIALIZE T_IMP T_STR T_OPT T_RES T_C3PO ;") 
        return True

    def terminate(self):
        self.a_.eval("ICOCO_TERMINATE T_IMP T_STR T_OPT T_RES T_C3PO ;") 
        self.a_.eval("EDTIME: 'TOUT' ; MEMOIRE: -1 ; ARRET: ;")
        self.a_.end()        
        self.isInit_ = False
        return True

    def initTimeStep(self, dt):
        self.dt_ = dt
        self.a_.eval("T_C3PO.'DT' = "+"{:.3f}".format(dt)+" ;")
        self.a_.eval("T_C3PO T_RES T_STR T_OPT = ICOCO_INIT_TIME_STEP T_IMP T_STR T_OPT T_RES T_C3PO ;") 
        return True

    def presentTime(self):
        return self.t_ 

    def computeTimeStep(self):
        """ Description of the expected outputs for the ICOCO_COMPUTE_TIME_STEP gibiane subroutine """
        """ The time step (floating-point number) must be output in the variable T_C3PO.'DT' """
        """ The stop flag must be output as an integer in the variable T_C3PO.'STOP' """
        """ (because 'getTableBool' sadly does not exist in Access so 'getTableInt' is used instead) """
        """ T_C3PO.'STOP'==0 means FALSE (do not stop) and T_C3PO.'STOP'>0 means TRUE (please stop)"""

        self.a_.eval("T_C3PO.'PRESENT_TIME' = "+"{:.3f}".format(self.t_)+" ;")
        self.a_.eval("T_C3PO T_RES T_STR T_OPT = ICOCO_COMPUTE_TIME_STEP T_IMP T_STR T_OPT T_RES T_C3PO ;") 
        ptr = self.a_.getTabPtr("T_C3PO")
        dt = self.a_.getTableFloat(ptr,"DT")
        stop = bool(self.a_.getTableInt(ptr,"STOP"))
        return (dt, stop)

    def solveTimeStep(self):
        self.a_.eval("T_C3PO T_RES T_STR T_OPT = ICOCO_SOLVE_TIME_STEP T_IMP T_STR T_OPT T_RES T_C3PO ;") 
        return True

    def validateTimeStep(self):
        self.t_ = self.t_ + self.dt_ 
        self.a_.eval("T_C3PO.'PRESENT_TIME' = "+"{:.3f}".format(self.t_)+" ;")
        self.a_.eval("T_C3PO T_RES T_STR T_OPT = ICOCO_VALIDATE_TIME_STEP T_IMP T_STR T_OPT T_RES T_C3PO ;") 

    def abortTimeStep(self):
        if self.dt_ > 0:
            raise Exception("CRONOS2Driver.abortTimeStep: NotImplemented.")
        else:
            pass

    def getOutputMEDField(self, name):
        if name == self.tag_.PUIS_:
            self.a_.eval("GR__ = CGRILLE: 0 T_STR.'DOMAINE' ; MESH_sortie = MED_GRID_2_MESH: GR__ ;")  
            self.a_.eval("pcoeurMW = T_OPT.'PUIS_RELATIVE' * T_OPT.'MW' ;")     
            self.a_.eval("PUIS_MW FLUX_ncm2s = NORMALISATION: 0 'PUISSANCE COEUR' pcoeurMW T_STR.'FLUXINT' T_STR.'PUIS' T_STR.'DOMAINE' ;")          
            self.a_.eval("GRILLE_sortie = CGRILLE: 0 PUIS_MW T_STR.'DOMAINE' ;")      
            self.a_.eval("GRILLE_sortie = FONCTION_GRILLE: 0 GRILLE_sortie 'PUISSANCE INTEGREE' 'FINAL' 'PUISSANCE_W' ;")         
            self.a_.eval("GRILLE_sortie = 1.0E6 * GRILLE_sortie ;")      
            self.a_.eval("FIELD_sortie = MED_GRID_2_FIELD: GRILLE_sortie MESH_sortie ;")
            myCppPtr = self.a_.getCppPtr("FIELD_sortie")
            field_output = MEDconvert.void2field(myCppPtr)
            field_output.setNature(MEDCoupling.Integral)
            return field_output
        else:
            raise Exception("CRONOS2Driver.getOutputMEDField Only " + self.tag_.PUIS_ + " output available.")

    def getInputMEDFieldTemplate(self, name):
        if ((name == self.tag_.TECO_) or (name == self.tag_.DMOD_)):
            self.a_.eval("GR__ = CGRILLE: 0 T_STR.'DOMAINE' ; MESH_sortie = MED_GRID_2_MESH: GR__ ;")  
            self.a_.eval("name = '"+str(name)+"' ;")
            self.a_.eval("GRILLE_sortie = CGRILLE: 0 T_STR.'TCOMP' T_STR.'DOMAINE' name ;")
            self.a_.eval("FIELD_sortie = MED_GRID_2_FIELD: GRILLE_sortie MESH_sortie ;")
            myCppPtr = self.a_.getCppPtr("FIELD_sortie")
            field_template = MEDconvert.void2field(myCppPtr)
            return field_template
        else:
            raise Exception("CRONOS2Driver.getIntputMEDFieldTemplate Only " + self.tag_.TECO_ + " and " + self.tag_.DMOD_ + " template available.")
 
    def setInputMEDField(self, name, field):
        if (name == self.tag_.TECO_ or name == self.tag_.DMOD_):
            self.a_.eval("T_C3PO.'ITH' = T_C3PO.'ITH' + 1 ; ITH = T_C3PO.'ITH' ;")
            intField = MEDtsetpt.SaphGetIdFromPtr(field) 
            self.a_.eval("T_C3PO.'MED'.ITH = MED_FIELD_SAPH: "+str(intField)+" ;") 
            self.a_.eval("GRILLE_ref = CGRILLE: 0 T_STR.'TCOMP' T_STR.'DOMAINE' ;")
            self.a_.eval("GRILLE_sortie = MED_FIELD_2_GRID: GRILLE_ref T_C3PO.'MED'.ITH ;")
            self.a_.eval("name = '"+str(name)+"' ;")
            self.a_.eval("T_STR.'TCOMP' = CGRILLE2C: 0 T_STR.'TCOMP' T_STR.'DOMAINE' GRILLE_sortie name ;")
        else:
            raise Exception("CRONOS2Driver.setInputMEDField Only " + self.tag_.TECO_ + " and " + self.tag_.DMOD_ + " input possible.")
 

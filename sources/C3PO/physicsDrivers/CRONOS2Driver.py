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

class ParamKey:
    """ Keys for the dictionary of the names of CRONOS2 parameters in PARAM-type structures """
    TECO = "TECO"
    DMOD = "DMOD"
    PUIS = "PUIS"

class TableKey:
    """ Keys for the dictionary of the names of CRONOS2 tables """
    PARAM = "PARAM"
    DOMAINE = "DOMAINE"
    FLUXINT = "FLUXINT"
    PUISS = "PUISS"
    MW = "MW"
    PUISS_RELATIVE = "PUISS_RELATIVE" 

class CRONOS2Driver(PhysicsDriver):
    """ This is the implementation of PhysicsDriver for CRONOS2. """

    def __init__(self):
        """ Builds a CRONOS2Driver object. """
        PhysicsDriver.__init__(self)
        self.isInit_ = False

        # CRONOS2 input file
        self.dataFile_ = ""

        # Access session in python
        self.a_ = 0

        # physical time
        self.t_ = 0

        # time step for transient
        self.dt_ = 0

        # Dictionary of names of CRONOS2 parameters in PARAM structures
        # The keys are defined in ParamKey and are used in C3PO coupling scripts for the names of MED fields
        # The values are set in "initialize" for use in gibiane instructions of CRONOS2 
        self.paramDict_ = {}

        # Dictionary of names of internal CRONOS2 tables 
        # The keys are defined in TableKey        
        # The values are set in "initialize" for use in gibiane instructions of CRONOS2 
        self.tableDict_ = {}

    def setDictionaries(self, paramDict, tableDict):
        """ This function is reserved for advanced use only ;
            do not use setDictionaries unless you know exactly what you are doing"""
        self.paramDict_ = paramDict
        self.tableDict_ = tableDict

    def setDataFile(self, dataFile):
        self.dataFile_ = dataFile

    def initialize(self):
        if not self.isInit_: 
            # start a session of python Access for CRONOS2
            self.a_ = Access.Access()
            self.a_.begin(10000,0)
            self.isInit = True
            # run a CRONOS2 input file if defined
            if bool(self.dataFile_):
                self.a_.evalFile(self.dataFile_)
            # initialize T_C3PO table  
            self.a_.eval("T_C3PO = TABLE: ; T_C3PO.'ITH' = 0 ; T_C3PO.'MED' = TABLE: ;")
            self.a_.eval("T_C3PO.'paramDict' = TABLE: ; T_C3PO.'tableDict' = TABLE: ; ")
            self.a_.eval("T_C3PO.'paramDict'.'TECO' = 'TECO' ; ")
            self.a_.eval("T_C3PO.'paramDict'.'DMOD' = 'DMOD' ; ")
            self.a_.eval("T_C3PO.'paramDict'.'PUIS' = 'PUISSANCE_W' ; ")
            self.a_.eval("T_C3PO.'tableDict'.'PARAM' = 'TCOMP' ; ")
            self.a_.eval("T_C3PO.'tableDict'.'DOMAINE' = 'DOMAINE' ; ")
            self.a_.eval("T_C3PO.'tableDict'.'FLUXINT' = 'FLUXINT' ; ")
            self.a_.eval("T_C3PO.'tableDict'.'PUISS' = 'PUIS' ; ")
            self.a_.eval("T_C3PO.'tableDict'.'MW' = 'MW' ; ")
            self.a_.eval("T_C3PO.'tableDict'.'PUISS_RELATIVE' = 'PUIS_RELATIVE' ; ")
            # if need be, modify/add relevant T_C3PO variables inside ICOCO_INITIALIZE
            self.a_.eval("T_C3PO T_RES T_STR T_OPT = ICOCO_INITIALIZE T_IMP T_STR T_OPT T_RES T_C3PO ;") 
            # initialize dictionary values
            self.a_.eval("STRING_VALUE = T_C3PO.'paramDict'.'TECO' ;")
            self.paramDict_[ParamKey.TECO] = self.a_.getString("STRING_VALUE") 
            self.a_.eval("STRING_VALUE = T_C3PO.'paramDict'.'DMOD' ;")
            self.paramDict_[ParamKey.DMOD] = self.a_.getString("STRING_VALUE") 
            self.a_.eval("STRING_VALUE = T_C3PO.'paramDict'.'PUIS' ;")
            self.paramDict_[ParamKey.PUIS] = self.a_.getString("STRING_VALUE") 
            self.a_.eval("STRING_VALUE = T_C3PO.'tableDict'.'PARAM' ;")
            self.tableDict_[TableKey.PARAM] = self.a_.getString("STRING_VALUE") 
            self.a_.eval("STRING_VALUE = T_C3PO.'tableDict'.'DOMAINE' ;")
            self.tableDict_[TableKey.DOMAINE] = self.a_.getString("STRING_VALUE") 
            self.a_.eval("STRING_VALUE = T_C3PO.'tableDict'.'FLUXINT' ;")
            self.tableDict_[TableKey.FLUXINT] = self.a_.getString("STRING_VALUE") 
            self.a_.eval("STRING_VALUE = T_C3PO.'tableDict'.'PUISS' ;")
            self.tableDict_[TableKey.PUISS] = self.a_.getString("STRING_VALUE") 
            self.a_.eval("STRING_VALUE = T_C3PO.'tableDict'.'MW' ;")
            self.tableDict_[TableKey.MW] = self.a_.getString("STRING_VALUE") 
            self.a_.eval("STRING_VALUE = T_C3PO.'tableDict'.'PUISS_RELATIVE' ;")
            self.tableDict_[TableKey.PUISS_RELATIVE] = self.a_.getString("STRING_VALUE") 
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
        """ Description of the expected outputs for the ICOCO_COMPUTE_TIME_STEP gibiane subroutine:
        The time step (floating-point number) must be output in the variable T_C3PO.'DT' 
        The stop flag (boolean) must be output in the variable T_C3PO.'STOP' """

        self.a_.eval("T_C3PO.'PRESENT_TIME' = "+"{:.3f}".format(self.t_)+" ;")
        self.a_.eval("T_C3PO T_RES T_STR T_OPT = ICOCO_COMPUTE_TIME_STEP T_IMP T_STR T_OPT T_RES T_C3PO ;") 
        self.a_.eval("TIME_STEP = T_C3PO.'DT' ; STOP_FLAG = T_C3PO.'STOP' ;")
        dt = self.a_.getFloat("TIME_STEP")
        stop = bool(self.a_.getBool("STOP_FLAG"))
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
        if name == ParamKey.PUIS:
            DOMAINE = self.tableDict_[TableKey.DOMAINE]
            PUISS_RELATIVE = self.tableDict_[TableKey.PUISS_RELATIVE]
            MW = self.tableDict_[TableKey.MW] 
            FLUXINT = self.tableDict_[TableKey.FLUXINT] 
            PUISS = self.tableDict_[TableKey.PUISS] 
            PUIS = self.paramDict_[ParamKey.PUIS] 
            self.a_.eval("GR__ = CGRILLE: 0 T_STR.'"+DOMAINE+"' ;")
            self.a_.eval("mesh_out = MED_GRID_2_MESH: GR__ ;") 
            self.a_.eval("PcoreMW = T_OPT.'"+PUISS_RELATIVE+"' * T_OPT.'"+MW+"' ;") 
            self.a_.eval("PUIS_MW FLUX_ncm2s = NORMALISATION: 0 'PUISSANCE COEUR' PcoreMW T_STR.'"+FLUXINT+"' T_STR.'"+PUISS+"' T_STR.'"+DOMAINE+"' ;") 
            self.a_.eval("grid_out = CGRILLE: 0 PUIS_MW T_STR.'"+DOMAINE+"' ;") 
            self.a_.eval("grid_out = FONCTION_GRILLE: 0 grid_out 'PUISSANCE INTEGREE' 'FINAL' '"+PUIS+"' ;") 
            self.a_.eval("grid_out = 1.0E6 * grid_out ;") 
            self.a_.eval("field_out = MED_GRID_2_FIELD: grid_out mesh_out ;")
            myCppPtr = self.a_.getCppPtr("field_out")
            field_output = MEDconvert.void2field(myCppPtr)
            field_output.setNature(MEDCoupling.Integral)
            return field_output
        else:
            raise Exception("CRONOS2Driver.getOutputMEDField Only "+ParamKey.PUIS+" output available.")

    def getInputMEDFieldTemplate(self, name):
        if ((name == ParamKey.TECO) or (name == ParamKey.DMOD)):
            DOMAINE = self.tableDict_[TableKey.DOMAINE]
            PARAM = self.tableDict_[TableKey.PARAM]
            self.a_.eval("GR__ = CGRILLE: 0 T_STR.'"+DOMAINE+"' ;")
            self.a_.eval("mesh_out = MED_GRID_2_MESH: GR__ ;")  
            self.a_.eval("name = '"+self.paramDict_[name]+"' ;")
            self.a_.eval("grid_out = CGRILLE: 0 T_STR.'"+PARAM+"' T_STR.'"+DOMAINE+"' name ;")
            self.a_.eval("field_out = MED_GRID_2_FIELD: grid_out mesh_out ;")
            myCppPtr = self.a_.getCppPtr("field_out")
            field_template = MEDconvert.void2field(myCppPtr)
            return field_template
        else:
            raise Exception("CRONOS2Driver.getIntputMEDFieldTemplate Only "+ParamKey.TECO+" and "+ParamKey.DMOD+" template available.")
 
    def setInputMEDField(self, name, field):
        if ((name == ParamKey.TECO) or (name == ParamKey.DMOD)):
            DOMAINE = self.tableDict_[TableKey.DOMAINE]
            PARAM = self.tableDict_[TableKey.PARAM]
            self.a_.eval("T_C3PO.'ITH' = T_C3PO.'ITH' + 1 ; ITH = T_C3PO.'ITH' ;")
            intField = MEDtsetpt.SaphGetIdFromPtr(field) 
            self.a_.eval("T_C3PO.'MED'.ITH = MED_FIELD_SAPH: "+str(intField)+" ;") 
            self.a_.eval("grid_ref = CGRILLE: 0 T_STR.'"+PARAM+"' T_STR.'"+DOMAINE+"' ;")
            self.a_.eval("grid_out = MED_FIELD_2_GRID: grid_ref T_C3PO.'MED'.ITH ;")
            self.a_.eval("name = '"+self.paramDict_[name]+"' ;")
            self.a_.eval("T_STR.'"+PARAM+"' = CGRILLE2C: 0 T_STR.'"+PARAM+"' T_STR.'"+DOMAINE+"' grid_out name ;")
        else:
            raise Exception("CRONOS2Driver.setInputMEDField Only "+ParamKey.TECO+" and "+ParamKey.DMOD+" input possible.")
 

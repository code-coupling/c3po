# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class CRONOS2Driver. """
from __future__ import print_function, division

import c3po.medcoupling_compat as mc
import Access
import MEDconvert
import MEDtsetpt

from c3po.PhysicsDriver import PhysicsDriver


class ParamKey:
    """! Keys for the dictionary of the names of CRONOS2 parameters in PARAM-type structures """
    TECO = "TECO"
    DMOD = "DMOD"
    TMOD = "TMOD"
    PUIS = "PUIS"
    inputKeys = [TECO, DMOD, TMOD]
    outputKeys = [PUIS]


class CRONOS2Driver(PhysicsDriver):
    """! This is the implementation of PhysicsDriver for CRONOS2. """

    def __init__(self):
        """! Build a CRONOS2Driver object. """
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

    def setParamDict(self, paramDict):
        """! Set a new dictionary of names of CRONOS2 parameters in PARAM structures.

        This function is reserved for advanced use only ;
        do not use it unless you know exactly what you are doing.
        """
        self.paramDict_ = paramDict

    def setDataFile(self, dataFile):
        """! See PhysicsDriver.setDataFile(). """
        self.dataFile_ = dataFile

    def initialize(self):
        """! See PhysicsDriver.initialize(). """
        if not self.isInit_:
            # start a session of python Access for CRONOS2
            self.a_ = Access.Access()
            self.a_.begin(10000, 0)
            self.isInit_ = True
            # run a CRONOS2 input file if defined
            if bool(self.dataFile_):
                self.a_.evalFile(self.dataFile_)
            # initialize T_C3PO table
            self.a_.eval("T_C3PO = TABLE: ; T_c3po.'ITH' = 0 ; T_c3po.'MED' = TABLE: ;")
            self.a_.eval("T_c3po.'paramDict' = TABLE: ; T_c3po.'value' = TABLE: ;")
            self.a_.eval("T_c3po.'paramDict'.'TECO' = 'TECO' ; ")
            self.a_.eval("T_c3po.'paramDict'.'DMOD' = 'DMOD' ; ")
            self.a_.eval("T_c3po.'paramDict'.'TMOD' = 'TMOD' ; ")
            self.a_.eval("T_c3po.'paramDict'.'PUIS' = 'PUISSANCE_W' ; ")
            # if need be, modify/add relevant T_C3PO variables inside ICOCO_INITIALIZE
            self.a_.eval("T_C3PO T_RES T_STR T_OPT = ICOCO_INITIALIZE T_IMP T_STR T_OPT T_RES T_C3PO ;")
            # initialize dictionary values
            tc3po_ptr = self.a_.getTabPtr('T_C3PO')
            param_ptr = self.a_.getTableTabPtr(tc3po_ptr, 'paramDict')
            self.paramDict_[ParamKey.TECO] = self.a_.getTableString(param_ptr, 'TECO')
            self.paramDict_[ParamKey.DMOD] = self.a_.getTableString(param_ptr, 'DMOD')
            self.paramDict_[ParamKey.TMOD] = self.a_.getTableString(param_ptr, 'TMOD')
            self.paramDict_[ParamKey.PUIS] = self.a_.getTableString(param_ptr, 'PUIS')
        return True

    def terminate(self):
        """! See PhysicsDriver.terminate(). """
        self.a_.eval("ICOCO_TERMINATE T_IMP T_STR T_OPT T_RES T_C3PO ;")
        self.a_.eval("EDTIME: 'TOUT' ; MEMOIRE: -1 ; ARRET: ;")
        self.a_.end()
        self.isInit_ = False
        self.dataFile_ = ""
        self.t_ = 0
        self.dt_ = 0
        self.paramDict_ = {}

    def initTimeStep(self, dt):
        """! See PhysicsDriver.initTimeStep(). """
        self.dt_ = dt
        self.a_.eval("T_c3po.'DT' = " + "{:.5f}".format(dt) + " ;")
        self.a_.eval("T_C3PO T_RES T_STR T_OPT = ICOCO_INIT_TIME_STEP T_IMP T_STR T_OPT T_RES T_C3PO ;")
        return True

    def presentTime(self):
        """! See PhysicsDriver.presentTime(). """
        return self.t_

    def computeTimeStep(self):
        """! See PhysicsDriver.computeTimeStep().

        Description of the expected outputs for the ICOCO_COMPUTE_TIME_STEP gibiane subroutine:

        - The time step (floating-point number) must be output in the variable T_c3po.'DT'

        - The stop flag (boolean) must be output in the variable T_c3po.'STOP'
        """

        self.a_.eval("T_c3po.'PRESENT_TIME' = " + "{:.5f}".format(self.t_) + " ;")
        self.a_.eval("T_C3PO T_RES T_STR T_OPT = ICOCO_COMPUTE_TIME_STEP T_IMP T_STR T_OPT T_RES T_C3PO ;")
        self.a_.eval("TIME_STEP = T_c3po.'DT' ; STOP_FLAG = T_c3po.'STOP' ;")
        dt = self.a_.getFloat("TIME_STEP")
        stop = bool(self.a_.getBool("STOP_FLAG"))
        return (dt, stop)

    def solveTimeStep(self):
        """! See PhysicsDriver.solveTimeStep(). """
        self.a_.eval("T_C3PO T_RES T_STR T_OPT = ICOCO_SOLVE_TIME_STEP T_IMP T_STR T_OPT T_RES T_C3PO ;")
        return True

    def validateTimeStep(self):
        """! See PhysicsDriver.validateTimeStep(). """
        self.t_ = self.t_ + self.dt_
        self.a_.eval("T_c3po.'PRESENT_TIME' = " + "{:.5f}".format(self.t_) + " ;")
        self.a_.eval("T_C3PO T_RES T_STR T_OPT = ICOCO_VALIDATE_TIME_STEP T_IMP T_STR T_OPT T_RES T_C3PO ;")

    def abortTimeStep(self):
        """! See PhysicsDriver.abortTimeStep(). """
        if self.dt_ > 0:
            raise Exception("CRONOS2Driver.abortTimeStep: NotImplemented.")
        else:
            pass

    def getOutputMEDField(self, name):
        """! See PhysicsDriver.getOutputMEDField().

        The gibiane subroutine ICOCO_GET_OUTPUT_MEDFIELD :

        - takes as input the name of the MED field in the string T_c3po.'name' ;

        - returns the required MED field in the variable T_c3po.'field_out' of type MEDFIELD.
        """

        if (name in ParamKey.outputKeys):
            self.a_.eval("T_c3po.'name' = '" + self.paramDict_[name] + "' ;")
            self.a_.eval("T_C3PO T_RES T_STR T_OPT = ICOCO_GET_OUTPUT_MEDFIELD T_IMP T_STR T_OPT T_RES T_C3PO ;")
            self.a_.eval("field_out = T_c3po.'field_out' ;")
            myCppPtr = self.a_.getCppPtr("field_out")
            field_output = MEDconvert.void2field(myCppPtr)
            field_output.setNature(mc.ExtensiveMaximum)  # ExtensiveMaximum interpolation of extensive variables
            return field_output
        else:
            raise Exception("CRONOS2Driver.getOutputMEDField Only " + str(ParamKey.outputKeys) + " output available but name='" + name + "'.")

    def getInputMEDFieldTemplate(self, name):
        """! See PhysicsDriver.getInputMEDFieldTemplate().

        The gibiane subroutine ICOCO_GET_INPUT_MEDFIELD_TEMPLATE :

        - takes as input the name of the MED field template in the string T_c3po.'name' ;

        - returns the required MED field template in the variable T_c3po.'field_out' of type MEDFIELD.
        """

        if (name in ParamKey.inputKeys):
            self.a_.eval("T_c3po.'name' = '" + self.paramDict_[name] + "' ;")
            self.a_.eval("T_C3PO T_RES T_STR T_OPT = ICOCO_GET_INPUT_MEDFIELD_TEMPLATE T_IMP T_STR T_OPT T_RES T_C3PO ;")
            self.a_.eval("field_out = T_c3po.'field_out' ;")
            myCppPtr = self.a_.getCppPtr("field_out")
            field_template = MEDconvert.void2field(myCppPtr)
            field_template.setNature(mc.IntensiveMaximum)  # IntensiveMaximum interpolation of intensive variables
            return field_template
        else:
            raise Exception("CRONOS2Driver.getIntputMEDFieldTemplate Only " + str(ParamKey.inputKeys) + " template available but name='" + name + "'.")

    def setInputMEDField(self, name, field):
        """! See PhysicsDriver.setInputMEDField().

        The gibiane subroutine ICOCO_SET_INPUT_MEDFIELD :

        - takes as input the name of the MED field in the string T_c3po.'name' ;

        - takes as input the MED field in the variable T_c3po.'MED'.ITH of type MEDFIELD ;

        - sorts away the MED field in the appropriate PARAM structures of CRONOS2.
        """

        if (name in ParamKey.inputKeys):
            field.setName(self.paramDict_[name])
            self.a_.eval("T_c3po.'ITH' = T_c3po.'ITH' + 1 ; ITH = T_c3po.'ITH' ;")
            intField = MEDtsetpt.SaphGetIdFromPtr(field)
            self.a_.eval("T_c3po.'MED'.ITH = MED_FIELD_SAPH: " + str(intField) + " ;")
            self.a_.eval("T_c3po.'name' = '" + self.paramDict_[name] + "' ;")
            self.a_.eval("T_C3PO T_RES T_STR T_OPT = ICOCO_SET_INPUT_MEDFIELD T_IMP T_STR T_OPT T_RES T_C3PO ;")
        else:
            raise Exception("CRONOS2Driver.setInputMEDField Only " + str(ParamKey.inputKeys) + " input possible but name='" + name + "'.")

    def setValue(self, name, value):
        """! See PhysicsDriver.setValue().

        The gibiane subroutine ICOCO_SET_VALUE :

        - takes as input the name of the value in the string T_c3po.'name' ;

        - takes as input the value stored in the table T_c3po.'value' with the index name ;

        - sorts away the value in the appropriate data structures of CRONOS2.
        """

        self.a_.eval("T_c3po.'name' = '" + name + "' ;")
        self.a_.eval("T_c3po.'value'.'" + name + "' = " + "{:.5f}".format(value) + " ;")
        self.a_.eval("T_C3PO T_RES T_STR T_OPT = ICOCO_SET_VALUE T_IMP T_STR T_OPT T_RES T_C3PO ;")

    def getValue(self, name):
        """! See PhysicsDriver.getValue().

        The gibiane subroutine ICOCO_GET_VALUE :

        - takes as input the name of the value in the string T_c3po.'name' ;

        - returns the required floating number value in the table T_c3po.'value' at the index name.
        """

        self.a_.eval("T_c3po.'name' = '" + name + "' ;")
        self.a_.eval("T_C3PO T_RES T_STR T_OPT = ICOCO_GET_VALUE T_IMP T_STR T_OPT T_RES T_C3PO ;")
        self.a_.eval("return_value = T_c3po.'value'.'" + name + "' ;")
        return self.a_.getFloat("return_value")
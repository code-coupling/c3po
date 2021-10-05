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

import Access
import MEDconvert
import MEDtsetpt

import c3po.medcouplingCompat as mc
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
        self._isInit = False

        # CRONOS2 input file
        self._dataFile = ""

        # Access session in python
        self._access = 0

        # physical time
        self._time = 0

        # time step for transient
        self._dt = 0

        # Dictionary of names of CRONOS2 parameters in PARAM structures
        # The keys are defined in ParamKey and are used in C3PO coupling scripts for the names of MED fields
        # The values are set in "initialize" for use in gibiane instructions of CRONOS2
        self._paramDict = {}

        self._stationaryMode = False

    def setParamDict(self, paramDict):
        """! Set a new dictionary of names of CRONOS2 parameters in PARAM structures.

        This function is reserved for advanced use only ;
        do not use it unless you know exactly what you are doing.
        """
        self._paramDict = paramDict

    def getICOCOVersion(self):
        return '2.0'

    def getMEDCouplingMajorVersion(self):
        return mc.MEDCouplingVersionMajMinRel()[0]

    def isMEDCoupling64Bits(self):
        return mc.MEDCouplingSizeOfIDs() == 64

    def setDataFile(self, datafile):
        """! See PhysicsDriver.setDataFile(). """
        self._dataFile = datafile

    def initialize(self):
        """! See PhysicsDriver.initialize(). """
        if not self._isInit:
            # start a session of python Access for CRONOS2
            self._access = Access.Access()
            self._access.begin(10000, 0)
            self._isInit = True
            # run a CRONOS2 input file if defined
            if bool(self._dataFile):
                self._access.evalFile(self._dataFile)
            # initialize T_C3PO table
            self._access.eval("T_C3PO = TABLE: ; T_C3PO.'ITH' = 0 ; T_C3PO.'MED' = TABLE: ;")
            self._access.eval("T_C3PO.'paramDict' = TABLE: ; T_C3PO.'value' = TABLE: ;")
            self._access.eval("T_C3PO.'paramDict'.'TECO' = 'TECO' ; ")
            self._access.eval("T_C3PO.'paramDict'.'DMOD' = 'DMOD' ; ")
            self._access.eval("T_C3PO.'paramDict'.'TMOD' = 'TMOD' ; ")
            self._access.eval("T_C3PO.'paramDict'.'PUIS' = 'PUISSANCE_W' ; ")
            # check for existence of basic CRONOS tables
            self._access.eval("WARNING_T_STR = FAUX ; WARNING_T_OPT = FAUX ; WARNING_T_RES = FAUX ; WARNING_T_IMP = FAUX; ")
            self._access.eval("NONSI (EXISTE T_STR) ; WARNING_T_STR = VRAI ; T_STR = TABLE: ; FINSI ;")
            self._access.eval("NONSI (EXISTE T_OPT) ; WARNING_T_OPT = VRAI ; T_OPT = TABLE: ; FINSI ;")
            self._access.eval("NONSI (EXISTE T_RES) ; WARNING_T_RES = VRAI ; T_RES = TABLE: ; FINSI ;")
            self._access.eval("NONSI (EXISTE T_IMP) ; WARNING_T_IMP = VRAI ; T_IMP = TABLE: ; FINSI ;")
            if bool(self._access.getBool("WARNING_T_STR")):
                self._access.eval("WRITE: 'LISCONS' 'WARNING: VARIABLE T_STR DOES NOT EXIST, TABLE T_STR IS CREATED' ; ")
            if bool(self._access.getBool("WARNING_T_OPT")):
                self._access.eval("WRITE: 'LISCONS' 'WARNING: VARIABLE T_OPT DOES NOT EXIST, TABLE T_OPT IS CREATED' ; ")
            if bool(self._access.getBool("WARNING_T_RES")):
                self._access.eval("WRITE: 'LISCONS' 'WARNING: VARIABLE T_RES DOES NOT EXIST, TABLE T_RES IS CREATED' ; ")
            if bool(self._access.getBool("WARNING_T_IMP")):
                self._access.eval("WRITE: 'LISCONS' 'WARNING: VARIABLE T_IMP DOES NOT EXIST, TABLE T_IMP IS CREATED' ; ")
            # if need be, modify/add relevant T_C3PO variables inside ICOCO_INITIALIZE
            self._access.eval("T_C3PO T_RES T_STR T_OPT = ICOCO_INITIALIZE T_IMP T_STR T_OPT T_RES T_C3PO ;")
            # initialize dictionary values
            tc3poPtr = self._access.getTabPtr('T_C3PO')
            paramPtr = self._access.getTableTabPtr(tc3poPtr, 'paramDict')
            self._paramDict[ParamKey.TECO] = self._access.getTableString(paramPtr, 'TECO')
            self._paramDict[ParamKey.DMOD] = self._access.getTableString(paramPtr, 'DMOD')
            self._paramDict[ParamKey.TMOD] = self._access.getTableString(paramPtr, 'TMOD')
            self._paramDict[ParamKey.PUIS] = self._access.getTableString(paramPtr, 'PUIS')
        return True

    def terminate(self):
        """! See PhysicsDriver.terminate(). """
        self._access.eval("ICOCO_TERMINATE T_IMP T_STR T_OPT T_RES T_C3PO ;")
        self._access.eval("EDTIME: 'TOUT' ; MEMOIRE: -1 ; ARRET: ;")
        self._access.end()
        self._isInit = False
        self._dataFile = ""
        self._time = 0
        self._dt = 0
        self._paramDict = {}

    def initTimeStep(self, dt):
        """! See PhysicsDriver.initTimeStep(). """
        self._dt = dt
        self._access.eval("T_C3PO.'DT' = " + "{:.5f}".format(dt) + " ;")
        self._access.eval("T_C3PO T_RES T_STR T_OPT = ICOCO_INIT_TIME_STEP T_IMP T_STR T_OPT T_RES T_C3PO ;")
        return True

    def presentTime(self):
        """! See PhysicsDriver.presentTime(). """
        return self._time

    def computeTimeStep(self):
        """! See PhysicsDriver.computeTimeStep().

        Description of the expected outputs for the ICOCO_COMPUTE_TIME_STEP gibiane subroutine:

        - The time step (floating-point number) must be output in the variable T_C3PO.'DT'

        - The stop flag (boolean) must be output in the variable T_C3PO.'STOP'
        """

        self._access.eval("T_C3PO.'PRESENT_TIME' = " + "{:.5f}".format(self._time) + " ;")
        self._access.eval("T_C3PO T_RES T_STR T_OPT = ICOCO_COMPUTE_TIME_STEP T_IMP T_STR T_OPT T_RES T_C3PO ;")
        self._access.eval("TIME_STEP = T_C3PO.'DT' ; STOP_FLAG = T_C3PO.'STOP' ;")
        dt = self._access.getFloat("TIME_STEP")
        dt = round(dt,5) # avoid precision problems due to float, e.g 0.01 != 0.009999999748
        stop = bool(self._access.getBool("STOP_FLAG"))
        return (dt, stop)

    def solveTimeStep(self):
        """! See PhysicsDriver.solveTimeStep(). """
        self._access.eval("T_C3PO T_RES T_STR T_OPT = ICOCO_SOLVE_TIME_STEP T_IMP T_STR T_OPT T_RES T_C3PO ;")
        return True

    def validateTimeStep(self):
        """! See PhysicsDriver.validateTimeStep(). """
        self._time = self._time + self._dt
        self._access.eval("T_C3PO.'PRESENT_TIME' = " + "{:.5f}".format(self._time) + " ;")
        self._access.eval("T_C3PO T_RES T_STR T_OPT = ICOCO_VALIDATE_TIME_STEP T_IMP T_STR T_OPT T_RES T_C3PO ;")

    def setStationaryMode(self, stationaryMode):
        self._stationaryMode = stationaryMode

    def getStationaryMode(self):
        return self._stationaryMode

    def abortTimeStep(self):
        """! See PhysicsDriver.abortTimeStep(). """
        if self._dt > 0:
            raise Exception("CRONOS2Driver.abortTimeStep: NotImplemented.")

    def resetTime(self, time_):
        self._time = time_

    def getOutputMEDDoubleField(self, name):
        """! See PhysicsDriver.getOutputMEDDoubleField().

        The gibiane subroutine ICOCO_GET_OUTPUT_MEDFIELD :

        - takes as input the name of the MED field in the string T_C3PO.'name' ;

        - returns the required MED field in the variable T_C3PO.'field_out' of type MEDFIELD.
        """

        if name in ParamKey.outputKeys:
            self._access.eval("T_C3PO.'name' = '" + self._paramDict[name] + "' ;")
            self._access.eval("T_C3PO T_RES T_STR T_OPT = ICOCO_GET_OUTPUT_MEDFIELD T_IMP T_STR T_OPT T_RES T_C3PO ;")
            self._access.eval("field_out = T_C3PO.'field_out' ;")
            myCppPtr = self._access.getCppPtr("field_out")
            fieldOutput = MEDconvert.void2field(myCppPtr)
            # Do not return a field pointer to gibiane memory, return a deep copy instead
            fieldReturn = fieldOutput.deepCpy()
            fieldReturn.setNature(mc.ExtensiveMaximum)  # ExtensiveMaximum interpolation of extensive variables
            return fieldReturn
        raise Exception("CRONOS2Driver.getOutputMEDField Only " + str(ParamKey.outputKeys) + " output available but name='" + name + "'.")

    def getInputMEDDoubleFieldTemplate(self, name):
        """! See PhysicsDriver.getInputMEDDoubleFieldTemplate().

        The gibiane subroutine ICOCO_GET_INPUT_MEDFIELD_TEMPLATE :

        - takes as input the name of the MED field template in the string T_C3PO.'name' ;

        - returns the required MED field template in the variable T_C3PO.'field_out' of type MEDFIELD.
        """

        if name in ParamKey.inputKeys:
            self._access.eval("T_C3PO.'name' = '" + self._paramDict[name] + "' ;")
            self._access.eval("T_C3PO T_RES T_STR T_OPT = ICOCO_GET_INPUT_MEDFIELD_TEMPLATE T_IMP T_STR T_OPT T_RES T_C3PO ;")
            self._access.eval("field_out = T_C3PO.'field_out' ;")
            myCppPtr = self._access.getCppPtr("field_out")
            fieldTemplate = MEDconvert.void2field(myCppPtr)
            # Do not return a field pointer to gibiane memory, return a deep copy instead
            fieldReturn = fieldTemplate.deepCpy()
            fieldReturn.setNature(mc.IntensiveMaximum)  # IntensiveMaximum interpolation of intensive variables
            return fieldReturn
        raise Exception("CRONOS2Driver.getIntputMEDFieldTemplate Only " + str(ParamKey.inputKeys) + " template available but name='" + name + "'.")

    def setInputMEDDoubleField(self, name, field):
        """! See PhysicsDriver.setInputMEDDoubleField().

        The gibiane subroutine ICOCO_SET_INPUT_MEDFIELD :

        - takes as input the name of the MED field in the string T_C3PO.'name' ;

        - takes as input the MED field in the variable T_C3PO.'MED'.ITH of type MEDFIELD ;

        - sorts away the MED field in the appropriate PARAM structures of CRONOS2.
        """

        if name in ParamKey.inputKeys:
            field.setName(self._paramDict[name])
            self._access.eval("T_C3PO.'ITH' = T_C3PO.'ITH' + 1 ; ITH = T_C3PO.'ITH' ;")
            intField = MEDtsetpt.SaphGetIdFromPtr(field)
            self._access.eval("T_C3PO.'MED'.ITH = MED_FIELD_SAPH: " + str(intField) + " ;")
            self._access.eval("T_C3PO.'name' = '" + self._paramDict[name] + "' ;")
            self._access.eval("T_C3PO T_RES T_STR T_OPT = ICOCO_SET_INPUT_MEDFIELD T_IMP T_STR T_OPT T_RES T_C3PO ;")
        else:
            raise Exception("CRONOS2Driver.setInputMEDField Only " + str(ParamKey.inputKeys) + " input possible but name='" + name + "'.")

    def setInputDoubleValue(self, name, value):
        """! See PhysicsDriver.setInputDoubleValue().

        The gibiane subroutine ICOCO_SET_VALUE :

        - takes as input the name of the value in the string T_C3PO.'name' ;

        - takes as input the value stored in the table T_C3PO.'value' with the index name ;

        - sorts away the value in the appropriate data structures of CRONOS2.
        """

        self._access.eval("T_C3PO.'name' = '" + name + "' ;")
        self._access.eval("T_C3PO.'value'.'" + name + "' = " + "{:.5f}".format(value) + " ;")
        self._access.eval("T_C3PO T_RES T_STR T_OPT = ICOCO_SET_VALUE T_IMP T_STR T_OPT T_RES T_C3PO ;")

    def getOutputDoubleValue(self, name):
        """! See PhysicsDriver.getOutputDoubleValue().

        The gibiane subroutine ICOCO_GET_VALUE :

        - takes as input the name of the value in the string T_C3PO.'name' ;

        - returns the required floating number value in the table T_C3PO.'value' at the index name.
        """

        self._access.eval("T_C3PO.'name' = '" + name + "' ;")
        self._access.eval("T_C3PO T_RES T_STR T_OPT = ICOCO_GET_VALUE T_IMP T_STR T_OPT T_RES T_C3PO ;")
        self._access.eval("return_value = T_C3PO.'value'.'" + name + "' ;")
        return self._access.getFloat("return_value")

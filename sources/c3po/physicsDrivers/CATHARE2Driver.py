# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class CATHARE2Driver. """
from __future__ import print_function, division

import c3po.medcouplingCompat as mc
try:
    #import Cathare2
    #import Cathare2.Problem_Cathare as C2
    from Cathare2 import Problem_Cathare as C2
except ImportError:
    # importation dans Corpus
    from CATHARE2SWIG import CATHARE2 as C2
from c3po.PhysicsDriver import PhysicsDriver


def shortName(name):
    """! INTERNAL """
    return name.split("__")[1] if (name.startswith("reconstruction") or name.startswith("sommewall__")) else name


def buildName(keyword, cname, loc, irad=-1):
    """! INTERNAL """
    newName = "{}@{}@{}".format(keyword, cname, loc)
    if int(irad) > 0:
        newName += "@{}".format(irad)
    return newName


class CATHARE2Driver(C2, PhysicsDriver):
    """! This is the implementation of PhysicsDriver for CATHARE2. """

    def __init__(self):
        C2.__init__(self)
        PhysicsDriver.__init__(self)
        self.io = 0
        self._timeShift = 0.
        self._stationaryMode = False
        self._dt = -1

    def getMEDCouplingMajorVersion(self):
        return mc.MEDCouplingVersionMajMinRel()[0]

    def isMEDCoupling64Bits(self):
        return mc.MEDCouplingSizeOfIDs() == 64

    def solveTimeStep(self):
        return C2.solveTimeStep(self)

    def computeTimeStep(self):
        dt, stop = C2.computeTimeStep(self)
        return dt, stop

    def initTimeStep(self, dt):
        self._dt = dt
        return C2.initTimeStep(self, dt)

    def validateTimeStep(self):
        C2.validateTimeStep(self)
        self.post()

    def setStationaryMode(self, stationaryMode):
        self._stationaryMode = stationaryMode

    def getStationaryMode(self):
        return self._stationaryMode

    def abortTimeStep(self):
        return C2.abortTimeStep(self)

    def initialize(self):
        return C2.initialize(self)

    def terminate(self):
        C2.terminate(self)

    def presentTime(self):
        return C2.presentTime(self) - self._timeShift

    def resetTime(self, time_):
        self._timeShift = C2.presentTime(self) - time_

    def getOutputMEDFieldDriver(self, name):
        """! INTERNAL """
        return C2.getOutputMEDField(self, name)

    def getOutputMEDDoubleField(self, name):
        return self.getOutputMEDFieldDriver(name)

    def setInputMEDDoubleField(self, name, field):
        return C2.setInputMEDField(self, name, field)

    def getInputMEDDoubleFieldTemplate(self, name):
        field = self.getOutputMEDDoubleField(name)
        field *= 0.0
        return field

    def getOutputDoubleValue(self, name):
        return C2.getValue(name)

    def setInputDoubleValue(self, name, value):
        return C2.setValue(name, value)

    def post(self):
        """! INTERNAL """
        # ecriture des maillages et entete fichier colonne
        if self.io == 0:
            for name in self.post_names["fields"]:
                field = self.getOutputMEDDoubleField(name)
                mc.WriteUMesh("{}.med".format(shortName(name)), field.getMesh(), True)

            with open("suivi_c2.txt", "w") as fic:
                headerNames = ["Time"] + self.post_names["fields"] + self.post_names["scalars"]
                fic.write(" ".join(["{:>12}".format(shortName(p).split("@")[0]) for p in headerNames]) + "\n")

        temps = self.presentTime()
        with open("suivi_c2.txt", "a") as fic:
            fic.write("{:12.5f} ".format(temps))
            for name in self.post_names["fields"]:
                field = self.getOutputMEDDoubleField(name)
                fic.write("{:12.5g} ".format(field.normMax()[0]))
                field.setTime(temps, self.io, 0)
                mc.WriteFieldUsingAlreadyWrittenMesh("{}.med".format(shortName(name)), field)
            for name in self.post_names["scalars"]:
                if name.startswith("sommewall__"):
                    _, keyword, listofobjects = name.split("__")
                    scalar = 0.0
                    for cname in listofobjects.split("//"):
                        elemName = self.getCValue("ELEMNAME@" + cname)
                        ihpoi = float(self.getIValue("IHPOI@" + elemName))
                        scalar += self.getValue("{}@{}".format(keyword, cname)) * ihpoi
                    fic.write("{:12.5g} ".format(scalar))
                else:
                    fic.write("{:12.5g} ".format(self.getValue(name)))
            fic.write("\n")
        self.io += 1

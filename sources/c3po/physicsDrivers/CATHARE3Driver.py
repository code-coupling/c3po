# -*- coding: utf-8 -*-

# Copyright (c) 2020, CEA
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Contain the class CATHARE3Driver. """
from __future__ import print_function, division

import c3po.medcouplingCompat as mc
try:
    #import Cathare_opt
    import Cathare_opt.Problem_Cathare as C3
except ImportError:
    # importation dans Corpus
    from CATHARE3SWIG import CATHARE3 as C3
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


class CATHARE3Driver(C3, PhysicsDriver):
    """! This is the implementation of PhysicsDriver for CATHARE3. """

    def __init__(self):
        C3.__init__(self)
        PhysicsDriver.__init__(self)
        self.io = 0
        self._timeShift = 0.
        self._stationaryMode = False

    def getICOCOVersion(self):
        return '2.0'

    def getMEDCouplingMajorVersion(self):
        return mc.MEDCouplingVersionMajMinRel()[0]

    def isMEDCoupling64Bits(self):
        return mc.MEDCouplingSizeOfIDs() == 64

    def solveTimeStep(self):
        return C3.solveTimeStep(self)

    def computeTimeStep(self):
        return C3.computeTimeStep(self)

    def initTimeStep(self, dt):
        return C3.initTimeStep(self, dt)

    def validateTimeStep(self):
        C3.validateTimeStep(self)
        self.post()

    def setStationaryMode(self, stationaryMode):
        self._stationaryMode = stationaryMode

    def getStationaryMode(self):
        return self._stationaryMode

    def abortTimeStep(self):
        return C3.abortTimeStep(self)

    def initialize(self):
        return C3.initialize(self)

    def terminate(self):
        C3.terminate(self)

    def presentTime(self):
        return C3.presentTime(self) - self._timeShift

    def resetTime(self, time_):
        self._timeShift = C3.presentTime(self) - time_

    def getOutputMEDFieldDriver(self, name):
        """! INTERNAL """
        separator = "@"
        if name.find(separator) == -1:
            separator = "_"
        if name.split(separator)[0] == "ROWLAND":
            return self.getRowland(*(name.split(separator)[1:]))
        if name.split(separator)[0] == "WEIGHTEDVOL":
            return self.getWeightedVolume(*(name.split(separator)[1:]))
        return C3.getOutputMEDField(self, name)

    def getRowland(self, cname, loc):
        """! INTERNAL """
        fieldC = self.getOutputMEDDoubleField(buildName("UO2CTEMP", cname, loc))
        fieldS = self.getOutputMEDDoubleField(buildName("UO2STEMP", cname, loc))
        fieldC *= 4. / 9.
        fieldS *= 5. / 9.
        fieldC.getArray().addEqual(fieldS.getArray())
        return fieldC

    def getWeightedVolume(self, cname, loc, irad=-1):
        """! INTERNAL """
        field = self.getOutputMEDDoubleField(buildName("VOLMED", cname, loc, irad))
        field *= float(self.getIValue("IWPOI@{}".format(cname)))
        return field

    def getOutputMEDDoubleField(self, name):
        if name.startswith("reconstruction"):
            reco, keyword, listofobjects = name.split("__")
            _, loc, irad = reco.split(":")
            fields = []
            for cname in listofobjects.split("//"):
                newName = buildName(keyword, cname, loc, irad)
                if hasattr(self, "get_field_on_3D_mesh"):
                    func = getattr(self, "get_field_on_3D_mesh")
                    fields.append(func(newName))
                else:
                    fields.append(self.getOutputMEDFieldDriver(newName))
            field = mc.MEDCouplingFieldDouble.MergeFields(fields)
            field.setName(keyword)
            return field
        return self.getOutputMEDFieldDriver(name)

    def setInputMEDDoubleField(self, name, field):

        if name.startswith("reconstruction"):
            reco, keyword, listofobjects = name.split("__")
            _, loc, irad = reco.split(":")

            if hasattr(self, "set_field_from_3D_mesh"):
                func = getattr(self, "set_field_from_3D_mesh")
                func(keyword, listofobjects.split("//"), loc, irad, field)
            else:
                count = 0
                for cname in listofobjects.split("//"):
                    newName = buildName(keyword, cname, loc, irad)
                    f1d = self.getInputMEDDoubleFieldTemplate(newName)
                    nbCells = f1d.getMesh().getNumberOfCells()

                    localArray = mc.DataArrayDouble.New(nbCells)
                    localArray.fillWithZero()
                    localArray += field.getArray()[count: count + nbCells]
                    count += nbCells

                    f1d.setArray(localArray)
                    C3.setInputMEDField(self, newName, f1d)
        else:
            C3.setInputMEDField(self, name, field)

    def getInputMEDDoubleFieldTemplate(self, name):
        field = self.getOutputMEDDoubleField(name)
        field *= 0.0
        return field

    def post(self):
        """! INTERNAL """
        # ecriture des maillages et entete fichier colonne
        if self.io == 0:
            for name in self.post_names["fields"]:
                field = self.getOutputMEDDoubleField(name)
                mc.WriteUMesh("{}.med".format(shortName(name)), field.getMesh(), True)

            with open("suivi_c3.txt", "w") as fic:
                headerNames = ["Time"] + self.post_names["fields"] + self.post_names["scalars"]
                fic.write(" ".join(["{:>12}".format(shortName(p).split("@")[0]) for p in headerNames]) + "\n")

        temps = self.presentTime()
        with open("suivi_c3.txt", "a") as fic:
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

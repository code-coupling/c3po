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

import c3po.medcoupling_compat as mc
try:
    import Cathare_opt
    import Cathare_opt.Problem_Cathare as C3
except ImportError:
    # importation dans Corpus
    from CATHARE3SWIG import CATHARE3 as C3
from c3po.PhysicsDriver import PhysicsDriver


def short_name(name): return name.split("__")[1] if (name.startswith("reconstruction") or name.startswith("sommewall__")) else name


def build_name(keyword, cname, loc, irad=-1):
    new_name = "{}@{}@{}".format(keyword, cname, loc)
    if int(irad) > 0:
        new_name += "@{}".format(irad)
    return new_name


class CATHARE3Driver(C3, PhysicsDriver):
    """! This is the implementation of PhysicsDriver for CATHARE3. """

    def __init__(self):
        C3.__init__(self)
        PhysicsDriver.__init__(self)
        self.io = 0

    def solveTimeStep(self):
        return C3.solveTimeStep(self)

    def computeTimeStep(self):
        return C3.computeTimeStep(self)

    def initTimeStep(self, dt):
        return C3.initTimeStep(self, dt)

    def validateTimeStep(self):
        C3.validateTimeStep(self)
        self.post()

    def abortTimeStep(self):
        return C3.abortTimeStep(self)

    def initialize(self):
        return C3.initialize(self)

    def terminate(self):
        C3.terminate(self)

    def getOutputMEDField_driver(self, name):
        separator = "@"
        if name.find(separator) == -1:
            separator = "_"
        if name.split(separator)[0] == "ROWLAND":
            return self.get_rowland(*(name.split(separator)[1:]))
        elif name.split(separator)[0] == "WEIGHTEDVOL":
            return self.get_weighted_volume(*(name.split(separator)[1:]))
        else:
            return C3.getOutputMEDField(self, name)

    def get_rowland(self, cname, loc):
        fc = self.getOutputMEDField(build_name("UO2CTEMP", cname, loc))
        fs = self.getOutputMEDField(build_name("UO2STEMP", cname, loc))

        fc *= 4. / 9.
        fs *= 5. / 9.
        fc.getArray().addEqual(fs.getArray())
        return fc

    def get_weighted_volume(self, cname, loc, irad=-1):

        f = self.getOutputMEDField(build_name("VOLMED", cname, loc, irad))
        f *= float(self.getIValue("IWPOI@{}".format(cname)))

        return f

    def getOutputMEDField(self, name):
        if name.startswith("reconstruction"):
            reco, keyword, listofobjects = name.split("__")
            _, loc, irad = reco.split(":")
            fields = []
            for cname in listofobjects.split("//"):
                new_name = build_name(keyword, cname, loc, irad)
                if hasattr(self, "get_field_on_3D_mesh"):
                    func = getattr(self, "get_field_on_3D_mesh")
                    fields.append(func(new_name))
                else:
                    fields.append(self.getOutputMEDField_driver(new_name))
            field = mc.MEDCouplingFieldDouble.MergeFields(fields)
            field.setName(keyword)
            return field
        else:
            return self.getOutputMEDField_driver(name)

    def setInputMEDField(self, name, field):

        if name.startswith("reconstruction"):
            reco, keyword, listofobjects = name.split("__")
            _, loc, irad = reco.split(":")

            if hasattr(self, "set_field_from_3D_mesh"):
                func = getattr(self, "set_field_from_3D_mesh")
                func(keyword, listofobjects.split("//"), loc, irad, field)
            else:
                o = 0
                for cname in listofobjects.split("//"):
                    new_name = build_name(keyword, cname, loc, irad)
                    f1d = self.getInputMEDFieldTemplate(new_name)
                    nc = f1d.getMesh().getNumberOfCells()

                    local_array = mc.DataArrayDouble.New(nc)
                    local_array.fillWithZero()
                    local_array += field.getArray()[o: o + nc]
                    o += nc

                    f1d.setArray(local_array)
                    C3.setInputMEDField(self, new_name, f1d)
        else:
            C3.setInputMEDField(self, name, field)

    def getInputMEDFieldTemplate(self, name):
        ch = self.getOutputMEDField(name)
        ch *= 0.0
        return ch

    def post(self):
        # ecriture des maillages et entete fichier colonne
        if self.io == 0:
            for name in self.post_names["fields"]:
                field = self.getOutputMEDField(name)
                mc.WriteUMesh("{}.med".format(short_name(name)), field.getMesh(), True)

            with open("suivi_c3.txt", "w") as f:
                header_names = ["Time"] + self.post_names["fields"] + self.post_names["scalars"]
                f.write(" ".join(["{:>12}".format(short_name(p).split("@")[0]) for p in header_names]) + "\n")

        t = self.presentTime()
        with open("suivi_c3.txt", "a") as fic:
            fic.write("{:12.5f} ".format(t))
            for name in self.post_names["fields"]:
                f = self.getOutputMEDField(name)
                fic.write("{:12.5g} ".format(f.normMax()[0]))
                f.setTime(t, self.io, 0)
                mc.WriteFieldUsingAlreadyWrittenMesh("{}.med".format(short_name(name)), f)
            for name in self.post_names["scalars"]:
                if name.startswith("sommewall__"):
                    _, keyword, listofobjects = name.split("__")
                    s = 0.0
                    for cname in listofobjects.split("//"):
                        elem_name = self.getCValue("ELEMNAME@" + cname)
                        ihpoi = float(self.getIValue("IHPOI@" + elem_name))
                        s += self.getValue("{}@{}".format(keyword, cname)) * ihpoi
                    fic.write("{:12.5g} ".format(s))
                else:
                    fic.write("{:12.5g} ".format(self.getValue(name)))
            fic.write("\n")
        self.io += 1

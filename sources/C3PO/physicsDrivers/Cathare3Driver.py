# -*- coding: utf-8 -*-
from __future__ import print_function, division

import MEDLoader as ml
import Cathare_opt as C3
from C3PO.physicsDriver import physicsDriver


short_name = lambda name: name.split("__")[1] if (name.startswith("reconstruction") or name.startswith("sommewall__")) else name


def build_name(keyword, cname, loc, irad=-1):
    new_name = "{}@{}@{}".format(keyword, cname, loc)
    if int(irad) > 0:
        new_name += "@{}".format(irad)
    return new_name


class PBC(C3.Problem_Cathare, physicsDriver):
    def __init__(self):
        C3.Problem_Cathare.__init__(self)
        physicsDriver.__init__(self)
        self.io = 0

    def solveTimeStep(self):
        return C3.Problem_Cathare.solveTimeStep(self)

    def computeTimeStep(self):
        return C3.Problem_Cathare.computeTimeStep(self)

    def initTimeStep(self, dt):
        return C3.Problem_Cathare.initTimeStep(self, dt)

    def validateTimeStep(self):
        C3.Problem_Cathare.validateTimeStep(self)
        self.post()

    def abortTimeStep(self):
        return C3.Problem_Cathare.abortTimeStep(self)

    def initialize(self):
        return C3.Problem_Cathare.initialize(self)

    def terminate(self):
        C3.Problem_Cathare.terminate(self)

    def getOutputMEDField_driver(self, name):
        separator = "@"
        if name.find(separator) == -1:
            separator = "_"
        if name.split(separator)[0] == "ROWLAND":
            return self.get_rowland(*(name.split(separator)[1:]))
        else: return C3.Problem_Cathare.getOutputMEDField(self, name)

    def get_rowland(self, cname, loc):
        fc = self.getOutputMEDField(build_name("UO2CTEMP", cname, loc))
        fs = self.getOutputMEDField(build_name("UO2STEMP", cname, loc))

        fc *= 4. / 9.
        fs *= 5. / 9.
        fc.getArray().addEqual(fs.getArray())
        return fc

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
            field = ml.MEDCouplingFieldDouble.MergeFields(fields)
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

                    local_array = ml.DataArrayDouble.New(nc)
                    local_array.fillWithZero()
                    local_array += field.getArray()[o : o + nc]
                    o += nc

                    f1d.setArray(local_array)
                    C3.Problem_Cathare.setInputMEDField(self, new_name, f1d)
        else:
            C3.Problem_Cathare.setInputMEDField(self, name, field)

    def getInputMEDFieldTemplate(self, name):
        ch = self.getOutputMEDField(name)
        ch *= 0.0
        return ch

    def compute_fuel_volume(self, list_of_wa):

        fields = []
        for cname in list_of_wa.split("//"):
            field = self.getOutputMEDField("reconstruction:CELLS:0__VOLMED__{}".format(cname))
            iwpoi = float(self.getIValue("IWPOI@{}".format(cname)))
            field *= iwpoi
            fields.append(field)

        field = ml.MEDCouplingFieldDouble.MergeFields(fields)
        field.setName("fuel_volume")
        ml.MEDLoader.WriteField("volume_uo2.med", field, True)

        return field

    def post(self):
        # ecriture des maillages et entete fichier colonne
        if self.io == 0:
            for name in self.post_names["fields"]:
                field = self.getOutputMEDField(name)
                ml.MEDLoader.WriteUMesh("{}.med".format(short_name(name)), field.getMesh(), True)

            with open("suivi_c3.txt", "w") as f:
                header_names = ["Time"] + self.post_names["fields"] + self.post_names["scalars"]
                f.write(" ".join(["{:>12}".format(short_name(p).split("@")[0]) for p in header_names]) + "\n")

        t = self.presentTime()
        with open("suivi_c3.txt", "a") as fic:
            fic.write("{:12.5f} ".format(t))
            for name in self.post_names["fields"]:
                f = self.getOutputMEDField(name)
                fic.write("{:12.5g} ".format(f.normMax()))
                f.setTime(t, self.io, 0)
                ml.MEDLoader.WriteFieldUsingAlreadyWrittenMesh("{}.med".format(short_name(name)), f)
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

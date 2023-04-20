# -*- coding: utf-8 -*-
# Contains some simple functions for MED Mesh building
from __future__ import print_function, division

import c3po.medcouplingCompat as mc


def makeMesh2DCart(x_coord, y_coord):
    arrayX = mc.DataArrayDouble(x_coord)
    arrayX.setInfoOnComponent(0, "X [m]")
    arrayY = mc.DataArrayDouble(y_coord)
    arrayY.setInfoOnComponent(0, "Y [m]")
    cMesh = mc.MEDCouplingCMesh("CartesianMesh")
    cMesh.setCoords(arrayX, arrayY)
    return cMesh.buildUnstructured()


def makeField2DCart(x_coord, y_coord):
    field = mc.MEDCouplingFieldDouble.New(mc.ON_CELLS)
    field.setMesh(makeMesh2DCart(x_coord, y_coord))
    nbMeshes = (len(x_coord) - 1) * (len(y_coord) - 1)
    values = [1.] * nbMeshes
    array = mc.DataArrayDouble.New()
    array.setValues(values, len(values), 1)
    field.setArray(array)
    field.setName("cartesianField")
    field.setNature(mc.IntensiveMaximum)
    return field

# -*- coding: utf-8 -*-
# Contains some simple functions for MED Mesh building
from __future__ import print_function, division
from math import *

import c3po.medcouplingCompat as mc
import tests.medBuilder as medBuilder


def makeMesh3DHexa(meshID = -1):
    length = 5.
    coordzbas = 0.
    coordzhaut = 10.
    entreplat = 2. * length * cos(pi / 6.)
    hexa = []
    if meshID == 0 or meshID == -1:
        hexa.append(medBuilder.makeOne3DHexa(-0.5 * entreplat, 0, length, coordzbas, coordzhaut))
    if meshID == 1 or meshID == -1:
        hexa.append(medBuilder.makeOne3DHexa(+0.5 * entreplat, 0, length, coordzbas, coordzhaut))
    meshHexa = mc.MEDCouplingUMesh.MergeUMeshes(hexa)
    meshHexa.setName("3DMeshHexa")
    return meshHexa


def makeField3DHexa(meshID = -1):
    nbMeshes = 2 if meshID < 0 else 1
    f = mc.MEDCouplingFieldDouble.New(mc.ON_CELLS)
    f.setMesh(makeMesh3DHexa(meshID))
    v = [0.] * nbMeshes
    array = mc.DataArrayDouble.New()
    array.setValues(v, len(v), 1)
    f.setArray(array)
    f.setName("3DFieldHexa")
    f.setNature(mc.IntensiveMaximum)
    return f


def makeMesh3DSquare(meshID = -1):
    length = 5.
    coordzbas = 0.
    coordzhaut = 10.
    decalage = 1.
    carres = []
    if meshID == 0 or meshID == -1:
        carres.append(medBuilder.makeOne3DSquare(-0.5 * length + decalage, 0, length, coordzbas, coordzhaut))
    if meshID == 1 or meshID == -1:
        carres.append(medBuilder.makeOne3DSquare(+0.5 * length + decalage, 0, length, coordzbas, coordzhaut))
    meshCarre = mc.MEDCouplingUMesh.MergeUMeshes(carres)
    meshCarre.setName("3DMeshSquare")
    return meshCarre


def makeField3DSquare(meshID = -1):
    nbMeshes = 2 if meshID < 0 else 1
    f = mc.MEDCouplingFieldDouble.New(mc.ON_CELLS)
    f.setMesh(makeMesh3DSquare(meshID))
    v = [0.] * nbMeshes
    array = mc.DataArrayDouble.New()
    array.setValues(v, len(v), 1)
    f.setArray(array)
    f.setName("3DFieldSquare")
    f.setNature(mc.ExtensiveMaximum)
    return f

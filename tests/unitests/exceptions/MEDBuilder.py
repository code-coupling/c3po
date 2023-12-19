# -*- coding: utf-8 -*-
# Contains some simple functions for MED Mesh building
from __future__ import print_function, division

import c3po.medcouplingCompat as mc


def makeMesh2DCart(x_coord, y_coord):
    arrayX = mc.DataArrayDouble(x_coord)
    arrayX.setInfoOnComponent(0, "X [m]")
    arrayY = mc.DataArrayDouble(y_coord)
    arrayY.setInfoOnComponent(0, "Y [m]")
    cMesh = mc.MEDCouplingCMesh("2DMesh")
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
    field.setName("2DField")
    field.setNature(mc.ExtensiveMaximum)
    return field


def makeMesh3DCart(sizeX, sizeY, sizeZ, nMeshX, nMeshY, nMeshZ):
    coord = 0.
    coordsX = []
    for i in range(nMeshX + 1):
        coordsX.append(coord)
        coord += sizeX / nMeshX
    coord = 0.
    coordsY = []
    for i in range(nMeshY + 1):
        coordsY.append(coord)
        coord += sizeY / nMeshY
    coord = 0.
    coordsZ = []
    for i in range(nMeshZ + 1):
        coordsZ.append(coord)
        coord += sizeZ / nMeshZ
    arrayX = mc.DataArrayDouble(coordsX)
    arrayX.setInfoOnComponent(0, "X [m]")
    arrayY = mc.DataArrayDouble(coordsY)
    arrayY.setInfoOnComponent(0, "Y [m]")
    arrayZ = mc.DataArrayDouble(coordsZ)
    arrayZ.setInfoOnComponent(0, "Z [m]")
    mesh = mc.MEDCouplingCMesh("3DMesh")
    mesh.setCoords(arrayX, arrayY, arrayZ)
    return mesh.buildUnstructured()


def makeField3DCart(sizeX, sizeY, sizeZ, nMeshX, nMeshY, nMeshZ):
    f = mc.MEDCouplingFieldDouble.New(mc.ON_CELLS)
    f.setMesh(makeMesh3DCart(sizeX, sizeY, sizeZ, nMeshX, nMeshY, nMeshZ))
    array = mc.DataArrayDouble.New()
    array.alloc(f.getMesh().getNumberOfCells())
    array.fillWithValue(0.)
    f.setArray(array)
    f.setName("3DField")
    f.setNature(mc.ExtensiveMaximum)
    return f

# -*- coding: utf-8 -*-
# Contains some simple functions for MED Mesh building
from __future__ import print_function, division
from math import *

import c3po.medcouplingCompat as mc


def makeMeshCarre(sizeX, sizeY, sizeZ, nMeshX, nMeshY, nMeshZ):
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


def makeFieldCarre(sizeX, sizeY, sizeZ, nMeshX, nMeshY, nMeshZ):
    f = mc.MEDCouplingFieldDouble.New(mc.ON_CELLS)
    f.setMesh(makeMeshCarre(sizeX, sizeY, sizeZ, nMeshX, nMeshY, nMeshZ))
    array = mc.DataArrayDouble.New()
    array.alloc(f.getMesh().getNumberOfCells())
    array.fillWithValue(0.)
    f.setArray(array)
    f.setName("P")
    f.setNature(mc.ExtensiveMaximum)
    return f


def makeMesh1D(length, nMesh):
    coordzbas = 0.
    coord = coordzbas
    coords = []
    for i in range(nMesh + 1):
        coords.append(coord)
        coord += length / nMesh
    array = mc.DataArrayDouble(coords)
    array.setInfoOnComponent(0, "X [m]")
    mesh = mc.MEDCouplingCMesh("1DMesh")
    mesh.setCoords(array)
    return mesh


def makeField1D(length, nMesh):
    f = mc.MEDCouplingFieldDouble.New(mc.ON_CELLS)
    f.setMesh(makeMesh1D(length, nMesh))
    array = mc.DataArrayDouble.New()
    array.alloc(f.getMesh().getNumberOfCells())
    array.fillWithValue(0.)
    f.setArray(array)
    f.setName("T")
    f.setNature(mc.IntensiveMaximum)
    return f

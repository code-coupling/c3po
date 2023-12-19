# -*- coding: utf-8 -*-
# Contains some simple functions for MED Mesh building
from __future__ import print_function, division
from math import *

import c3po.medcouplingCompat as mc


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
    f.setName("1DField")
    f.setNature(mc.IntensiveMaximum)
    return f


def makeOne3DPrism(x0, y0, coordzbas, coordzhaut):
    nbpoints = len(x0)

    data = mc.DataArrayDouble.New()
    data.alloc(nbpoints, 3)

    group = mc.DataArrayInt.New()
    group.alloc(1, nbpoints + 1)
    group.setIJ(0, 0, mc.NORM_POLYGON)

    for isommet in range(nbpoints):
        data.setIJ(isommet, 0, x0[isommet])
        data.setIJ(isommet, 1, y0[isommet])
        data.setIJ(isommet, 2, coordzbas)
        group.setIJ(0, isommet + 1, isommet)

    inds = mc.DataArrayInt.New()
    inds.alloc(2, 1)
    inds.setIJ(0, 0, 0)
    inds.setIJ(1, 0, nbpoints + 1)

    Hexa = mc.MEDCouplingUMesh.New()
    Hexa.setMeshDimension(2)
    Hexa.setCoords(data)
    Hexa.setConnectivity(group, inds)

    data_z = mc.DataArrayDouble.New()
    data_z.alloc(2, 3)
    data_z.setIJ(0, 0, x0[0])
    data_z.setIJ(0, 1, y0[0])
    data_z.setIJ(0, 2, coordzbas)

    data_z.setIJ(1, 0, x0[0])
    data_z.setIJ(1, 1, y0[0])
    data_z.setIJ(1, 2, coordzhaut)

    mesh1d = mc.MEDCouplingUMesh.New()
    mesh1d.setMeshDimension(1)
    mesh1d.setCoords(data_z)

    mesh1d.allocateCells(1)

    inds_z = [0, 1]
    mesh1d.insertNextCell(mc.NORM_SEG2, 2, inds_z)
    mesh1d.finishInsertingCells()

    mesh3d = Hexa.buildExtrudedMesh(mesh1d, 0)

    return mesh3d


def makeOne3DHexa(x0, y0, length2, coordzbas, coordzhaut):
    coordx = []
    coordy = []

    for isommet in range(6):
        coordx.append(x0 + length2 * cos(radians(30 * (2 * isommet) + 30)))
        coordy.append(y0 + length2 * sin(radians(30 * (2 * isommet) + 30)))

    return makeOne3DPrism(coordx, coordy, coordzbas, coordzhaut)


def makeOne3DSquare(x0, y0, length, coordzbas, coordzhaut):
    coordx = []
    coordy = []

    coordx.append(x0 + length / 2.)
    coordx.append(x0 + length / 2.)
    coordx.append(x0 - length / 2.)
    coordx.append(x0 - length / 2.)

    coordy.append(y0 - length / 2.)
    coordy.append(y0 + length / 2.)
    coordy.append(y0 + length / 2.)
    coordy.append(y0 - length / 2.)

    return makeOne3DPrism(coordx, coordy, coordzbas, coordzhaut)

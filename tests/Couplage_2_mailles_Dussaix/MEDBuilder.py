# -*- coding: utf-8 -*-
# Contains some simple functions for MED Mesh building
from __future__ import print_function, division
from math import *

import MEDCoupling


def makePrismeQuelconqueMED(x0, y0, coordzbas, coordzhaut):
    nbpoints = len(x0)

    data = MEDCoupling.DataArrayDouble.New()
    data.alloc(nbpoints, 3)

    group = MEDCoupling.DataArrayInt.New()
    group.alloc(1, nbpoints + 1)
    group.setIJ(0, 0, MEDCoupling.NORM_POLYGON)

    for isommet in range(nbpoints):
        data.setIJ(isommet, 0, x0[isommet])
        data.setIJ(isommet, 1, y0[isommet])
        data.setIJ(isommet, 2, coordzbas)
        group.setIJ(0, isommet + 1, isommet)

    inds = MEDCoupling.DataArrayInt.New()
    inds.alloc(2, 1)
    inds.setIJ(0, 0, 0)
    inds.setIJ(1, 0, nbpoints + 1)

    Hexa = MEDCoupling.MEDCouplingUMesh.New()
    Hexa.setMeshDimension(2)
    Hexa.setCoords(data)
    Hexa.setConnectivity(group, inds)

    data_z = MEDCoupling.DataArrayDouble.New()
    data_z.alloc(2, 3)
    data_z.setIJ(0, 0, x0[0])
    data_z.setIJ(0, 1, y0[0])
    data_z.setIJ(0, 2, coordzbas)

    data_z.setIJ(1, 0, x0[0])
    data_z.setIJ(1, 1, y0[0])
    data_z.setIJ(1, 2, coordzhaut)

    mesh1d = MEDCoupling.MEDCouplingUMesh.New()
    mesh1d.setMeshDimension(1)
    mesh1d.setCoords(data_z)

    mesh1d.allocateCells(1)

    inds_z = [0, 1]
    mesh1d.insertNextCell(MEDCoupling.NORM_SEG2, 2, inds_z)
    mesh1d.finishInsertingCells()

    mesh3d = Hexa.buildExtrudedMesh(mesh1d, 0)

    return mesh3d


def makePrismeHexaMED(x0, y0, length2, coordzbas, coordzhaut):
    coordx = []
    coordy = []

    for isommet in range(6):
        coordx.append(x0 + length2 * cos(radians(30 * (2 * isommet) + 30)))
        coordy.append(y0 + length2 * sin(radians(30 * (2 * isommet) + 30)))

    return makePrismeQuelconqueMED(coordx, coordy, coordzbas, coordzhaut)


def makeMeshHexa():
    length = 5.
    coordzbas = 0.
    coordzhaut = 10.
    entreplat = 2. * length * cos(pi / 6.)
    hexa = []
    hexa.append(makePrismeHexaMED(-0.5 * entreplat, 0, length, coordzbas, coordzhaut))
    hexa.append(makePrismeHexaMED(+0.5 * entreplat, 0, length, coordzbas, coordzhaut))
    meshHexa = MEDCoupling.MEDCouplingUMesh.MergeUMeshes(hexa)
    meshHexa.setName("MeshHexa")
    return meshHexa


def makeFieldHexa():
    f = MEDCoupling.MEDCouplingFieldDouble.New(MEDCoupling.ON_CELLS)
    f.setMesh(makeMeshHexa())
    v = [0., 0.]
    array = MEDCoupling.DataArrayDouble.New()
    array.setValues(v, len(v), 1)
    f.setArray(array)
    f.setName("Rho")
    f.setNature(MEDCoupling.ConservativeVolumic)
    return f


def makePrismeCarreMED(x0, y0, length, coordzbas, coordzhaut):
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

    return makePrismeQuelconqueMED(coordx, coordy, coordzbas, coordzhaut)


def makeMeshCarre():
    length = 5.
    coordzbas = 0.
    coordzhaut = 10.
    decalage = 1.
    carres = []
    carres.append(makePrismeCarreMED(-0.5 * length + decalage, 0, length, coordzbas, coordzhaut))
    carres.append(makePrismeCarreMED(+0.5 * length + decalage, 0, length, coordzbas, coordzhaut))
    meshCarre = MEDCoupling.MEDCouplingUMesh.MergeUMeshes(carres)
    meshCarre.setName("MeshCarre")
    return meshCarre


def makeFieldCarre():
    f = MEDCoupling.MEDCouplingFieldDouble.New(MEDCoupling.ON_CELLS)
    f.setMesh(makeMeshCarre())
    v = [0., 0.]
    array = MEDCoupling.DataArrayDouble.New()
    array.setValues(v, len(v), 1)
    f.setArray(array)
    f.setName("T")
    f.setNature(MEDCoupling.Integral)
    return f
